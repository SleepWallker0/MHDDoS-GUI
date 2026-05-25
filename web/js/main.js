import { SocketManager } from './core/socket.js';
import { TerminalUI, setLogLevel } from './ui/terminal.js';
import { showToast } from './ui/toast.js';
import { telemetry } from './core/telemetry.js';
import { TelemetryChart } from './core/telemetry-chart.js';
import { TaskManager } from './ui/tasks.js';
import * as engine from './core/engine.js';
import * as modals from './ui/modals.js';
import * as history from './ui/history.js';
import { uiProMax } from './ui/ui-pro-max.js';
import * as helpers from './utils/helpers.js';

// Initialize UI Components
const terminal = new TerminalUI('terminal-content');
const mainChart = new TelemetryChart('networkVelocityChart');
const tasks = new TaskManager('tasks-container');

// Save terminal reference for global helper functions
window._terminal = terminal;

// Bridge to Global Scope for HTML Event Handlers
window.handleMainAction = engine.handleMainAction;
window.analyzeTarget = engine.analyzeTarget;

window.openToolsModal = modals.openToolsModal;
window.closeToolsModal = modals.closeToolsModal;
window.switchToolTab = modals.switchToolTab;
window.executeTool = modals.executeTool;

window.openSettingsModal = modals.openSettingsModal;
window.closeSettingsModal = modals.closeSettingsModal;
window.saveSettings = modals.saveSettings;

window.openConfigModal = modals.openConfigModal;
window.closeConfigModal = modals.closeConfigModal;
window.addConfigSource = modals.addConfigSource;
window.saveProxyConfig = modals.saveProxyConfig;

window.setLogLevel = setLogLevel;
window.clearTerminal = () => terminal.clear();
window.copyLogs = () => terminal.copy();
window.toggleTerminalScroll = () => {
    const active = terminal.toggleAutoScroll();
    showToast(active ? "Auto-scroll active" : "Auto-scroll paused", "info");
};

window.switchMainView = (view) => {
    history.switchMainView(view);
};
window.refreshHistory = history.refreshHistory;
window.changeHistoryPage = history.changeHistoryPage;
window.showToast = showToast;
window.uiProMax = uiProMax;

window.toggleAdvancedSettings = function() {
    const container = document.getElementById('advanced-settings-container');
    const icon = document.getElementById('advanced-settings-icon');
    if (container.classList.contains('hidden')) {
        container.classList.remove('hidden');
        if(icon) icon.style.transform = 'rotate(180deg)';
    } else {
        container.classList.add('hidden');
        if(icon) icon.style.transform = 'rotate(0deg)';
    }
}

// WebSocket Orchestration
const socket = new SocketManager('/ws/logs', (data) => {
    if (data.type === 'log') {
        terminal.append(data.msg, data.level, data.task_id);
    } else if (data.type === 'telemetry') {
        telemetry.updateTask(data.task_id, data);
        const agg = telemetry.getAggregate();
        
        // Update DOM elements for global metrics
        const elements = {
            'current-rps': (val) => helpers.formatHuman(val),
            'peak-rps': (val) => helpers.formatHuman(val),
            'current-bps': (val) => helpers.formatBytes(val),
            'peak-bps': (val) => helpers.formatBytes(val),
            'active-tasks-count': (val) => val,
            'current-threads': (val) => helpers.formatHuman(val)
        };

        Object.entries(elements).forEach(([id, formatter]) => {
            const el = document.getElementById(id);
            if (el) el.innerText = formatter(agg[id] || 0);
        });

        // Update Charts
        mainChart.update(agg);

        window.dispatchEvent(new CustomEvent('telemetry-update', {
            detail: agg
        }));
    }
});

// Bootstrap
document.addEventListener('DOMContentLoaded', () => {
    socket.connect();
    uiProMax.init();
    tasks.startPolling();
    showToast('MHDDoS PRO Core Linked', 'success');
});
