<script setup lang="ts">
import { onMounted } from 'vue';
import { useWayTravelStore } from './stores/wayTravel';

import { ThemeEnum } from '@/global.types'


const wayTraveledStore = useWayTravelStore();
onMounted(() => {
  console.log(document.body.getAttribute("data-theme"));
  if (localStorage.getItem('data-theme') === null) {
    localStorage.setItem('data-theme', ThemeEnum.LIGHT);
  }
  const theme = localStorage.getItem('data-theme') === 'light' ? ThemeEnum.LIGHT : ThemeEnum.DARK;
  document.body.setAttribute("data-theme", theme);
  wayTraveledStore.theme = theme;
});
const toggleTheme = () => {
  const current = document.body.getAttribute("data-theme");
  const next = current === "light" ? ThemeEnum.DARK : ThemeEnum.LIGHT;
  localStorage.setItem('data-theme', next);
  document.body.setAttribute("data-theme", next);
  wayTraveledStore.theme = next;
};
</script>

<template>
  <div class="main-container">

    <button class="theme-toggle" @click="toggleTheme">
      <span class="icon sun">☀️</span>
      <span class="icon moon">🌙</span>
    </button>

    <router-view />
  </div>
</template>

<style lang="scss" >
#app {
  width: 100%!important;
  height: 100%!important;
}

.main-container {
  padding: 10px;
  margin-bottom: 100px;
  margin-top: 50px;
  background-color: var(--bg);
}

.theme-toggle {
  position: fixed;
  bottom: 20px;
  right: 20px;

  width: 50px;
  height: 50px;

  border-radius: 50%;
  border: none;

  background: var(--toggle-bg);
  color: var(--toggle-icon);

  display: flex;
  align-items: center;
  justify-content: center;

  font-size: 24px;
  cursor: pointer;

  transition: all 0.3s ease;
  box-shadow: 0 3px 12px rgba(0,0,0,0.15);
  z-index: 9999;
}

/* Hover эффект */
.theme-toggle:hover {
  transform: scale(1.1);
  box-shadow: 0 5px 18px rgba(0,0,0,0.25);
}

/* Иконки внутри */
.theme-toggle .icon {
  position: absolute;
  opacity: 0;
  transform: scale(0.5);
  transition: 0.25s ease;
}

/* Светлая тема — показываем солнце */
[data-theme="light"] .theme-toggle .sun {
  opacity: 1;
  transform: scale(1);
}

/* Тёмная тема — показываем луну */
[data-theme="dark"] .theme-toggle .moon {
  opacity: 1;
  transform: scale(1);
}
</style>
