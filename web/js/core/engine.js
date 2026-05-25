import { apiRequest } from './api.js';
import { showToast } from '../ui/toast.js';
import { uiProMax } from '../ui/ui-pro-max.js';

let isRunning = false;

export async function handleMainAction() {
    if (isRunning) {
        uiProMax.setAppState('stopping');
        showToast("Stopping all active deployments...", "warning");
        try {
            const res = await apiRequest('/api/attack/status');
            if (res.status === 'success' && res.active_tasks) {
                for (let t of res.active_tasks) {
                    await apiRequest('/api/attack/stop', { task_id: t.task_id });
                }
            }
            isRunning = false;
            uiProMax.setAppState('idle');
            showToast("Global sequence terminated.", "success");
        } catch (e) {
            showToast("Termination failed.", "error");
            uiProMax.setAppState('running');
        }
        return;
    }

    const target = document.getElementById('target').value;
    const method = document.getElementById('method').value;
    const threads = parseInt(document.getElementById('threads')?.value || '100');
    const duration = parseInt(document.getElementById('duration')?.value || '3600');
    const rpc = parseInt(document.getElementById('rpc')?.value || '100');
    
    // Advanced Parameters
    const proxy_type = document.getElementById('proxy_type')?.value || 'SOCKS5';
    const proxy_refresh = parseInt(document.getElementById('proxy_refresh')?.value || '0');
    const proxy_list = document.getElementById('proxy_list')?.value || '';
    const reflector = document.getElementById('reflector')?.value || '';
    
    // Boolean Flags
    const auto_harvest = document.getElementById('auto_harvest')?.checked || false;
    const smart_rpc = document.getElementById('smart_rpc')?.checked || false;
    const autoscale = document.getElementById('autoscale')?.checked || false;
    const evasion = document.getElementById('evasion')?.checked || false;
    const distribute_to_workers = document.getElementById('distribute_to_workers')?.checked || false;

    if (!target) return showToast("Target required.", "warning");

    uiProMax.setAppState('starting');
    showToast(`Initiating ${method} against ${target}`, "info");

    try {
        const payload = {
            target,
            method,
            threads,
            duration,
            rpc,
            proxy_type,
            proxy_refresh,
            proxy_list,
            reflector,
            auto_harvest,
            smart_rpc,
            autoscale,
            evasion,
            distribute_to_workers
        };

        const data = await apiRequest('/api/attack/start', payload);
        if (data.status === 'success') {
            isRunning = true;
            uiProMax.setAppState('running');
            showToast("Attack sequence authorized.", "success");
        } else {
            isRunning = false;
            uiProMax.setAppState('idle');
            showToast(data.message || "Deployment rejected.", "error");
        }
    } catch (e) {
        isRunning = false;
        uiProMax.setAppState('idle');
        showToast("Backend connection failed.", "error");
    }
}

export async function analyzeTarget() {
    const target = document.getElementById('target').value;
    if (!target) return showToast("Target required for radar scan.", "warning");

    showToast("Analyzing infrastructure...", "info");
    try {
        const data = await apiRequest('/api/recon/analyze', { target });
        if (data.status === 'success') {
            document.getElementById('method').value = data.recommendation;
            showToast(`Target identified. Recommended: ${data.recommendation}`, "success");
        }
    } catch (e) {
        showToast("Reconnaissance failed.", "error");
    }
}
