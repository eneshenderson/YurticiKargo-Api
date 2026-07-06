package functions

import (
	"bytes"
	"encoding/xml"
	"fmt"
	"io"
	"net/http"
	"strings"

	"github.com/yurticikargo/api-client/models"
)

// createShipmentEnvelope builds the SOAP XML for createShipment (dispatch).
func buildCreateShipmentXML(username, password, language string, shipments []models.ShipmentOrder) string {
	var sb strings.Builder

	sb.WriteString(`<?xml version="1.0" encoding="UTF-8"?>`)
	sb.WriteString(`<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ship="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">`)
	sb.WriteString(`<soapenv:Header/>`)
	sb.WriteString(`<soapenv:Body>`)
	sb.WriteString(`<ship:dispatch>`)
	sb.WriteString(fmt.Sprintf(`<wsUserName>%s</wsUserName>`, xmlEscape(username)))
	sb.WriteString(fmt.Sprintf(`<wsPassword>%s</wsPassword>`, xmlEscape(password)))
	sb.WriteString(fmt.Sprintf(`<wsLanguage>%s</wsLanguage>`, xmlEscape(language)))
	sb.WriteString(`<ShippingOrderVO>`)

	for _, s := range shipments {
		sb.WriteString(`<ShippingOrderDetailVO>`)
		sb.WriteString(fmt.Sprintf(`<cargoKey>%s</cargoKey>`, xmlEscape(s.CargoKey)))
		sb.WriteString(fmt.Sprintf(`<invoiceKey>%s</invoiceKey>`, xmlEscape(s.InvoiceKey)))
		sb.WriteString(fmt.Sprintf(`<receiverCustName>%s</receiverCustName>`, xmlEscape(s.ReceiverCustName)))
		sb.WriteString(fmt.Sprintf(`<receiverAddress>%s</receiverAddress>`, xmlEscape(s.ReceiverAddress)))
		sb.WriteString(fmt.Sprintf(`<receiverPhone1>%s</receiverPhone1>`, xmlEscape(s.ReceiverPhone1)))

		if s.ReceiverPhone2 != "" {
			sb.WriteString(fmt.Sprintf(`<receiverPhone2>%s</receiverPhone2>`, xmlEscape(s.ReceiverPhone2)))
		}
		if s.ReceiverPhone3 != "" {
			sb.WriteString(fmt.Sprintf(`<receiverPhone3>%s</receiverPhone3>`, xmlEscape(s.ReceiverPhone3)))
		}
		if s.CityName != "" {
			sb.WriteString(fmt.Sprintf(`<cityName>%s</cityName>`, xmlEscape(s.CityName)))
		}
		if s.TownName != "" {
			sb.WriteString(fmt.Sprintf(`<townName>%s</townName>`, xmlEscape(s.TownName)))
		}
		if s.CustProdId != "" {
			sb.WriteString(fmt.Sprintf(`<custProdId>%s</custProdId>`, xmlEscape(s.CustProdId)))
		}
		if s.Desi != "" {
			sb.WriteString(fmt.Sprintf(`<desi>%s</desi>`, xmlEscape(s.Desi)))
		}
		if s.Kg != "" {
			sb.WriteString(fmt.Sprintf(`<kg>%s</kg>`, xmlEscape(s.Kg)))
		}
		if s.CargoCount > 0 {
			sb.WriteString(fmt.Sprintf(`<cargoCount>%d</cargoCount>`, s.CargoCount))
		}
		if s.WaybillNo != "" {
			sb.WriteString(fmt.Sprintf(`<waybillNo>%s</waybillNo>`, xmlEscape(s.WaybillNo)))
		}
		if s.SpecialField1 != "" {
			sb.WriteString(fmt.Sprintf(`<specialField1>%s</specialField1>`, xmlEscape(s.SpecialField1)))
		}
		if s.SpecialField2 != "" {
			sb.WriteString(fmt.Sprintf(`<specialField2>%s</specialField2>`, xmlEscape(s.SpecialField2)))
		}
		if s.SpecialField3 != "" {
			sb.WriteString(fmt.Sprintf(`<specialField3>%s</specialField3>`, xmlEscape(s.SpecialField3)))
		}
		if s.TtCollectionType != "" {
			sb.WriteString(fmt.Sprintf(`<ttCollectionType>%s</ttCollectionType>`, xmlEscape(s.TtCollectionType)))
		}
		if s.TtInvoiceAmount != "" {
			sb.WriteString(fmt.Sprintf(`<ttInvoiceAmount>%s</ttInvoiceAmount>`, xmlEscape(s.TtInvoiceAmount)))
		}
		if s.TtDocumentId != "" {
			sb.WriteString(fmt.Sprintf(`<ttDocumentId>%s</ttDocumentId>`, xmlEscape(s.TtDocumentId)))
		}
		if s.TtDocumentSaveType != "" {
			sb.WriteString(fmt.Sprintf(`<ttDocumentSaveType>%s</ttDocumentSaveType>`, xmlEscape(s.TtDocumentSaveType)))
		}
		if s.DcSelectedCredit != "" {
			sb.WriteString(fmt.Sprintf(`<dcSelectedCredit>%s</dcSelectedCredit>`, xmlEscape(s.DcSelectedCredit)))
		}
		if s.DcCreditRule != "" {
			sb.WriteString(fmt.Sprintf(`<dcCreditRule>%s</dcCreditRule>`, xmlEscape(s.DcCreditRule)))
		}
		if s.OrgReceiverCustId != "" {
			sb.WriteString(fmt.Sprintf(`<orgReceiverCustId>%s</orgReceiverCustId>`, xmlEscape(s.OrgReceiverCustId)))
		}
		if s.Description != "" {
			sb.WriteString(fmt.Sprintf(`<description>%s</description>`, xmlEscape(s.Description)))
		}
		if s.TaxNumber != "" {
			sb.WriteString(fmt.Sprintf(`<taxNumber>%s</taxNumber>`, xmlEscape(s.TaxNumber)))
		}
		if s.TaxOfficeId != "" {
			sb.WriteString(fmt.Sprintf(`<taxOfficeId>%s</taxOfficeId>`, xmlEscape(s.TaxOfficeId)))
		}
		if s.TaxOfficeName != "" {
			sb.WriteString(fmt.Sprintf(`<taxOfficeName>%s</taxOfficeName>`, xmlEscape(s.TaxOfficeName)))
		}
		if s.OrgGeoCode != "" {
			sb.WriteString(fmt.Sprintf(`<orgGeoCode>%s</orgGeoCode>`, xmlEscape(s.OrgGeoCode)))
		}
		if s.PrivilegeOrder != "" {
			sb.WriteString(fmt.Sprintf(`<privilegeOrder>%s</privilegeOrder>`, xmlEscape(s.PrivilegeOrder)))
		}
		if s.EmailAddress != "" {
			sb.WriteString(fmt.Sprintf(`<emailAddress>%s</emailAddress>`, xmlEscape(s.EmailAddress)))
		}

		sb.WriteString(`</ShippingOrderDetailVO>`)
	}

	sb.WriteString(`</ShippingOrderVO>`)
	sb.WriteString(`</ship:dispatch>`)
	sb.WriteString(`</soapenv:Body>`)
	sb.WriteString(`</soapenv:Envelope>`)

	return sb.String()
}

// shipmentResponseEnvelope is used for XML parsing of the SOAP response.
type shipmentResponseEnvelope struct {
	XMLName xml.Name            `xml:"Envelope"`
	Body    shipmentResponseBody `xml:"Body"`
}

type shipmentResponseBody struct {
	DispatchResponse shipmentDispatchResponse `xml:"dispatchResponse"`
}

type shipmentDispatchResponse struct {
	ShippingOrderResult shipmentResultXML `xml:"ShippingOrderResultVO"`
}

type shipmentResultXML struct {
	OutFlag   int                    `xml:"outFlag"`
	OutResult string                 `xml:"outResult"`
	JobId     int                    `xml:"jobId"`
	Count     int                    `xml:"count"`
	Details   []shipmentDetailXML    `xml:"shippingOrderDetailVO"`
}

type shipmentDetailXML struct {
	CargoKey   string `xml:"cargoKey"`
	InvoiceKey string `xml:"invoiceKey"`
	ErrCode    int    `xml:"errCode"`
	ErrMessage string `xml:"errMessage"`
}

// CreateShipment sends a create shipment SOAP request and returns the result.
func CreateShipment(client *http.Client, endpoint, username, password, language string, shipments []models.ShipmentOrder) (*models.ShipmentResult, error) {
	soapXML := buildCreateShipmentXML(username, password, language, shipments)

	req, err := http.NewRequest("POST", endpoint, bytes.NewBufferString(soapXML))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "text/xml; charset=utf-8")
	req.Header.Set("SOAPAction", "")

	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to send request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("SOAP fault: HTTP %d - %s", resp.StatusCode, string(body))
	}

	var envelope shipmentResponseEnvelope
	if err := xml.Unmarshal(body, &envelope); err != nil {
		return nil, fmt.Errorf("failed to parse response XML: %w", err)
	}

	result := &models.ShipmentResult{
		OutFlag:   envelope.Body.DispatchResponse.ShippingOrderResult.OutFlag,
		OutResult: envelope.Body.DispatchResponse.ShippingOrderResult.OutResult,
		JobId:     envelope.Body.DispatchResponse.ShippingOrderResult.JobId,
		Count:     envelope.Body.DispatchResponse.ShippingOrderResult.Count,
	}

	for _, d := range envelope.Body.DispatchResponse.ShippingOrderResult.Details {
		result.Details = append(result.Details, models.ShipmentDetail{
			CargoKey:   d.CargoKey,
			InvoiceKey: d.InvoiceKey,
			ErrCode:    d.ErrCode,
			ErrMessage: d.ErrMessage,
		})
	}

	return result, nil
}
