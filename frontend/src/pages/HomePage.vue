<script setup lang="ts">
import DayProgressBar from '@/components/DayProgressBar.vue';
import WayChart from '@/components/WayChart.vue';
import { ref, onMounted, computed, nextTick } from 'vue';
import type { Ref } from 'vue';
import type { Interval } from '@/pages/pages.types.ts';
import { useWayTravelStore } from '@/stores/wayTravel';
import type { AverageMaxSpeed, DayProgress, WeekTravel, MounthTravel, YearTravel, YearsTravel } from '@/global.types';

const isLoading = ref(false);
const wayTraveledStore = useWayTravelStore();

// --- Исправленные названия
const weekTravel = ref<WeekTravel>({} as WeekTravel);
const monthTravel = ref<MounthTravel>({} as MounthTravel);
const yearTravel = ref<YearTravel>({} as YearTravel);
const yearsTravel = ref<YearsTravel>({} as YearsTravel);
const todayProgress = ref<DayProgress>({ yesterday: 0, today: 0 });

// --- Исправлен ключ month вместо mouth
const averageMaxSpeed = ref<AverageMaxSpeed>({
  today: { average: [55], max: [55] },
  week: { average: [55], max: [55] },
  mouth: { average: [55], max: [55] },
  year: { average: [55], max: [55] },
  alltime: { average: [55], max: [55] },
});
const summary = ref<any>({});

// --- чистая функция среднего
const avg = (arr: number[]) =>
  arr?.length ? Number((arr.reduce((p, c) => p + c, 0) / arr.length).toFixed(1)) : 0;

  
// --- улучшена структура расчётов speedData
const speedData = computed(() => {
  const d = averageMaxSpeed.value;
  return {
    Сегодня: {
      average: d.today.average,
      max: d.today.max
    },
    Неделя: {
      average: d.week.average,
      max: d.week.max
    },
    
    Месяц: {
      average: d.mouth.average,
      max: d.mouth.max
    },
    Год: {
      average: d.year.average,
      max: d.year.max
    },
    'Все время': {
      average: d.alltime.average,
      max: d.alltime.max
    }
  };
});

// --- загрузка данных
onMounted(async () => {
  await wayTraveledStore.getDateTravelInfo();
  const data = wayTraveledStore.travelData;

  weekTravel.value = data.week_travel;
  monthTravel.value = data.mounth_travel; 
  yearTravel.value = data.year_travel;
  yearsTravel.value = data.years_travel
  todayProgress.value = data.day_progress;
  summary.value = data.summary;
  averageMaxSpeed.value = data.average_max_speed;

  isLoading.value = true;
});

// --- переключатель интервала
const intervals: Interval[] = ['Сегодня', 'Неделя', 'Месяц', 'Год', 'Все время'];
const speedInterval: Ref<Interval> = ref('Сегодня');
const isSwitch = ref(true);

async function setDateInterval(interval: Interval) {
  isSwitch.value = false;
  speedInterval.value = interval;

  // Вместо setTimeout использован nextTick — вариант более корректный
  await nextTick();

  isSwitch.value = true;
}

const distanceData = computed(() => ({
  Сегодня: summary.value.today?.distance_km ?? 0,
  Неделя: summary.value.week?.distance_km ?? 0,
  Месяц: summary.value.month?.distance_km ?? 0,
  Год: summary.value.year?.distance_km ?? 0,
  'Все время': summary.value.alltime?.distance_km ?? 0
}));
</script>

<template>
  <div v-if="isLoading" class="home-container">
    <day-progress-bar :yesterday="todayProgress.yesterday" :today="todayProgress.today" />

    <div class="interval-toggle">
      <button v-for="interval in intervals" :key="interval" :class="{ active: speedInterval === interval }"
        @click="setDateInterval(interval)">
        {{ interval }}
      </button>
    </div>

    <div class="speed-info">
      <div class="speed-row speed-header">
        <h3>Скорость</h3>
        <h3>Средняя</h3>
        <h3>Максимальная</h3>
      </div>

      <Transition name="fade" mode="out-in">
        <div v-if="isSwitch" class="speed-row speed-body">
          <h3>{{ speedInterval }}</h3>
          <span>{{ speedData[speedInterval].average }} км/ч</span>
          <span>{{ speedData[speedInterval].max }} км/ч</span>
        </div>
      </Transition>
    </div>

    <div class="vert-line"></div>

    <div class="kilometrs-info">
      <div class="speed-row speed-header">
        <h3>Пройдено</h3>
        <h3>Километры</h3>
      </div>

      <Transition name="fade" mode="out-in">
        <div v-if="isSwitch" class="speed-row speed-body">
          <h3>{{ speedInterval }}</h3>
          <span>{{ distanceData[speedInterval] }} км</span>
        </div>
      </Transition>
    </div>

    <!-- даты оставлены как есть (по твоей логике), но без ошибок -->
    <WayChart :wayTraveled="weekTravel" title="Неделя" />
    <WayChart :wayTraveled="monthTravel" title="Месяц" />
    <WayChart :wayTraveled="yearTravel" title="Год" />
    <WayChart :wayTraveled="yearsTravel" title="Года" />
  </div>
</template>

<style lang="scss" scoped>
/* ------------------ АНИМАЦИЯ ------------------ */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s, transform 0.4s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-enter-to,
.fade-leave-from {
  opacity: 1;
  transform: translateY(0);
}

/* ------------------ ОСНОВНОЙ КОНТЕЙНЕР ------------------ */
.home-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: var(--text);
}

/* ------------------ ПЕРЕКЛЮЧАТЕЛЬ ТЕМЫ ------------------ */
.theme-switch {
  margin-top: 20px;
  padding: 8px 12px;
  border-radius: 12px;
  background: var(--btn-bg);
  color: var(--btn-text);
  border: 1px solid var(--btn-border);
  transition: 0.3s;
  cursor: pointer;
}

.theme-switch:hover {
  background: var(--btn-bg-hover);
}

/* ------------------ БЛОК СКОРОСТИ ------------------ */

@mixin info-mixin {
  width: 100%;
  max-width: 600px;
  background: var(--card-bg);
  border-radius: 16px;
  box-shadow: var(--card-shadow);
  padding: 8px;
  font-family: 'Montserrat', sans-serif;
  color: var(--text);
}

.speed-info {
  @include info-mixin;
}

.kilometrs-info {
  @include info-mixin;
}

.speed-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  align-items: center;
  margin-bottom: 16px;
}

.speed-header h3 {
  font-weight: 600;
  font-size: 16px;
  color: var(--text-secondary);
  text-align: center;
}

.speed-body h3 {
  font-weight: 500;
  font-size: 14px;
  color: var(--text-muted);
  text-align: center;
}

.speed-body span {
  font-size: 20px;
  font-weight: 600;
  color: var(--text);
  text-align: center;
}

.speed-row:not(:last-child) {
  border-bottom: 1px solid var(--divider);
  padding-bottom: 12px;
}

/* ------------------ ПЕРЕКЛЮЧАЛКА ИНТЕРВАЛОВ ------------------ */
.interval-toggle {
  margin-top: 40px;
  margin-bottom: 10px;
  display: flex;
  gap: 10px;
}

.interval-toggle button {
  padding: 4px 8px;
  border: 1px solid var(--btn-border);
  background: var(--btn-bg);
  border-radius: 12px;
  cursor: pointer;
  font-family: 'Montserrat', sans-serif;
  font-weight: 500;
  transition: all 0.2s;
  color: var(--text);
}

.interval-toggle button:hover {
  background: var(--btn-bg-hover);
}

.interval-toggle button.active {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}
.vert-line {
  height: 40px;
  width: 3px;
  background: var(--divider);
  margin: 0 10px;
  opacity: 0.7;
}
</style>
