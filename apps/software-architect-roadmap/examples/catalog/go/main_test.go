package main

import (
    "net/http/httptest"
    "encoding/json"
    "testing"
)

func TestProducts(t *testing.T) {
    request := httptest.NewRequest("GET", "/products", nil)
    recorder := httptest.NewRecorder()
    handler(recorder, request)
    var products []Product
    if err := json.Unmarshal(recorder.Body.Bytes(), &products); err != nil { t.Fatal(err) }
    if recorder.Code != 200 || len(products) != 2 || products[0].UnitPrice != 1200 {
        t.Fatalf("unexpected catalog: %s", recorder.Body.String())
    }
}

func TestWrongMethod(t *testing.T) {
    recorder := httptest.NewRecorder()
    handler(recorder, httptest.NewRequest("POST", "/products", nil))
    if recorder.Code != 405 { t.Fatal(recorder.Code) }
}
