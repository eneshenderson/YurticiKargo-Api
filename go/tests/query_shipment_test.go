package tests

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/yurticikargo/api-client/functions"
)

func TestQueryShipment_Success(t *testing.T) {
	mockResponse := `<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <deliveryReportShipmentResponse xmlns="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">
      <ShippingDeliveryResultVO>
        <outFlag>0</outFlag>
        <outResult>Başarılı</outResult>
        <senderCustId>123456</senderCustId>
        <count>1</count>
        <shippingDeliveryDetailVO>
          <cargoKey>12520</cargoKey>
          <invoiceKey>INV12520</invoiceKey>
          <operationStatus>DLV</operationStatus>
          <operationMessage>Teslim edildi</operationMessage>
          <errCode>0</errCode>
          <errMessage></errMessage>
          <invDocCargoVO>
            <trackingUrl>http://tracking.yurticikargo.com/12520</trackingUrl>
            <receiverCustName>Ali Veli</receiverCustName>
            <departureUnitName>İstanbul Şube</departureUnitName>
            <deliveryDate>2024-01-15</deliveryDate>
            <deliveryTime>14:30</deliveryTime>
            <invDocCargoDAMVOArray>
              <InvDocCargoDAMVO>
                <unitName>İstanbul Şube</unitName>
                <eventName>Kabul</eventName>
                <reasonName></reasonName>
                <eventDate>2024-01-14</eventDate>
                <eventTime>10:00</eventTime>
                <cityName>İstanbul</cityName>
                <townName>Maslak</townName>
              </InvDocCargoDAMVO>
              <InvDocCargoDAMVO>
                <unitName>Ankara Şube</unitName>
                <eventName>Teslim</eventName>
                <reasonName></reasonName>
                <eventDate>2024-01-15</eventDate>
                <eventTime>14:30</eventTime>
                <cityName>Ankara</cityName>
                <townName>Çankaya</townName>
              </InvDocCargoDAMVO>
            </invDocCargoDAMVOArray>
          </invDocCargoVO>
        </shippingDeliveryDetailVO>
      </ShippingDeliveryResultVO>
    </deliveryReportShipmentResponse>
  </soap:Body>
</soap:Envelope>`

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/xml")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(mockResponse))
	}))
	defer server.Close()

	result, err := functions.QueryShipment(server.Client(), server.URL, "YKTEST", "YK", "TR", []string{"12520"}, 0, true, false)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if !result.IsSuccess() {
		t.Error("expected IsSuccess() to be true")
	}
	if result.OutFlag != 0 {
		t.Errorf("expected outFlag 0, got %d", result.OutFlag)
	}
	if len(result.Details) != 1 {
		t.Fatalf("expected 1 detail, got %d", len(result.Details))
	}

	detail := result.Details[0]
	if detail.CargoKey != "12520" {
		t.Errorf("expected cargoKey 12520, got %s", detail.CargoKey)
	}
	if detail.OperationStatus != "DLV" {
		t.Errorf("expected operationStatus DLV, got %s", detail.OperationStatus)
	}
	if !detail.IsSuccess() {
		t.Error("expected detail IsSuccess() to be true")
	}

	if detail.ItemDetail == nil {
		t.Fatal("expected itemDetail to be non-nil")
	}
	if detail.ItemDetail.ReceiverCustName != "Ali Veli" {
		t.Errorf("expected receiverCustName Ali Veli, got %s", detail.ItemDetail.ReceiverCustName)
	}
	if detail.ItemDetail.DeliveryDate != "2024-01-15" {
		t.Errorf("expected deliveryDate 2024-01-15, got %s", detail.ItemDetail.DeliveryDate)
	}
	if len(detail.ItemDetail.CargoHistory) != 2 {
		t.Fatalf("expected 2 cargo history events, got %d", len(detail.ItemDetail.CargoHistory))
	}
	if detail.ItemDetail.CargoHistory[0].EventName != "Kabul" {
		t.Errorf("expected first event Kabul, got %s", detail.ItemDetail.CargoHistory[0].EventName)
	}
}

func TestQueryShipment_NotFound(t *testing.T) {
	mockResponse := `<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <deliveryReportShipmentResponse xmlns="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">
      <ShippingDeliveryResultVO>
        <outFlag>1</outFlag>
        <outResult>Hata</outResult>
        <senderCustId>0</senderCustId>
        <count>1</count>
        <shippingDeliveryDetailVO>
          <cargoKey>NOEXIST</cargoKey>
          <invoiceKey></invoiceKey>
          <operationStatus>NOP</operationStatus>
          <operationMessage>Bulunamadı</operationMessage>
          <errCode>82526</errCode>
          <errMessage>ERR_INTG_KEYS_NOT_FOUND</errMessage>
        </shippingDeliveryDetailVO>
      </ShippingDeliveryResultVO>
    </deliveryReportShipmentResponse>
  </soap:Body>
</soap:Envelope>`

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/xml")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(mockResponse))
	}))
	defer server.Close()

	result, err := functions.QueryShipment(server.Client(), server.URL, "YKTEST", "YK", "TR", []string{"NOEXIST"}, 0, false, false)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if result.IsSuccess() {
		t.Error("expected IsSuccess() to be false")
	}
}

func TestQueryShipment_HTTPError(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusBadGateway)
		w.Write([]byte("Bad Gateway"))
	}))
	defer server.Close()

	_, err := functions.QueryShipment(server.Client(), server.URL, "YKTEST", "YK", "TR", []string{"12520"}, 0, true, false)
	if err == nil {
		t.Fatal("expected error, got nil")
	}
}
