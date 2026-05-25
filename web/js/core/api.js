export async function apiRequest(endpoint, params = {}) {
    const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
    });
    return await res.json();
}

export async function fetchStatus() {
    const res = await fetch('/api/attack/status');
    return await res.json();
}