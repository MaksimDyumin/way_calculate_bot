from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS
from datetime import datetime, date, timedelta
import math

from constants import (
    BIKE_RADIUS_M,
    SCOOTER_RADIUS_M,
    BUS_RADIUS_M,
    BIKE_SPEED_MIN_KMH,
    BIKE_SPEED_MAX_KMH,
    BIKE_PRIORITY_LOCATIONS,
    SCOOTER_A,
    SCOOTER_B,
    SCOOTER_PARKING,
    BUS_STOPS,
)

DB_PATH = "travel.db"


app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "http://localhost:5173"}})

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS segments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                start_date TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                distance_m REAL NOT NULL,
                duration_s REAL NOT NULL,
                speed_kmh REAL NOT NULL,
                UNIQUE(start_time, end_time, activity_type, distance_m)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def parse_iso(ts_str):
    # Разбирает ISO-строку, например "2024-11-20T11:24:00.449+01:00"
    return datetime.fromisoformat(ts_str)


def parse_geo(geo_str):
    """
    'geo:47.552953,9.697704' -> (lat, lon)
    """
    if not isinstance(geo_str, str):
        return None, None
    if not geo_str.startswith("geo:"):
        return None, None
    try:
        lat_str, lon_str = geo_str[4:].split(",", 1)
        return float(lat_str), float(lon_str)
    except Exception:
        return None, None


def haversine_m(lat1, lon1, lat2, lon2):
    """
    Расстояние между двумя точками (lat, lon) в метрах.
    """
    if None in (lat1, lon1, lat2, lon2):
        return None
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(
        dlambda / 2
    ) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def is_near(lat, lon, target_lat, target_lon, radius_m):
    dist = haversine_m(lat, lon, target_lat, target_lon)
    return dist is not None and dist <= radius_m


def is_near_any(lat, lon, locations, radius_m):
    for loc in locations:
        if is_near(lat, lon, loc["lat"], loc["lon"], radius_m):
            return True
    return False


def is_scooter_segment(start_lat, start_lon, end_lat, end_lon):
    """
    2 группа правил (электросамокат).
    """
    a_lat, a_lon = SCOOTER_A["lat"], SCOOTER_A["lon"]
    b_lat, b_lon = SCOOTER_B["lat"], SCOOTER_B["lon"]
    p_lat, p_lon = SCOOTER_PARKING["lat"], SCOOTER_PARKING["lon"]

    # A -> B
    if is_near(start_lat, start_lon, a_lat, a_lon, SCOOTER_RADIUS_M) and \
       is_near(end_lat, end_lon, b_lat, b_lon, SCOOTER_RADIUS_M):
        return True

    # B -> A
    if is_near(start_lat, start_lon, b_lat, b_lon, SCOOTER_RADIUS_M) and \
       is_near(end_lat, end_lon, a_lat, a_lon, SCOOTER_RADIUS_M):
        return True

    # парковка -> A/B
    if is_near(start_lat, start_lon, p_lat, p_lon, SCOOTER_RADIUS_M) and (
        is_near(end_lat, end_lon, a_lat, a_lon, SCOOTER_RADIUS_M)
        or is_near(end_lat, end_lon, b_lat, b_lon, SCOOTER_RADIUS_M)
    ):
        return True

    # A/B -> парковка
    if is_near(end_lat, end_lon, p_lat, p_lon, SCOOTER_RADIUS_M) and (
        is_near(start_lat, start_lon, a_lat, a_lon, SCOOTER_RADIUS_M)
        or is_near(start_lat, start_lon, b_lat, b_lon, SCOOTER_RADIUS_M)
    ):
        return True

    # парковка -> парковка
    if is_near(start_lat, start_lon, p_lat, p_lon, SCOOTER_RADIUS_M) and \
       is_near(end_lat, end_lon, p_lat, p_lon, SCOOTER_RADIUS_M):
        return True

    return False


def is_bus_segment(start_lat, start_lon, end_lat, end_lon):
    """
    1 группа правил (автобус).
    """
    if not BUS_STOPS:
        return False

    start_near = is_near_any(start_lat, start_lon, BUS_STOPS, BUS_RADIUS_M)
    end_near = is_near_any(end_lat, end_lon, BUS_STOPS, BUS_RADIUS_M)
    return start_near and end_near


def classify_activity(raw_type, speed_kmh, start_lat, start_lon, end_lat, end_lon):
    """
    Применяем правила:
      - самокат
      - автобус
      - велосипед (в приоритетных точках + по скорости)
      - иначе как есть.
    """
    if start_lat is None or start_lon is None or end_lat is None or end_lon is None:
        return raw_type or "unknown"

    if is_scooter_segment(start_lat, start_lon, end_lat, end_lon):
        return "e-scooter"

    if is_bus_segment(start_lat, start_lon, end_lat, end_lon):
        return "in bus"

    if BIKE_SPEED_MIN_KMH <= speed_kmh <= BIKE_SPEED_MAX_KMH:
        if is_near_any(start_lat, start_lon, BIKE_PRIORITY_LOCATIONS, BIKE_RADIUS_M) or \
           is_near_any(end_lat, end_lon, BIKE_PRIORITY_LOCATIONS, BIKE_RADIUS_M):
            return "cycling"

    return raw_type or "unknown"


def event_to_row(ev):
    """
    Один объект из location-history.json -> строка для БД.
    """
    if "activity" not in ev:
        return None

    act = ev["activity"]

    if "distanceMeters" not in act:
        return None

    try:
        dist_m = float(act["distanceMeters"])
    except (TypeError, ValueError):
        return None

    try:
        start_dt = parse_iso(ev["startTime"])
        end_dt = parse_iso(ev["endTime"])
    except Exception:
        return None

    duration_s = (end_dt - start_dt).total_seconds()
    if duration_s <= 0:
        return None

    speed_kmh = (dist_m / 1000.0) / (duration_s / 3600.0)

    start_geo = ev["activity"].get("start")
    end_geo = ev["activity"].get("end")
    start_lat, start_lon = parse_geo(start_geo)
    end_lat, end_lon = parse_geo(end_geo)

    raw_type = act.get("topCandidate", {}).get("type")

    activity_type = classify_activity(
        raw_type=raw_type,
        speed_kmh=speed_kmh,
        start_lat=start_lat,
        start_lon=start_lon,
        end_lat=end_lat,
        end_lon=end_lon,
    )

    start_date = start_dt.date().isoformat()

    return (
        ev["startTime"],
        ev["endTime"],
        start_date,
        activity_type,
        dist_m,
        duration_s,
        speed_kmh,
    )


# ---------- Агрегации с учётом валидных скоростей ----------

def aggregate_by_date(rows):
    """
    date -> {
      dist_m_total  — вся дистанция,
      dist_m_speed  — дистанция только по валидным скоростям,
      dur_s_speed   — длительность только по валидным,
      max_speed     — макс скорость по валидным
    }
    """
    result = {}
    for r in rows:
        d = datetime.fromisoformat(r["start_date"]).date()
        dist_m = float(r["distance_m"])
        dur_s = float(r["duration_s"])
        speed = float(r["speed_kmh"])

        info = result.get(d)
        if info is None:
            info = {
                "dist_m_total": 0.0,
                "dist_m_speed": 0.0,
                "dur_s_speed": 0.0,
                "max_speed": 0.0,
            }
            result[d] = info

        # Дистанция для километража — всегда
        info["dist_m_total"] += dist_m

        # Скорости — только если в диапазоне велосипеда
        if BIKE_SPEED_MIN_KMH <= speed <= BIKE_SPEED_MAX_KMH:
            info["dist_m_speed"] += dist_m
            info["dur_s_speed"] += dur_s
            if speed > info["max_speed"]:
                info["max_speed"] = speed

    return result


def aggregate_by_month(rows):
    """
    (year, month) -> агрегаты как выше.
    """
    result = {}
    for r in rows:
        d = datetime.fromisoformat(r["start_date"]).date()
        key = (d.year, d.month)
        dist_m = float(r["distance_m"])
        dur_s = float(r["duration_s"])
        speed = float(r["speed_kmh"])

        info = result.get(key)
        if info is None:
            info = {
                "dist_m_total": 0.0,
                "dist_m_speed": 0.0,
                "dur_s_speed": 0.0,
                "max_speed": 0.0,
            }
            result[key] = info

        info["dist_m_total"] += dist_m

        if BIKE_SPEED_MIN_KMH <= speed <= BIKE_SPEED_MAX_KMH:
            info["dist_m_speed"] += dist_m
            info["dur_s_speed"] += dur_s
            if speed > info["max_speed"]:
                info["max_speed"] = speed

    return result


def aggregate_by_year(rows):
    """
    year -> агрегаты как выше.
    """
    result = {}
    for r in rows:
        d = datetime.fromisoformat(r["start_date"]).date()
        year = d.year
        dist_m = float(r["distance_m"])
        dur_s = float(r["duration_s"])
        speed = float(r["speed_kmh"])

        info = result.get(year)
        if info is None:
            info = {
                "dist_m_total": 0.0,
                "dist_m_speed": 0.0,
                "dur_s_speed": 0.0,
                "max_speed": 0.0,
            }
            result[year] = info

        info["dist_m_total"] += dist_m

        if BIKE_SPEED_MIN_KMH <= speed <= BIKE_SPEED_MAX_KMH:
            info["dist_m_speed"] += dist_m
            info["dur_s_speed"] += dur_s
            if speed > info["max_speed"]:
                info["max_speed"] = speed

    return result


# ---------- API: импорт ----------

@app.route("/import", methods=["POST"])
def import_location_history():
    """
    Принимает JSON как location-history.json
    и складывает сегменты в SQLite.
    """
    data = request.get_json(force=True, silent=True)
    if data is None:
        return jsonify({"error": "Expected JSON body"}), 400

    if isinstance(data, dict):
        if "events" in data:
            data = data["events"]
        elif "timelineObjects" in data:
            data = data["timelineObjects"]
        else:
            return jsonify({"error": "Expected JSON array or known wrapper"}), 400

    if not isinstance(data, list):
        return jsonify({"error": "Expected JSON array"}), 400

    conn = get_db()
    cur = conn.cursor()

    imported = 0
    skipped = 0

    for ev in data:
        row = event_to_row(ev)
        if row is None:
            continue
        cur.execute(
            """
            INSERT OR IGNORE INTO segments
            (start_time, end_time, start_date, activity_type,
             distance_m, duration_s, speed_kmh)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            row,
        )
        if cur.rowcount == 0:
            skipped += 1
        else:
            imported += 1

    conn.commit()
    conn.close()

    return jsonify(
        {
            "imported": imported,
            "skipped_duplicates": skipped,
        }
    )


# ---------- API: статистика ----------

@app.route("/stats", methods=["GET"])
def get_stats():
    """
    Возвращает статистику по велосипеду (activity_type='cycling').
    """
    date_param = request.args.get("date")
    if date_param:
        try:
            base_date = datetime.fromisoformat(date_param).date()
        except Exception:
            return jsonify({"error": "date must be in format YYYY-MM-DD"}), 400
    else:
        base_date = date.today()

    yesterday = base_date - timedelta(days=1)

    # Неделя (понедельник–воскресенье)
    week_start = base_date - timedelta(days=base_date.weekday())
    week_end = week_start + timedelta(days=6)

    # Месяц
    month_start = base_date.replace(day=1)
    if base_date.month == 12:
        next_month_start = base_date.replace(year=base_date.year + 1, month=1, day=1)
    else:
        next_month_start = base_date.replace(month=base_date.month + 1, day=1)
    month_end = next_month_start - timedelta(days=1)

    # Год
    year_start = date(base_date.year, 1, 1)
    year_end = date(base_date.year, 12, 31)

    conn = get_db()
    cur = conn.cursor()

    # Берём минимум для day/week, чтобы неделя покрывалась полностью
    query_start = min(yesterday, week_start)

    # Для day_progress / week
    cur.execute(
        """
        SELECT start_date, distance_m, duration_s, speed_kmh
        FROM segments
        WHERE start_date BETWEEN ? AND ?
          AND activity_type = 'cycling'
        """,
        (query_start.isoformat(), week_end.isoformat()),
    )
    day_rows = cur.fetchall()
    by_date = aggregate_by_date(day_rows)

    # Для mounth_travel и average_max_speed.mouth
    cur.execute(
        """
        SELECT start_date, distance_m, duration_s, speed_kmh
        FROM segments
        WHERE start_date BETWEEN ? AND ?
          AND activity_type = 'cycling'
        """,
        (month_start.isoformat(), month_end.isoformat()),
    )
    month_rows = cur.fetchall()
    by_date_for_month = aggregate_by_date(month_rows)

    # Для year_travel и average_max_speed.year
    cur.execute(
        """
        SELECT start_date, distance_m, duration_s, speed_kmh
        FROM segments
        WHERE start_date BETWEEN ? AND ?
          AND activity_type = 'cycling'
        """,
        (year_start.isoformat(), year_end.isoformat()),
    )
    year_rows = cur.fetchall()
    by_month_for_year = aggregate_by_month(year_rows)

    # Для years / alltime
    cur.execute(
        """
        SELECT start_date, distance_m, duration_s, speed_kmh
        FROM segments
        WHERE activity_type = 'cycling'
        """
    )
    all_rows = cur.fetchall()
    by_year_all = aggregate_by_year(all_rows)

    conn.close()

    # ---------- day_progress ----------
    def km_for(d):
        info = by_date.get(d)
        if not info:
            return 0.0
        return round(info["dist_m_total"] / 1000.0, 2)

    day_progress = {
        "yesterday": km_for(yesterday),
        "today": km_for(base_date),
    }

    # ---------- week_travel ----------
    week_days = [week_start + timedelta(days=i) for i in range(7)]
    week_data = [
        round(by_date.get(d, {"dist_m_total": 0})["dist_m_total"] / 1000.0, 2)
        for d in week_days
    ]
    week_travel = {
        "data": week_data,
        "start_week_data": week_start.isoformat(),
        "end_week_data": week_end.isoformat(),
    }

    # ---------- mounth_travel ----------
    days_in_month = (month_end - month_start).days + 1
    month_days = [month_start + timedelta(days=i) for i in range(days_in_month)]
    month_data = [
        round(by_date_for_month.get(d, {"dist_m_total": 0})["dist_m_total"] / 1000.0, 2)
        for d in month_days
    ]
    mounth_travel = {
        "data": month_data,
        "start_mounth_data": month_start.isoformat(),
        "end_mounth_data": month_end.isoformat(),
    }

    # ---------- year_travel ----------
    year_month_data = []
    for m in range(1, 13):
        info = by_month_for_year.get((base_date.year, m))
        if not info:
            year_month_data.append(0.0)
        else:
            year_month_data.append(round(info["dist_m_total"] / 1000.0, 2))

    year_travel = {
        "data": year_month_data,
        "start_year_data": year_start.isoformat(),
        "end_year_data": year_end.isoformat(),
    }

    # ---------- массивы скоростей для графиков ----------

    def avg_max_arrays_for_days(dates_list, agg_dict):
        avg_list = []
        max_list = []
        for d in dates_list:
            info = agg_dict.get(d)
            if not info or info["dur_s_speed"] <= 0:
                avg_list.append(0.0)
                max_list.append(0.0)
            else:
                dist_km = info["dist_m_speed"] / 1000.0
                hours = info["dur_s_speed"] / 3600.0
                if hours <= 0:
                    avg_list.append(0.0)
                    max_list.append(0.0)
                else:
                    avg_speed = dist_km / hours
                    avg_list.append(round(avg_speed, 2))
                    max_list.append(round(info["max_speed"], 2))
        return avg_list, max_list

    # today — сразу как скаляр
    today_info = by_date.get(base_date)
    if today_info and today_info["dur_s_speed"] > 0:
        dist_km = today_info["dist_m_speed"] / 1000.0
        hours = today_info["dur_s_speed"] / 3600.0
        if hours > 0:
            today_avg_val = round(dist_km / hours, 2)
            today_max_val = round(today_info["max_speed"], 2)
        else:
            today_avg_val = 0.0
            today_max_val = 0.0
    else:
        today_avg_val = 0.0
        today_max_val = 0.0

    # week / month / year — массивы значений для графиков
    week_avg_values, week_max_values = avg_max_arrays_for_days(week_days, by_date)
    mouth_avg_values, mouth_max_values = avg_max_arrays_for_days(
        month_days, by_date_for_month
    )

    max_month = base_date.month
    year_avg_values = []
    year_max_values = []
    for m in range(1, max_month + 1):
        info = by_month_for_year.get((base_date.year, m))
        if not info or info["dur_s_speed"] <= 0:
            year_avg_values.append(0.0)
            year_max_values.append(0.0)
            continue

        dist_km = info["dist_m_speed"] / 1000.0
        hours = info["dur_s_speed"] / 3600.0
        if hours <= 0:
            year_avg_values.append(0.0)
            year_max_values.append(0.0)
            continue

        avg_speed = dist_km / hours
        year_avg_values.append(round(avg_speed, 2))
        year_max_values.append(round(info["max_speed"], 2))

    # По годам
    all_years_sorted = sorted(by_year_all.keys())
    years_labels = all_years_sorted
    years_avg_values = []
    years_max_values = []
    for y in years_labels:
        info = by_year_all[y]
        if info["dur_s_speed"] <= 0:
            years_avg_values.append(0.0)
            years_max_values.append(0.0)
            continue

        dist_km = info["dist_m_speed"] / 1000.0
        hours = info["dur_s_speed"] / 3600.0
        if hours <= 0:
            years_avg_values.append(0.0)
            years_max_values.append(0.0)
            continue

        avg_speed = dist_km / hours
        years_avg_values.append(round(avg_speed, 2))
        years_max_values.append(round(info["max_speed"], 2))

    # ---------- агрегированные средние по периодам (одиночные значения) ----------

    # week
    week_total_dist_m = 0.0
    week_dist_m_speed = 0.0
    week_dur_s_speed = 0.0
    week_max_speed_val = 0.0
    for d in week_days:
        info = by_date.get(d)
        if not info:
            continue
        week_total_dist_m += info["dist_m_total"]
        week_dist_m_speed += info["dist_m_speed"]
        week_dur_s_speed += info["dur_s_speed"]
        if info["max_speed"] > week_max_speed_val:
            week_max_speed_val = info["max_speed"]

    if week_dur_s_speed > 0:
        week_avg_speed_val = (week_dist_m_speed / 1000.0) / (week_dur_s_speed / 3600.0)
    else:
        week_avg_speed_val = 0.0
        week_max_speed_val = 0.0

    # month
    month_total_dist_m = 0.0
    month_dist_m_speed = 0.0
    month_dur_s_speed = 0.0
    month_max_speed_val = 0.0
    for d in month_days:
        info = by_date_for_month.get(d)
        if not info:
            continue
        month_total_dist_m += info["dist_m_total"]
        month_dist_m_speed += info["dist_m_speed"]
        month_dur_s_speed += info["dur_s_speed"]
        if info["max_speed"] > month_max_speed_val:
            month_max_speed_val = info["max_speed"]

    if month_dur_s_speed > 0:
        month_avg_speed_val = (month_dist_m_speed / 1000.0) / (
            month_dur_s_speed / 3600.0
        )
    else:
        month_avg_speed_val = 0.0
        month_max_speed_val = 0.0

    # year (текущий)
    year_total_dist_m = 0.0
    year_dist_m_speed = 0.0
    year_dur_s_speed = 0.0
    year_max_speed_val = 0.0
    for m in range(1, max_month + 1):
        info = by_month_for_year.get((base_date.year, m))
        if not info:
            continue
        year_total_dist_m += info["dist_m_total"]
        year_dist_m_speed += info["dist_m_speed"]
        year_dur_s_speed += info["dur_s_speed"]
        if info["max_speed"] > year_max_speed_val:
            year_max_speed_val = info["max_speed"]

    if year_dur_s_speed > 0:
        year_avg_speed_val = (year_dist_m_speed / 1000.0) / (
            year_dur_s_speed / 3600.0
        )
    else:
        year_avg_speed_val = 0.0
        year_max_speed_val = 0.0

    # alltime
    alltime_total_dist_m = 0.0
    alltime_dist_m_speed = 0.0
    alltime_dur_s_speed = 0.0
    alltime_max_speed_val = 0.0
    for info in by_year_all.values():
        alltime_total_dist_m += info["dist_m_total"]
        alltime_dist_m_speed += info["dist_m_speed"]
        alltime_dur_s_speed += info["dur_s_speed"]
        if info["max_speed"] > alltime_max_speed_val:
            alltime_max_speed_val = info["max_speed"]

    if alltime_dur_s_speed > 0:
        alltime_avg_speed_val = (alltime_dist_m_speed / 1000.0) / (
            alltime_dur_s_speed / 3600.0
        )
    else:
        alltime_avg_speed_val = 0.0
        alltime_max_speed_val = 0.0

    # ---------- summary по периодам ----------
    summary_today = {
        "distance_km": round(
            by_date.get(base_date, {"dist_m_total": 0})["dist_m_total"] / 1000.0, 2
        )
        if base_date in by_date
        else 0.0,
        "average_speed": round(today_avg_val, 2),
        "max_speed": round(today_max_val, 2),
    }

    summary_week = {
        "distance_km": round(week_total_dist_m / 1000.0, 2),
        "average_speed": round(week_avg_speed_val, 2),
        "max_speed": round(week_max_speed_val, 2),
    }

    summary_month = {
        "distance_km": round(month_total_dist_m / 1000.0, 2),
        "average_speed": round(month_avg_speed_val, 2),
        "max_speed": round(month_max_speed_val, 2),
    }

    summary_year = {
        "distance_km": round(year_total_dist_m / 1000.0, 2),
        "average_speed": round(year_avg_speed_val, 2),
        "max_speed": round(year_max_speed_val, 2),
    }

    summary_alltime = {
        "distance_km": round(alltime_total_dist_m / 1000.0, 2),
        "average_speed": round(alltime_avg_speed_val, 2),
        "max_speed": round(alltime_max_speed_val, 2),
    }

    # ---------- average_max_speed (новый формат) ----------

    average_max_speed = {
        "today": {
            "average": summary_today["average_speed"],   # double
            "max": summary_today["max_speed"],           # double
        },
        "week": {
            "average": summary_week["average_speed"],
            "max": summary_week["max_speed"],
            "average_values": week_avg_values,           # массив по дням недели
            "max_values": week_max_values,
        },
        "mouth": {
            "average": summary_month["average_speed"],
            "max": summary_month["max_speed"],
            "average_values": mouth_avg_values,          # массив по дням месяца
            "max_values": mouth_max_values,
        },
        "year": {
            "average": summary_year["average_speed"],
            "max": summary_year["max_speed"],
            "average_values": year_avg_values,           # массив по месяцам
            "max_values": year_max_values,
        },
        "years": {
            "years": years_labels,                       # список годов
            "average_values": years_avg_values,          # по годам
            "max_values": years_max_values,
        },
        "alltime": {
            "average": summary_alltime["average_speed"],
            "max": summary_alltime["max_speed"],
        },
    }

    # ---------- суммы километров за период ----------

    week_travel_total = round(sum(week_data), 2)
    mounth_travel_total = round(sum(month_data), 2)
    year_travel_total = round(sum(year_month_data), 2)

    week_travel["total"] = week_travel_total
    mounth_travel["total"] = mounth_travel_total
    year_travel["total"] = year_travel_total

    # ---------- years_travel (км по годам + суммарно) ----------

    years_travel_years = years_labels
    years_travel_data = [
        round(by_year_all[y]["dist_m_total"] / 1000.0, 2) for y in years_travel_years
    ]
    years_travel_total = round(sum(years_travel_data), 2)

    years_travel = {
        "years": years_travel_years,
        "data": years_travel_data,
        "total": years_travel_total,
    }

    # ---------- summary в одном месте ----------
    summary = {
        "today": summary_today,
        "week": summary_week,
        "month": summary_month,
        "year": summary_year,
        "alltime": summary_alltime,
    }

    response = {
        "day_progress": day_progress,
        "week_travel": week_travel,
        "mounth_travel": mounth_travel,
        "year_travel": year_travel,
        "years_travel": years_travel,
        "average_max_speed": average_max_speed,
        "summary": summary,
    }

    return jsonify(response)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
