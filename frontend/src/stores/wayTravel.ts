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
      // console.log(travelData.value)
      // travelData.value = {
      //   day_progress: {
      //     yesterday: 12,
      //     today: 10
      //   },

      //   week_travel: {
      //     data: [4, 6, 7, 3, 10, 12, 8],
      //     start_week_data: "17.11.2025",
      //     end_week_data: "23.11.2025",
      //   },

      //   mounth_travel: {
      //     data: [4, 6, 7, 3, 10, 12, 8, 4, 6, 7, 3, 10, 12, 8, 4, 6, 7, 3, 10, 12, 8, 4, 6, 7, 3, 10, 12, 8],
      //     mounth_name: "Ноябрь",
      //   },

      //   year_travel: {
      //     data: [4, 6, 7, 3, 10, 12, 4, 6, 7, 3, 10, 12],
      //     year: "2025",
      //   },

      //   average_max_speed: {
      //     today: {
      //       average: 12,
      //       max: 45
      //     },
      //     week: {
      //       average: 15,
      //       max: 50
      //     },
      //     mouth: {
      //       average: 14,
      //       max: 48
      //     },
      //     year: {
      //       average: 13,
      //       max: 47
      //     },
      //     all_time: {
      //       average: 16,
      //       max: 55
      //     },
      //   },
      // }
    } catch (error) {
      console.error('Error fetching travel info:', error)
    }
  }

  return { getDateTravelInfo, travelData, theme }

})
