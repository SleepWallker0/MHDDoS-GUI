self.onmessage = function(e) {
    const { type, data, payload } = e.data;

    if (type === 'downsample') {
        const { targetLength, taskId } = payload;
        const result = doDownsample(data, targetLength, taskId);
        self.postMessage({ type: 'downsample_result', result, id: payload.id });
    } else if (type === 'serialize') {
        // limit history buffer size for localStorage
        const dataToSave = data.length > 2000 ? doDownsample(data, 2000) : data;
        const serialized = JSON.stringify(dataToSave);
        self.postMessage({ type: 'serialize_result', serialized });
    }
};

function doDownsample(data, targetLength, taskId = null) {
    if (data.length <= targetLength) {
        if (taskId) {
            return data.map(point => {
                const m = point.tasks?.[taskId];
                return {
                    time: point.time,
                    rps: m ? m.rps || 0 : 0,
                    bps: m ? m.bps || 0 : 0,
                    lat: m ? m.lat || 0 : 0,
                    s: m ? m.s || 0 : 0,
                    w: m ? m.w || 0 : 0,
                    e: m ? m.e || 0 : 0,
                    t: m ? m.t || 0 : 0
                };
            });
        }
        return data;
    }
    const factor = Math.ceil(data.length / targetLength);
    const res = [];
    for (let i = 0; i < data.length; i += factor) {
        const chunk = data.slice(i, i + factor);

        let rps = 0, bps = 0, lat = 0, count = 0;
        let s = 0, w = 0, e = 0, t = 0;

        chunk.forEach(point => {
            if (taskId) {
                const m = point.tasks?.[taskId];
                if (m) {
                    rps += m.rps || 0;
                    bps += m.bps || 0;
                    lat += m.lat || 0;
                    s += m.s || 0;
                    w += m.w || 0;
                    e += m.e || 0;
                    t += m.t || 0;
                    count++;
                }
            } else {
                rps += point.rps || 0;
                bps += point.bps || 0;
                lat += point.lat || 0;
                s += point.s || 0;
                w += point.w || 0;
                e += point.e || 0;
                t += point.t || 0;
                count++;
            }
        });

        if (count > 0) {
            res.push({
                time: chunk[chunk.length - 1].time, // use end of chunk time
                rps: Math.round(rps / count),
                bps: Math.round(bps / count),
                lat: Math.round(lat / count),
                s: Math.round(s / count),
                w: Math.round(w / count),
                e: Math.round(e / count),
                t: Math.round(t / count)
            });
        }
    }
    return res;
}
