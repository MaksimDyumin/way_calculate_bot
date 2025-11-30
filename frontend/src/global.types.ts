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
        average: number[],
        max: number[]
    },
    week: {
        average: number[],
        max: number[]
    },
    mouth: {
        average: number[],
        max: number[]
    },
    year: {
        average: number[],
        max: number[]
    },
    alltime: {
        average: number[],
        max: number[]
    },
}

export type IntervalTravel = {
    data: Array<number>
    total: number
}

export type WeekTravel = IntervalTravel & {
    end_week_data: string
    start_week_data:string
}

export type MounthTravel = IntervalTravel & {
    end_mounth_data: string
    start_mounth_data: string
}

export type YearTravel = IntervalTravel & {
    end_year_data: string
    start_year_data: string
}

export type YearsTravel = IntervalTravel & {
    data: Array<number>
    years: Array<number>
    total: number
}

export type IntervalTravelTypes = WeekTravel | MounthTravel | YearTravel | YearsTravel;