export type Theme = 'light' | 'dark'

export enum ThemeEnum {
    LIGHT = 'light',
    DARK = 'dark'
}

export type DayProgress = {
    yesterday: number,
    today: number
}

export type AverageMaxSpeed = {
    today: {
        average: number,
        max: number
    },
    week: {
        average: number,
        max: number
    },
    mouth: {
        average: number,
        max: number
    },
    year: {
        average: number,
        max: number
    },
    all_time: {
        average: number,
        max: number
    },
}