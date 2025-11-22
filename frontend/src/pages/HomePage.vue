<script setup lang="ts">
import DayProgressBar from '@/components/DayProgressBar.vue';
import WayChart from '@/components/WayChart.vue';
import { ref, onMounted } from 'vue';
import type { Ref } from 'vue';
import type { Interval } from '@/pages/pages.types.ts';

const weekTravel: number[] = [4, 6, 7, 3, 10, 12, 8];
const mounthTravel: number[] = [4, 6, 7, 3, 10, 12, 8, 4, 6, 7, 3, 10, 12, 8, 4, 6, 7, 3, 10, 12, 8, 4, 6, 7, 3, 10, 12, 8];
const yearTravel: number[] = [4, 6, 7, 3, 10, 12, 4, 6, 7, 3, 10, 12];

const intervals: Interval[] = ['Сегодня', 'Неделя', 'Месяц', 'Год', 'Все время'];
const speedInterval: Ref<Interval> = ref('Сегодня');
const isSwitch: Ref<boolean> = ref(true);

const speedData: Record<Interval, { average: number; max: number }> = {
  Сегодня: { average: 20, max: 25 },
  Неделя: { average: 18, max: 27 },
  Месяц: { average: 22, max: 30 },
  Год: { average: 19, max: 28 },
  'Все время': { average: 115, max: 443 },
};

// --- Функция смены интервала
async function setInterval(interval: Interval) {
  isSwitch.value = false;
  speedInterval.value = interval;
  await new Promise((res) => setTimeout(res, 100));
  isSwitch.value = true;
}

// --- Определение темы
</script>

<template>
  <div class="home-container">
    <day-progress-bar :yesterday="9" :today="12" />

    <div class="interval-toggle">
      <button
        v-for="interval in intervals"
        :key="interval"
        :class="{ active: speedInterval === interval }"
        @click="setInterval(interval)"
      >
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

    <WayChart :wayTraveled="weekTravel" title="Неделя" data="17.11.2025 - 23.11.2025" />
    <WayChart :wayTraveled="mounthTravel" title="Месяц" data="Ноябрь 2025" />
    <WayChart :wayTraveled="yearTravel" title="Год" data="2025" />
  </div>
</template>

<style lang="scss" scoped>
/* ------------------ АНИМАЦИЯ ------------------ */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.4s, transform 0.4s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
.fade-enter-to, .fade-leave-from {
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
.speed-info {
  width: 100%;
  max-width: 600px;
  background: var(--card-bg);
  border-radius: 16px;
  box-shadow: var(--card-shadow);
  padding: 8px;
  font-family: 'Montserrat', sans-serif;
  color: var(--text);
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
</style>
