<template>
  <div class="distance-bar">
    <!-- Заголовок -->
    <div class="header">
      <div class="today">{{ today }} км</div>
      <div class="diff" :class="diffClass">
        на {{ Math.abs(diff) }} км {{ diff > 0 ? "больше" : diff < 0 ? "меньше" : "" }} чем вчера
      </div>
    </div>

    <!-- Полоска -->
    <div class="bar">
      <div class="bar-yesterday" :style="{ width: todayPercent + '%' }"></div>
      <div
        v-if="diff !== 0"
        class="bar-diff"
        :class="diff > 0 ? 'more' : 'less'"
        :style="{ width: Math.abs(diffPercent) + '%' }"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  yesterday: { type: Number, required: true },
  today: { type: Number, required: true }
});

const diff = computed(() => props.today - props.yesterday);
const max = computed(() => Math.max(props.today, props.yesterday));
const todayPercent = computed(() => (props.today / max.value) * 100);
const diffPercent = computed(() => (diff.value / max.value) * 100);

const diffClass = computed(() => {
  if (diff.value > 0) return "positive";
  if (diff.value < 0) return "negative";
  return "";
});
</script>

<style lang="scss" scoped>
.distance-bar {
  width: 100%;
  max-width: 320px;
  font-family: sans-serif;
}

.header {
  text-align: center;
  margin-bottom: 10px;
}

.today {
  font-size: 2rem;
  font-weight: bold;
}

.diff {
  font-size: 1rem;
  margin-top: 4px;
}

.diff.positive {
  color: green; /* зелёный #2a9d8f */
}

.diff.negative {
  color: #d35f5f; /* красный */
}

.bar {
  position: relative;
  height: 20px;
  background: #eee;
  border-radius: 10px;
  overflow: hidden;
  display: flex;
}

.bar-yesterday {
  height: 100%;
  background: #f4c542; /* жёлтый */
}

.bar-diff.more {
  height: 100%;
  background: #4caf50; /* зелёный */
  position: absolute;
  right: 0;
}

.bar-diff.less {
  height: 100%;
  background: #d9534f; /* красный */
  position: absolute;
  right: 0;
}
</style>
