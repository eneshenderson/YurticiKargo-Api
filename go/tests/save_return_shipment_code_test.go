package tests

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/yurticikargo/api-client/functions"
)

func TestSaveReturnShipmentCode_Success(t *testing.T) {
	mockResponse := `<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <saveReturnShipmentCodeResponse xmlns="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">
      <saveReturnShipmentCodeResultVO>
        <outFlag>0</outFlag>
        <outResult>Başarılı</outResult>
        <errCode>0</errCode>
      </saveReturnShipmentCodeResultVO>
    </saveReturnShipmentCodeResponse>
  </soap:Body>
</soap:Envelope>`

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/xml")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(mockResponse))
	}))
	defer server.Close()

	result, err := functions.SaveReturnShipmentCode(
		server.Client(), server.URL, "YKTEST", "YK", "TR",
		"RMA-2024-001", "20240101", "20240131", 1, "53",
	)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if !result.IsSuccess() {
		t.Error("expected IsSuccess() to be true")
	}
	if result.OutFlag != 0 {
		t.Errorf("expected outFlag 0, got %d", result.OutFlag)
	}
	if result.ErrCode != 0 {
		t.Errorf("expected errCode 0, got %d", result.ErrCode)
	}
}

func TestSaveReturnShipmentCode_DuplicateCode(t *testing.T) {
	mockResponse := `<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <saveReturnShipmentCodeResponse xmlns="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">
      <saveReturnShipmentCodeResultVO>
        <outFlag>1</outFlag>
        <outResult>İade kodu daha önceden kaydedilmiştir</outResult>
        <errCode>82655</errCode>
      </saveReturnShipmentCodeResultVO>
    </saveReturnShipmentCodeResponse>
  </soap:Body>
</soap:Envelope>`

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/xml")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(mockResponse))
	}))
	defer server.Close()

	result, err := functions.SaveReturnShipmentCode(
		server.Client(), server.URL, "YKTEST", "YK", "TR",
		"RMA-2024-001", "20240101", "20240131", 1, "53",
	)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if result.IsSuccess() {
		t.Error("expected IsSuccess() to be false")
	}
	if result.ErrCode != 82655 {
		t.Errorf("expected errCode 82655, got %d", result.ErrCode)
	}
}

func TestSaveReturnShipmentCode_HTTPError(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte("Server Error"))
	}))
	defer server.Close()

	_, err := functions.SaveReturnShipmentCode(
		server.Client(), server.URL, "YKTEST", "YK", "TR",
		"RMA-2024-001", "20240101", "20240131", 1, "53",
	)
	if err == nil {
		t.Fatal("expected error, got nil")
	}
}
