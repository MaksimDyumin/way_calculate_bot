import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

import type { Ref } from 'vue'
import type { Theme } from '@/global.types'

import { ThemeEnum } from '@/global.types'
import { apiClient } from '@/axios/axios'


export const useWayTravelStore = defineStore('wayTravel', () => {
  const theme: Ref<Theme> = ref(ThemeEnum.LIGHT)
  const travelData: any = ref(null)

  async function getDateTravelInfo(): Promise<void> {
    try {
      const response = await apiClient.get('stats')
      travelData.value = response.data
    } catch (error) {
      console.error('Error fetching travel info:', error)
    }
  }

  return { getDateTravelInfo, travelData, theme }

})
