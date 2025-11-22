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
import { Line, Bar } from 'vue-chartjs';
import { generateWeekBarConfig } from '@/utilFunctions/generateConfigs';
import { useWayTravelStore } from '@/stores/wayTravel';
import { computed, onMounted, ref, watch } from 'vue';

const wayTraveledStore = useWayTravelStore();
const reloadData = ref(false)

const {wayTraveled, title, data} = defineProps<{ wayTraveled: Array<number> | null, title: string, data: string }>();
let chartData: any = null;
let options: any = null;
onMounted(() => {
  const data = generateWeekBarConfig(wayTraveled, title, wayTraveledStore.theme);
  chartData = data?.chartData;
  options = data?.options;
  reloadData.value = true
});


const themeChanges = watch(
  () => wayTraveledStore.theme,
  (newTheme) => {
    reloadData.value = false;
    const updatedConfig = generateWeekBarConfig(wayTraveled, title, newTheme);
    chartData = updatedConfig?.chartData;
    options = updatedConfig?.options;
    
    setTimeout(() => {
      reloadData.value = true;
    }, 10);
  }
);
const dataChanges = watch(
  () => wayTraveledStore.travelData,
  (newTheme) => {
    reloadData.value = false;
    const updatedConfig = generateWeekBarConfig(wayTraveled, title, newTheme);
    chartData = updatedConfig?.chartData;
    options = updatedConfig?.options;
    
    setTimeout(() => {
      reloadData.value = true;
    }, 10);
  }
);

</script>

<template>
    <div class="chart-wrapper">
      <div class="title-container"><span class="title">{{ title }}</span> {{ data }}</div> <!-- TODO:  -->
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

.title{
  font-size: 20px;
  font-weight: bold;
  color: var(--text);
}

.title-container{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
  color: gray;
}
</style>