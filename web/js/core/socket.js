export class SocketManager {
    constructor(url, onMessage) {
        this.url = url;
        this.onMessage = onMessage;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.ws = new WebSocket(`${protocol}//${window.location.host}${this.url}`);
        
        this.ws.onopen = () => {
            console.log("WebSocket connected.");
            this.reconnectAttempts = 0;
            const dot = document.getElementById('connection-status-dot');
            if (dot) {
                dot.classList.remove('bg-error', 'bg-warning');
                dot.classList.add('bg-primary', 'status-pulse');
            }
        };
        
        this.ws.onmessage = (e) => {
            try {
                this.onMessage(JSON.parse(e.data));
            } catch (err) {
                console.error("Error parsing WS message:", err);
            }
        };
        
        this.ws.onclose = () => {
            console.warn("WebSocket disconnected. Attempting reconnect...");
            const dot = document.getElementById('connection-status-dot');
            if (dot) {
                dot.classList.remove('bg-primary', 'status-pulse');
                dot.classList.add('bg-warning');
            }
            this.scheduleReconnect();
        };
    }

    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            const delay = Math.pow(2, this.reconnectAttempts) * 1000;
            setTimeout(() => this.connect(), delay);
            this.reconnectAttempts++;
        }
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }
}