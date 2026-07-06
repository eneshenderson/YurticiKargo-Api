package tests

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/yurticikargo/api-client/functions"
)

func TestCancelShipment_Success(t *testing.T) {
	mockResponse := `<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <cancelShipmentResponse xmlns="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">
      <cancelShipmentResultVO>
        <outFlag>0</outFlag>
        <outResult>Başarılı</outResult>
        <senderCustId>123456</senderCustId>
        <count>2</count>
        <cancelShipmentDetailVO>
          <cargoKey>KEY001</cargoKey>
          <invoiceKey>INV001</invoiceKey>
          <jobId>100</jobId>
          <docId>DOC001</docId>
          <operationCode>3</operationCode>
          <operationMessage>Kargo çıkışı engellendi</operationMessage>
          <operationStatus>CNL</operationStatus>
          <errCode>0</errCode>
          <errMessage></errMessage>
        </cancelShipmentDetailVO>
        <cancelShipmentDetailVO>
          <cargoKey>KEY002</cargoKey>
          <invoiceKey>INV002</invoiceKey>
          <jobId>101</jobId>
          <docId>DOC002</docId>
          <operationCode>4</operationCode>
          <operationMessage>Kargo zaten iptal edilmiş</operationMessage>
          <operationStatus>ISC</operationStatus>
          <errCode>0</errCode>
          <errMessage></errMessage>
        </cancelShipmentDetailVO>
      </cancelShipmentResultVO>
    </cancelShipmentResponse>
  </soap:Body>
</soap:Envelope>`

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/xml")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(mockResponse))
	}))
	defer server.Close()

	result, err := functions.CancelShipment(server.Client(), server.URL, "YKTEST", "YK", "TR", []string{"KEY001", "KEY002"})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if !result.IsSuccess() {
		t.Error("expected IsSuccess() to be true")
	}
	if result.OutFlag != 0 {
		t.Errorf("expected outFlag 0, got %d", result.OutFlag)
	}
	if result.SenderCustId != 123456 {
		t.Errorf("expected senderCustId 123456, got %d", result.SenderCustId)
	}
	if len(result.Details) != 2 {
		t.Fatalf("expected 2 details, got %d", len(result.Details))
	}
	if result.Details[0].OperationStatus != "CNL" {
		t.Errorf("expected operationStatus CNL, got %s", result.Details[0].OperationStatus)
	}
	if result.Details[1].OperationStatus != "ISC" {
		t.Errorf("expected operationStatus ISC, got %s", result.Details[1].OperationStatus)
	}
}

func TestCancelShipment_NotFound(t *testing.T) {
	mockResponse := `<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <cancelShipmentResponse xmlns="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">
      <cancelShipmentResultVO>
        <outFlag>1</outFlag>
        <outResult>Hata</outResult>
        <senderCustId>0</senderCustId>
        <count>1</count>
        <cancelShipmentDetailVO>
          <cargoKey>NOEXIST</cargoKey>
          <invoiceKey></invoiceKey>
          <jobId>0</jobId>
          <docId></docId>
          <operationCode>0</operationCode>
          <operationMessage>Kargo bulunamadı</operationMessage>
          <operationStatus>NOP</operationStatus>
          <errCode>82519</errCode>
          <errMessage>ERR_INTG_CARGO_KEY_NOT_FOUND</errMessage>
        </cancelShipmentDetailVO>
      </cancelShipmentResultVO>
    </cancelShipmentResponse>
  </soap:Body>
</soap:Envelope>`

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/xml")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(mockResponse))
	}))
	defer server.Close()

	result, err := functions.CancelShipment(server.Client(), server.URL, "YKTEST", "YK", "TR", []string{"NOEXIST"})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if result.IsSuccess() {
		t.Error("expected IsSuccess() to be false")
	}
	if result.Details[0].ErrCode != 82519 {
		t.Errorf("expected errCode 82519, got %d", result.Details[0].ErrCode)
	}
}

func TestCancelShipment_HTTPError(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusServiceUnavailable)
		w.Write([]byte("Service Unavailable"))
	}))
	defer server.Close()

	_, err := functions.CancelShipment(server.Client(), server.URL, "YKTEST", "YK", "TR", []string{"KEY001"})
	if err == nil {
		t.Fatal("expected error, got nil")
	}
}
