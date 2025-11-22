import type { Theme } from "@/global.types";

export function generateWeekConfig(wayTraveled: number[], type?: string) {
    const daysCount = wayTraveled.length;
    const labels = Array.from({ length: daysCount }, (_, i) => `${i + 1}`);

    const pointColors = wayTraveled.map((distance, index) => {
        if (index === 0) return 'gray';
        const prev = wayTraveled[index - 1] ?? 0;
        return distance > prev ? 'green' : 'red';
    });

    const chartData = {
        labels: labels,
        datasets: [
            {
                label: 'Пройдено км',
                data: wayTraveled,
                borderWidth: 2,
                borderColor: '#f4c542',
                backgroundColor: 'rgba(75, 125, 255, 0.1)', // заливка под графиком
                pointBackgroundColor: pointColors,
                pointBorderColor: '#ffff',
                pointRadius: 5,
                fill: true,
                tension: 0.3
            }
        ]
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                ticks: { color: '#333' },
                grid: { color: 'rgba(0,0,0,0.1)' }
            },
            y: {
                ticks: { color: '#333' },
                grid: { color: 'rgba(0,0,0,0.1)' }
            }
        },
        plugins: {
            legend: { labels: { color: '#333' }, display: false }
        }
    };

    return { chartData, options };
}

export function generateWeekBarConfig(wayTraveled: number[], type?: string, theme?: Theme) {
    const daysCount = wayTraveled.length;
    let labels = Array.from({ length: daysCount }, (_, i) => `${i + 1}`);
    if (type === 'Неделя') {
        labels = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
    }
    if (type === 'Год') {
        labels = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'];
    }
    const currentTheme: any = {}
    if (theme === 'light') {
        currentTheme.ticks = { color: '#111111'}
        currentTheme.ticks = { grid: '#111111'}
    } else {
        currentTheme.ticks = { color: '#787878ff'}
        currentTheme.grid = { color: '#7e7e7eff'}
    }

    // Генерируем цвета для каждого бара
    const barColors = wayTraveled.map((distance, index) => {
        if (index === 0) return 'green';
        const prev = wayTraveled[index - 1] ?? 0;
        return distance > prev ? 'green' : 'red';
    });

    const chartData = {
        labels,
        datasets: [
            {
                label: 'Км',
                data: wayTraveled,
                backgroundColor: barColors, // цвет каждого бара
                borderColor: '#f4c542',
                borderWidth: 2
            }
        ]
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                ticks: currentTheme.ticks, //
                grid: currentTheme.grid, //
            },
            y: {
                ticks: currentTheme.ticks,
                grid: currentTheme.grid,
            }
        },
        // plugins: {
        //     legend: { labels: { color: '#333' } }
        // }
    };

    return { chartData, options };
}
