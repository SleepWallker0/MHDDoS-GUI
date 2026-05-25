import { formatBytes, formatHuman } from '../utils/helpers.js';

export class TelemetryStore {
    constructor() {
        this.taskMetrics = {};
        this.peakRPS = 0;
        this.peakBPS = 0;
    }

    updateTask(taskId, data) {
        if (!taskId) return;
        this.taskMetrics[taskId] = {
            ...this.taskMetrics[taskId],
            ...data,
            lastUpdate: Date.now()
        };
        this.purgeStale();
    }

    purgeStale() {
        const now = Date.now();
        Object.keys(this.taskMetrics).forEach(id => {
            if (now - this.taskMetrics[id].lastUpdate > 10000) delete this.taskMetrics[id];
        });
    }

    getAggregate() {
        const metrics = Object.values(this.taskMetrics);
        const totalRps = metrics.reduce((s, m) => s + (m.rps || 0), 0);
        const totalBps = metrics.reduce((s, m) => s + (m.bps || 0), 0);
        const totalThreads = metrics.reduce((s, m) => s + (m.threads || 0), 0);

        if (totalRps > this.peakRPS) this.peakRPS = totalRps;
        if (totalBps > this.peakBPS) this.peakBPS = totalBps;

        return {
            'current-rps': totalRps,
            'current-bps': totalBps,
            'peak-rps': this.peakRPS,
            'peak-bps': this.peakBPS,
            'active-tasks-count': metrics.length,
            'current-threads': totalThreads
        };
    }
}

export const telemetry = new TelemetryStore();