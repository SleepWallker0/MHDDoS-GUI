/**
 * MHDDoS PRO - Telemetry Charting Logic
 * Handles real-time visualization of network metrics using Chart.js
 */

export class TelemetryChart {
    constructor(canvasId) {
        this.ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!this.ctx) return;

        this.maxPoints = 60; // 1 minute of data at 1s intervals
        this.labels = Array(this.maxPoints).fill('');
        this.ppsData = Array(this.maxPoints).fill(0);
        this.bpsData = Array(this.maxPoints).fill(0);

        this.chart = new Chart(this.ctx, {
            type: 'line',
            data: {
                labels: this.labels,
                datasets: [
                    {
                        label: 'PPS',
                        data: this.ppsData,
                        borderColor: '#06b6d4',
                        backgroundColor: 'rgba(6, 182, 212, 0.1)',
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: true,
                        tension: 0.4,
                        yAxisID: 'y'
                    },
                    {
                        label: 'BPS',
                        data: this.bpsData,
                        borderColor: '#94a3b8',
                        borderWidth: 1,
                        borderDash: [5, 5],
                        pointRadius: 0,
                        tension: 0.4,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        display: false
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#64748b', font: { size: 9 } }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: { drawOnChartArea: false },
                        ticks: { color: '#64748b', font: { size: 9 } }
                    }
                }
            }
        });
    }

    update(agg) {
        if (!this.chart) return;

        this.ppsData.push(agg['current-rps'] || 0);
        this.bpsData.push(agg['current-bps'] || 0);

        if (this.ppsData.length > this.maxPoints) {
            this.ppsData.shift();
            this.bpsData.shift();
        }

        this.chart.update();
    }
}
