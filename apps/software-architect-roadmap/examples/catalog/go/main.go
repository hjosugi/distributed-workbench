package main

import (
    "encoding/json"
    "log"
    "net/http"
    "os"
    "time"
)

type Product struct {
    SKU string `json:"sku"`
    UnitPrice int `json:"unit_price"`
}

func handler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    status := http.StatusOK
    var body any
    switch {
    case r.Method != "GET":
        status, body = 405, map[string]string{"error": "method not allowed"}
    case r.URL.Path == "/products":
        body = []Product{{"book", 1200}, {"pen", 200}}
    case r.URL.Path == "/health":
        body = map[string]string{"status": "ok"}
    default:
        status, body = 404, map[string]string{"error": "not found"}
    }
    w.WriteHeader(status)
    if err := json.NewEncoder(w).Encode(body); err != nil { log.Print(err) }
}

func main() {
    host, port := os.Getenv("BIND_HOST"), os.Getenv("PORT")
    if host == "" { host = "127.0.0.1" }
    if port == "" { port = "8081" }
    server := &http.Server{Addr: host + ":" + port, Handler: http.HandlerFunc(handler),
        ReadHeaderTimeout: 5*time.Second, ReadTimeout: 5*time.Second, WriteTimeout: 5*time.Second}
    log.Fatal(server.ListenAndServe())
}
