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

// buildCancelShipmentXML builds the SOAP XML for cancelShipment.
func buildCancelShipmentXML(username, password, language string, cargoKeys []string) string {
	var sb strings.Builder

	sb.WriteString(`<?xml version="1.0" encoding="UTF-8"?>`)
	sb.WriteString(`<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ship="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">`)
	sb.WriteString(`<soapenv:Header/>`)
	sb.WriteString(`<soapenv:Body>`)
	sb.WriteString(`<ship:cancelShipment>`)
	sb.WriteString(fmt.Sprintf(`<wsUserName>%s</wsUserName>`, xmlEscape(username)))
	sb.WriteString(fmt.Sprintf(`<wsPassword>%s</wsPassword>`, xmlEscape(password)))
	sb.WriteString(fmt.Sprintf(`<wsLanguage>%s</wsLanguage>`, xmlEscape(language)))

	for _, key := range cargoKeys {
		sb.WriteString(fmt.Sprintf(`<cargoKeys>%s</cargoKeys>`, xmlEscape(key)))
	}

	sb.WriteString(`</ship:cancelShipment>`)
	sb.WriteString(`</soapenv:Body>`)
	sb.WriteString(`</soapenv:Envelope>`)

	return sb.String()
}

// cancelResponseEnvelope is used for XML parsing of the SOAP response.
type cancelResponseEnvelope struct {
	XMLName xml.Name         `xml:"Envelope"`
	Body    cancelResponseBody `xml:"Body"`
}

type cancelResponseBody struct {
	CancelResponse cancelShipmentResponse `xml:"cancelShipmentResponse"`
}

type cancelShipmentResponse struct {
	CancelResult cancelResultXML `xml:"cancelShipmentResultVO"`
}

type cancelResultXML struct {
	OutFlag      int               `xml:"outFlag"`
	OutResult    string            `xml:"outResult"`
	SenderCustId int               `xml:"senderCustId"`
	Count        int               `xml:"count"`
	Details      []cancelDetailXML `xml:"cancelShipmentDetailVO"`
}

type cancelDetailXML struct {
	CargoKey         string `xml:"cargoKey"`
	InvoiceKey       string `xml:"invoiceKey"`
	JobId            int    `xml:"jobId"`
	DocId            string `xml:"docId"`
	OperationCode    int    `xml:"operationCode"`
	OperationMessage string `xml:"operationMessage"`
	OperationStatus  string `xml:"operationStatus"`
	ErrCode          int    `xml:"errCode"`
	ErrMessage       string `xml:"errMessage"`
}

// CancelShipment sends a cancel shipment SOAP request and returns the result.
func CancelShipment(client *http.Client, endpoint, username, password, language string, cargoKeys []string) (*models.CancelResult, error) {
	soapXML := buildCancelShipmentXML(username, password, language, cargoKeys)

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

	var envelope cancelResponseEnvelope
	if err := xml.Unmarshal(body, &envelope); err != nil {
		return nil, fmt.Errorf("failed to parse response XML: %w", err)
	}

	result := &models.CancelResult{
		OutFlag:      envelope.Body.CancelResponse.CancelResult.OutFlag,
		OutResult:    envelope.Body.CancelResponse.CancelResult.OutResult,
		SenderCustId: envelope.Body.CancelResponse.CancelResult.SenderCustId,
		Count:        envelope.Body.CancelResponse.CancelResult.Count,
	}

	for _, d := range envelope.Body.CancelResponse.CancelResult.Details {
		result.Details = append(result.Details, models.CancelDetail{
			CargoKey:         d.CargoKey,
			InvoiceKey:       d.InvoiceKey,
			JobId:            d.JobId,
			DocId:            d.DocId,
			OperationCode:    d.OperationCode,
			OperationMessage: d.OperationMessage,
			OperationStatus:  d.OperationStatus,
			ErrCode:          d.ErrCode,
			ErrMessage:       d.ErrMessage,
		})
	}

	return result, nil
}
