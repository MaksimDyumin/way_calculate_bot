<script setup lang="ts">
import {
  Chart as ChartJS,
  LineElement,
  BarElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
} from 'chart.js';

ChartJS.register(
  LineElement,
  BarElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
);

import { Bar } from 'vue-chartjs';
import { generateWeekBarConfig } from '@/utilFunctions/generateConfigs';
import { useWayTravelStore } from '@/stores/wayTravel';
import { computed, onMounted, ref, watch } from 'vue';
import { format, parseISO } from 'date-fns';
import { ru } from 'date-fns/locale';
import type { IntervalTravel, WeekTravel, MounthTravel, YearTravel, YearsTravel } from '@/global.types';

const wayTraveledStore = useWayTravelStore();

const { wayTraveled, title } = defineProps<{
  wayTraveled: WeekTravel | MounthTravel | YearTravel | YearsTravel | null,
  title: string,
}>();

let chartData: any = null;
let options: any = null;

const reloadData = ref(false);

// ----------------------
// 📌 Форматирование дат
// ----------------------
const formattedDate = computed(() => {
  if (!wayTraveled) return '';

  // Неделя
  if ('start_week_data' in wayTraveled && wayTraveled.start_week_data) {
    const start = format(parseISO(wayTraveled.start_week_data), 'dd.MM.yyyy', { locale: ru });
    const end = format(parseISO(wayTraveled.end_week_data), 'dd.MM.yyyy', { locale: ru });
    return `${start} — ${end}`;
  }

  const daysCount = wayTraveled.data.length;

  if ('start_mounth_data' in wayTraveled && title === 'Месяц') {
    const month = format(parseISO(wayTraveled.start_mounth_data ?? new Date().toISOString()), 'LLLL yyyy', { locale: ru });
    return month.charAt(0).toUpperCase() + month.slice(1); // первая буква заглавная
  }

  // Год → обычно 365–366 значений
  if ('start_year_data' in wayTraveled && title === 'Год') {
    const year = format(parseISO(wayTraveled.start_year_data ?? new Date().toISOString()), 'yyyy');
    return `${year} год`;
  }

  if ('years' in wayTraveled && title === 'Года') {
    const years = wayTraveled.years
    return `${years[0]} - ${years[years.length - 1]}`;
  }

  // Месяц → 28–31 значение
  

  return '1';
});

// ----------------------
// 📌 Инициализация графика
// ----------------------
onMounted(() => {
  if (!wayTraveled) return;
  const cfg = generateWeekBarConfig(wayTraveled, title, wayTraveledStore.theme);
  chartData = cfg?.chartData;
  options = cfg?.options;
  reloadData.value = true;
});

// ----------------------
// 📌 Переключение темы
// ----------------------
watch(() => wayTraveledStore.theme, (newTheme) => {
  if (!wayTraveled) return;
  reloadData.value = false;

  const cfg = generateWeekBarConfig(wayTraveled, title, newTheme);
  chartData = cfg?.chartData;
  options = cfg?.options;

  setTimeout(() => reloadData.value = true, 10);
});

// ----------------------
// 📌 Обновление данных
// ----------------------
watch(() => wayTraveledStore.travelData, () => {
  if (!wayTraveled) return;
  reloadData.value = false;

  const cfg = generateWeekBarConfig(wayTraveled, title, wayTraveledStore.theme);
  chartData = cfg?.chartData;
  options = cfg?.options;

  setTimeout(() => reloadData.value = true, 10);
});
</script>

<template>
  <div class="chart-wrapper">
    <div class="title-container">
      <span class="title">{{ title }}</span>
      <span>{{ formattedDate }}</span>
    </div>
    <Bar v-if="reloadData" :data="chartData" :options="options" />
  </div>
</template>

<style lang="scss" scoped>
.chart-wrapper {
  padding: 5px;
  border-radius: 10px;
  width: 100%;
  height: 300px;
  margin-top: 80px;
  display: flex;
  flex-direction: column;
  background-color: var(--card-bg);
}

.title {
  font-size: 20px;
  font-weight: bold;
  color: var(--text);
}

.title-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
  color: gray;
}
</style>
