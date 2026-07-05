import { apiRequest } from '../core/api.js';
import { showToast } from './toast.js';
import { escapeHtml } from '../utils/helpers.js';

export class TaskManager {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.interval = null;
    }

    startPolling() {
        this.refresh();
        this.interval = setInterval(() => this.refresh(), 2000);
    }

    stopPolling() {
        if (this.interval) clearInterval(this.interval);
    }

    async refresh() {
        try {
            const data = await apiRequest('/api/attack/status');
            if (data.status === 'success') {
                this.render(data.active_tasks);
                const badge = document.getElementById('active-tasks-count');
                if (badge) badge.innerText = data.active_tasks.length;
            }
        } catch (e) {
            console.error("Task refresh failed", e);
        }
    }

    render(tasks) {
        if (!this.container) return;

        if (!tasks || tasks.length === 0) {
            this.container.innerHTML = `
                <div class="flex flex-col items-center justify-center py-12 opacity-20">
                    <span class="material-symbols-outlined text-4xl mb-2"> cloud_off </span>
                    <p class="text-[10px] font-mono uppercase tracking-widest">No Active Deployments</p>
                </div>
            `;
            return;
        }

        this.container.innerHTML = tasks.map(t => `
            <div class="bg-black/20 border border-outline-variant rounded-lg p-4 flex flex-col gap-3 group hover:border-primary/30 transition-all">
                <div class="flex justify-between items-start">
                    <div class="space-y-1">
                        <div class="text-xs font-bold text-on-surface truncate max-w-[180px]" title="${escapeHtml(t.target)}">${escapeHtml(t.target)}</div>
                        <div class="flex items-center gap-2">
                            <span class="text-[9px] font-black px-1.5 py-0.5 rounded bg-primary/10 text-primary border border-primary/20 uppercase">${escapeHtml(t.method)}</span>
                            <span class="text-[9px] font-mono text-on-surface-variant/60">ID: ${escapeHtml(String(t.task_id || '').substring(0, 8))}</span>
                        </div>
                    </div>
                    <button onclick="stopTask('${escapeHtml(t.task_id || '')}')" class="text-on-surface-variant hover:text-error transition-colors">
                        <span class="material-symbols-outlined text-sm">cancel</span>
                    </button>
                </div>
                <div class="space-y-1">
                    <div class="flex justify-between text-[9px] font-mono text-on-surface-variant">
                        <span>Progress</span>
                        <span>${t.pps?.toLocaleString() || 0} PPS</span>
                    </div>
                    <div class="h-1 w-full bg-outline-variant rounded-full overflow-hidden">
                        <div class="h-full bg-primary animate-pulse" style="width: 100%"></div>
                    </div>
                </div>
            </div>
        `).join('');
    }
}

window.stopTask = async (taskId) => {
    try {
        const data = await apiRequest('/api/attack/stop', { task_id: taskId });
        if (data.status === 'success') {
            showToast("Task termination sequence initiated.", "success");
        }
    } catch (e) {
        showToast("Termination failed.", "error");
    }
};
