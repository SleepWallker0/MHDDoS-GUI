/**
 * MHDDoS PRO MAX — UI Intelligence & Fluid Motion Controller
 * Orchestrates professional transitions and high-performance micro-interactions.
 */

export class UIProMax {
    constructor() {
        this.appState = document.body.dataset.appState || 'idle';
        this.initialized = false;
    }

    init() {
        if (this.initialized) return;
        this.setupMicroInteractions();
        this.initialized = true;
        console.log('UI_PRO_MAX: Operations_Initialized');
    }

    /**
     * Enhances buttons and cards with tactical visual cues
     */
    setupMicroInteractions() {
        const buttons = document.querySelectorAll('button');
        buttons.forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                // Future: trigger short tactical audio beep
            });
        });
    }

    /**
     * Orchestrates smooth view switching
     */
    switchView(viewId) {
        const views = ['dashboard', 'history'];
        views.forEach(v => {
            const el = document.getElementById(`view-${v}`);
            if (el) {
                if (v === viewId) {
                    el.classList.remove('hidden');
                } else {
                    el.classList.add('hidden');
                }
            }
        });

        // Update navigation active states
        navs.forEach(n => {
            const btn = document.getElementById(`tab-nav-${n}`);
            if (btn) {
                if (n === viewId) {
                    btn.classList.add('bg-primary/10', 'text-primary', 'border-primary');
                    btn.classList.remove('text-on-surface-variant', 'border-transparent');
                } else {
                    btn.classList.remove('bg-primary/10', 'text-primary', 'border-primary');
                    btn.classList.add('text-on-surface-variant', 'border-transparent');
                }
            }
        });
    }

    /**
     * Updates the global app state and triggers visual sequence
     */
    setAppState(state) {
        document.body.dataset.appState = state;
        this.appState = state;

        const deployBtn = document.getElementById('deploy-hub-btn');
        const deployIcon = document.getElementById('deploy-hub-icon');
        const deployText = document.getElementById('deploy-hub-text');

        if (!deployBtn) return;

        switch(state) {
            case 'running':
                deployBtn.classList.remove('bg-primary');
                deployBtn.classList.add('bg-error');
                deployText.innerText = 'Stop Attack';
                deployIcon.innerText = 'stop_circle';
                break;
            case 'starting':
                deployBtn.disabled = true;
                deployText.innerText = 'Initializing...';
                deployIcon.innerText = 'hourglass_empty';
                deployIcon.classList.add('animate-spin');
                break;
            case 'stopping':
                deployBtn.disabled = true;
                deployText.innerText = 'Stopping...';
                deployIcon.innerText = 'refresh';
                deployIcon.classList.add('animate-spin');
                break;
            default:
                deployBtn.disabled = false;
                deployBtn.classList.add('bg-primary');
                deployBtn.classList.remove('bg-error');
                deployText.innerText = 'Start Attack';
                deployIcon.innerText = 'play_arrow';
                deployIcon.classList.remove('animate-spin');
        }
    }
}

export const uiProMax = new UIProMax();
