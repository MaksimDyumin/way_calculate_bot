```json
{
    "day_progress": {
        "yesterday": "Number", // Путь пройденный за сегодня 
        "today": "Number"  // Путь пройденный за вчера
        // Относительно дня get запроса
    },

    "week_travel": {
       "data": "number[]", // Километры пройденные в каждый день недели example: [12, 10, 6 ...]
       "start_week_data": "date/str",
       "end_week_data": "date/str",
    },

    "mounth_travel": {
       "data": "number[]", // Километры пройденные в каждый день месяца
       "start_mounth_data": "date/str",
       "end_mounth_data": "date/str",
    },

    "year_travel": {
       "data": "number[]", // Километры пройденные в каждый месяц года
       "start_mounth_data": "date/str",
       "end_mounth_data": "date/str",
    },

    "average_max_speed": {
       "today": {
            "average": "number[]",
            "max": "number[]"
        },
        "week": {
            "average": "number[]",
            "max": "number[]"
        },
        "mouth": {
            "average": "number[]",
            "max": "number[]"
        },
        "year": {
            "average": "number[]",
            "max": "number[]"
        },
        "all_time": {
            "average": "number[]",
            "max": "number[]"
        },
    },
}


```