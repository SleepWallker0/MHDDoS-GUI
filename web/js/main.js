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

// Save references for global helper access
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
window.switchAssetTab = modals.switchAssetTab;

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

window.scrollToConfig = () => {
    const el = document.getElementById('config-section');
    if (el) {
        el.scrollIntoView({ behavior: 'smooth' });
        el.classList.add('ring-4', 'ring-primary/20', 'rounded-2xl');
        setTimeout(() => el.classList.remove('ring-4', 'ring-primary/20'), 2000);
    }
};

window.refreshHistory = history.refreshHistory;
window.changeHistoryPage = history.changeHistoryPage;
window.showToast = showToast;
window.uiProMax = uiProMax;
window.uploadAssetFile = modals.uploadAssetFile;
window.deleteAssetFile = modals.deleteAssetFile;

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

window.populateFileLists = async function() {
    try {
        const res = await fetch('/api/files/list');
        const data = await res.json();
        if (data.status === 'success') {
            const proxySelect = document.getElementById('proxy_list');
            const reflSelect = document.getElementById('reflector');
            const modalProxyList = document.getElementById('modal-proxy-list');
            const modalReflList = document.getElementById('modal-reflector-list');

            if (proxySelect) {
                proxySelect.innerHTML = '<option value="AUTO">⚡ Auto Harvest (Smart)</option>' +
                    '<option value="">📄 default.txt</option>' +
                    data.proxies.filter(f => f !== 'default.txt').map(f => `<option value="${f}">📄 ${f}</option>`).join('');
            }
            if (reflSelect) {
                reflSelect.innerHTML = '<option value="">None (Standard)</option>' + 
                    '<option value="reflector.txt">📄 reflector.txt</option>' +
                    data.reflectors.filter(f => f !== 'reflector.txt').map(f => `<option value="${f}">📄 ${f}</option>`).join('');
            }
            
            // Populate lists in Asset Manager modal
            if (modalProxyList) {
                modalProxyList.innerHTML = data.proxies.map(f => `
                    <div class="flex justify-between items-center py-1.5 border-b border-white/5 last:border-0 group">
                        <span>${f}</span>
                        ${f !== 'default.txt' ? `<button onclick="deleteAssetFile('proxy', '${f}')" class="text-error opacity-0 group-hover:opacity-100 transition-opacity" title="Delete File"><span class="material-symbols-outlined text-[14px]">delete</span></button>` : ''}
                    </div>`).join('');
            }
            if (modalReflList) {
                modalReflList.innerHTML = data.reflectors.map(f => `
                    <div class="flex justify-between items-center py-1.5 border-b border-white/5 last:border-0 group">
                        <span>${f}</span>
                        ${f !== 'reflector.txt' ? `<button onclick="deleteAssetFile('reflector', '${f}')" class="text-error opacity-0 group-hover:opacity-100 transition-opacity" title="Delete File"><span class="material-symbols-outlined text-[14px]">delete</span></button>` : ''}
                    </div>`).join('');
            }
        }
    } catch (e) { console.error("File list fetch failed", e); }
}

function handleMethodChange() {
    const method = document.getElementById('method').value;
    const reflContainer = document.getElementById('reflector-container');
    
    // List of methods requiring reflector (Amplification)
    const ampMethods = ["MEM", "NTP", "DNS", "ARD", "CLDAP", "CHAR", "RDP"];
    
    if (ampMethods.includes(method)) {
        reflContainer.classList.remove('hidden');
    } else {
        reflContainer.classList.add('hidden');
    }
}

function populateMethods() {
    const methodSelect = document.getElementById('method');
    if (!methodSelect) return;

    const l7 = ["CFB", "BYPASS", "GET", "POST", "OVH", "STRESS", "DYN", "SLOW", "HEAD", "NULL", "COOKIE", "PPS", "EVEN", "GSB", "DGB", "AVB", "CFBUAM", "APACHE", "XMLRPC", "BOT", "BOMB", "DOWNLOADER", "KILLER", "TOR", "RHEX", "STOMP"];
    const l4_amp = ["MEM", "NTP", "DNS", "ARD", "CLDAP", "CHAR", "RDP"];
    const l4_normal = ["TCP", "UDP", "SYN", "VSE", "MINECRAFT", "MCBOT", "CONNECTION", "CPS", "FIVEM", "FIVEM-TOKEN", "TS3", "MCPE", "ICMP", "OVH-UDP"];

    methodSelect.innerHTML = `
        <optgroup label="Layer 7 (Web / Apps)">
            ${l7.map(m => `<option value="${m}" ${m === 'GET' ? 'selected' : ''}>${m}</option>`).join('')}
        </optgroup>
        <optgroup label="Layer 4 (Transport / Network)">
            ${l4_normal.map(m => `<option value="${m}">${m}</option>`).join('')}
        </optgroup>
        <optgroup label="Layer 4 (Amplification)">
            ${l4_amp.map(m => `<option value="${m}">${m}</option>`).join('')}
        </optgroup>
    `;
    
    methodSelect.addEventListener('change', handleMethodChange);
    handleMethodChange(); // Initial check
}

// WebSocket Orchestration
const socket = new SocketManager('/ws/logs', (data) => {
    if (data.type === 'log') {
        terminal.append(data.msg, data.level, data.task_id);
    } else if (data.type === 'telemetry') {
        telemetry.updateTask(data.task_id, data);
        const agg = telemetry.getAggregate();
        
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
    populateMethods();
    populateFileLists();
    showToast('MHDDoS PRO Operational', 'success');
});
