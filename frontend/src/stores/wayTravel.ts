import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import { defineStore } from 'pinia'
import type { Theme } from '@/global.types'

import { ThemeEnum } from '@/global.types'

export const useWayTravelStore = defineStore('wayTravel', () => {
  const count = ref(0)
  const theme: Ref<Theme> = ref(ThemeEnum.LIGHT)
  const doubleCount = computed(() => count.value * 2)
  function increment() {
    count.value++
  }
  // function increment() {
  //   count.value++
  // }
  // function increment() {
  //   count.value++
  // }

  return { count, doubleCount, increment, theme }
})
