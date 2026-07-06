package tests

import (
	"encoding/xml"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/yurticikargo/api-client/functions"
	"github.com/yurticikargo/api-client/models"
)

func TestCreateShipment_Success(t *testing.T) {
	mockResponse := `<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <dispatchResponse xmlns="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">
      <ShippingOrderResultVO>
        <outFlag>0</outFlag>
        <outResult>Başarılı</outResult>
        <jobId>12345</jobId>
        <count>1</count>
        <shippingOrderDetailVO>
          <cargoKey>TEST001</cargoKey>
          <invoiceKey>INV001</invoiceKey>
          <errCode>0</errCode>
          <errMessage>Başarılı</errMessage>
        </shippingOrderDetailVO>
      </ShippingOrderResultVO>
    </dispatchResponse>
  </soap:Body>
</soap:Envelope>`

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" {
			t.Errorf("expected POST, got %s", r.Method)
		}
		if r.Header.Get("Content-Type") != "text/xml; charset=utf-8" {
			t.Errorf("unexpected content type: %s", r.Header.Get("Content-Type"))
		}
		w.Header().Set("Content-Type", "text/xml")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(mockResponse))
	}))
	defer server.Close()

	shipments := []models.ShipmentOrder{
		{
			CargoKey:         "TEST001",
			InvoiceKey:       "INV001",
			ReceiverCustName: "Test User",
			ReceiverAddress:  "Test Address",
			ReceiverPhone1:   "05551234567",
			CityName:         "İstanbul",
			TownName:         "Maslak",
		},
	}

	result, err := functions.CreateShipment(server.Client(), server.URL, "YKTEST", "YK", "TR", shipments)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if result.OutFlag != 0 {
		t.Errorf("expected outFlag 0, got %d", result.OutFlag)
	}
	if result.JobId != 12345 {
		t.Errorf("expected jobId 12345, got %d", result.JobId)
	}
	if len(result.Details) != 1 {
		t.Fatalf("expected 1 detail, got %d", len(result.Details))
	}
	if result.Details[0].CargoKey != "TEST001" {
		t.Errorf("expected cargoKey TEST001, got %s", result.Details[0].CargoKey)
	}
	if !result.IsSuccess() {
		t.Error("expected IsSuccess() to be true")
	}
}

func TestCreateShipment_Error(t *testing.T) {
	mockResponse := `<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <dispatchResponse xmlns="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">
      <ShippingOrderResultVO>
        <outFlag>1</outFlag>
        <outResult>Hata oluştu</outResult>
        <jobId>0</jobId>
        <count>1</count>
        <shippingOrderDetailVO>
          <cargoKey>TEST001</cargoKey>
          <invoiceKey>INV001</invoiceKey>
          <errCode>60020</errCode>
          <errMessage>ERR_EXIST_CARGO_KEY_PARAM</errMessage>
        </shippingOrderDetailVO>
      </ShippingOrderResultVO>
    </dispatchResponse>
  </soap:Body>
</soap:Envelope>`

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/xml")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(mockResponse))
	}))
	defer server.Close()

	shipments := []models.ShipmentOrder{
		{
			CargoKey:         "TEST001",
			InvoiceKey:       "INV001",
			ReceiverCustName: "Test User",
			ReceiverAddress:  "Test Address",
			ReceiverPhone1:   "05551234567",
		},
	}

	result, err := functions.CreateShipment(server.Client(), server.URL, "YKTEST", "YK", "TR", shipments)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if result.IsSuccess() {
		t.Error("expected IsSuccess() to be false")
	}
	if result.OutFlag != 1 {
		t.Errorf("expected outFlag 1, got %d", result.OutFlag)
	}

	errors := result.GetErrors()
	if len(errors) != 1 {
		t.Fatalf("expected 1 error, got %d", len(errors))
	}
	if errors[0].ErrCode != 60020 {
		t.Errorf("expected errCode 60020, got %d", errors[0].ErrCode)
	}
}

func TestCreateShipment_HTTPError(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte("Internal Server Error"))
	}))
	defer server.Close()

	shipments := []models.ShipmentOrder{
		{
			CargoKey:         "TEST001",
			InvoiceKey:       "INV001",
			ReceiverCustName: "Test User",
			ReceiverAddress:  "Test Address",
			ReceiverPhone1:   "05551234567",
		},
	}

	_, err := functions.CreateShipment(server.Client(), server.URL, "YKTEST", "YK", "TR", shipments)
	if err == nil {
		t.Fatal("expected error, got nil")
	}
}

// Verify ShipmentOrder XML tags are correct
func TestShipmentOrder_XMLSerialization(t *testing.T) {
	order := models.ShipmentOrder{
		CargoKey:         "KEY1",
		InvoiceKey:       "INV1",
		ReceiverCustName: "John",
		ReceiverAddress:  "Address",
		ReceiverPhone1:   "123",
	}

	data, err := xml.Marshal(order)
	if err != nil {
		t.Fatalf("failed to marshal: %v", err)
	}

	xmlStr := string(data)
	if !contains(xmlStr, "<cargoKey>KEY1</cargoKey>") {
		t.Error("missing cargoKey in XML output")
	}
	if !contains(xmlStr, "<invoiceKey>INV1</invoiceKey>") {
		t.Error("missing invoiceKey in XML output")
	}
}

func contains(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || len(s) > 0 && containsHelper(s, substr))
}

func containsHelper(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}
