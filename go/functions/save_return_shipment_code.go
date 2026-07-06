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

// buildSaveReturnShipmentCodeXML builds the SOAP XML for saveReturnShipmentCode.
func buildSaveReturnShipmentCodeXML(username, password, language, returnCode, startDate, endDate string, maxCount int, fieldName string) string {
	var sb strings.Builder

	sb.WriteString(`<?xml version="1.0" encoding="UTF-8"?>`)
	sb.WriteString(`<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ship="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">`)
	sb.WriteString(`<soapenv:Header/>`)
	sb.WriteString(`<soapenv:Body>`)
	sb.WriteString(`<ship:saveReturnShipmentCode>`)
	sb.WriteString(fmt.Sprintf(`<wsUserName>%s</wsUserName>`, xmlEscape(username)))
	sb.WriteString(fmt.Sprintf(`<wsPassword>%s</wsPassword>`, xmlEscape(password)))
	sb.WriteString(fmt.Sprintf(`<wsLanguage>%s</wsLanguage>`, xmlEscape(language)))
	sb.WriteString(fmt.Sprintf(`<fieldName>%s</fieldName>`, xmlEscape(fieldName)))
	sb.WriteString(fmt.Sprintf(`<returnCode>%s</returnCode>`, xmlEscape(returnCode)))
	sb.WriteString(fmt.Sprintf(`<startDate>%s</startDate>`, xmlEscape(startDate)))
	sb.WriteString(fmt.Sprintf(`<endDate>%s</endDate>`, xmlEscape(endDate)))
	sb.WriteString(fmt.Sprintf(`<maxCount>%d</maxCount>`, maxCount))
	sb.WriteString(`</ship:saveReturnShipmentCode>`)
	sb.WriteString(`</soapenv:Body>`)
	sb.WriteString(`</soapenv:Envelope>`)

	return sb.String()
}

// returnCodeResponseEnvelope is used for XML parsing of the SOAP response.
type returnCodeResponseEnvelope struct {
	XMLName xml.Name             `xml:"Envelope"`
	Body    returnCodeResponseBody `xml:"Body"`
}

type returnCodeResponseBody struct {
	ReturnCodeResponse saveReturnCodeResponse `xml:"saveReturnShipmentCodeResponse"`
}

type saveReturnCodeResponse struct {
	ReturnCodeResult returnCodeResultXML `xml:"saveReturnShipmentCodeResultVO"`
}

type returnCodeResultXML struct {
	OutFlag   int    `xml:"outFlag"`
	OutResult string `xml:"outResult"`
	ErrCode   int    `xml:"errCode"`
}

// SaveReturnShipmentCode sends a save return shipment code SOAP request and returns the result.
func SaveReturnShipmentCode(client *http.Client, endpoint, username, password, language, returnCode, startDate, endDate string, maxCount int, fieldName string) (*models.ReturnCodeResult, error) {
	soapXML := buildSaveReturnShipmentCodeXML(username, password, language, returnCode, startDate, endDate, maxCount, fieldName)

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

	var envelope returnCodeResponseEnvelope
	if err := xml.Unmarshal(body, &envelope); err != nil {
		return nil, fmt.Errorf("failed to parse response XML: %w", err)
	}

	result := &models.ReturnCodeResult{
		OutFlag:   envelope.Body.ReturnCodeResponse.ReturnCodeResult.OutFlag,
		OutResult: envelope.Body.ReturnCodeResponse.ReturnCodeResult.OutResult,
		ErrCode:   envelope.Body.ReturnCodeResponse.ReturnCodeResult.ErrCode,
	}

	return result, nil
}
