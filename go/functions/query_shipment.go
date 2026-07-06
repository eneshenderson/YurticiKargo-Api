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

// buildQueryShipmentXML builds the SOAP XML for queryShipment (deliveryReportShipment).
func buildQueryShipmentXML(username, password, language string, keys []string, keyType int, addHistoricalData bool, onlyTracking bool) string {
	var sb strings.Builder

	sb.WriteString(`<?xml version="1.0" encoding="UTF-8"?>`)
	sb.WriteString(`<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ship="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">`)
	sb.WriteString(`<soapenv:Header/>`)
	sb.WriteString(`<soapenv:Body>`)
	sb.WriteString(`<ship:deliveryReportShipment>`)
	sb.WriteString(fmt.Sprintf(`<wsUserName>%s</wsUserName>`, xmlEscape(username)))
	sb.WriteString(fmt.Sprintf(`<wsPassword>%s</wsPassword>`, xmlEscape(password)))
	sb.WriteString(fmt.Sprintf(`<wsLanguage>%s</wsLanguage>`, xmlEscape(language)))
	sb.WriteString(fmt.Sprintf(`<keys>%s</keys>`, xmlEscape(strings.Join(keys, ","))))
	sb.WriteString(fmt.Sprintf(`<keyType>%d</keyType>`, keyType))
	sb.WriteString(fmt.Sprintf(`<addHistoricalData>%s</addHistoricalData>`, boolToString(addHistoricalData)))
	sb.WriteString(fmt.Sprintf(`<onlyTracking>%s</onlyTracking>`, boolToString(onlyTracking)))
	sb.WriteString(`</ship:deliveryReportShipment>`)
	sb.WriteString(`</soapenv:Body>`)
	sb.WriteString(`</soapenv:Envelope>`)

	return sb.String()
}

// queryResponseEnvelope is used for XML parsing of the SOAP response.
type queryResponseEnvelope struct {
	XMLName xml.Name        `xml:"Envelope"`
	Body    queryResponseBody `xml:"Body"`
}

type queryResponseBody struct {
	QueryResponse deliveryReportResponse `xml:"deliveryReportShipmentResponse"`
}

type deliveryReportResponse struct {
	QueryResult queryResultXML `xml:"ShippingDeliveryResultVO"`
}

type queryResultXML struct {
	OutFlag      int              `xml:"outFlag"`
	OutResult    string           `xml:"outResult"`
	SenderCustId int              `xml:"senderCustId"`
	Count        int              `xml:"count"`
	Details      []queryDetailXML `xml:"shippingDeliveryDetailVO"`
}

type queryDetailXML struct {
	CargoKey         string              `xml:"cargoKey"`
	InvoiceKey       string              `xml:"invoiceKey"`
	OperationStatus  string              `xml:"operationStatus"`
	OperationMessage string              `xml:"operationMessage"`
	ErrCode          int                 `xml:"errCode"`
	ErrMessage       string              `xml:"errMessage"`
	ItemDetail       *queryItemDetailXML `xml:"invDocCargoVO"`
}

type queryItemDetailXML struct {
	TrackingUrl       string          `xml:"trackingUrl"`
	ReceiverCustName  string          `xml:"receiverCustName"`
	DepartureUnitName string          `xml:"departureUnitName"`
	DeliveryDate      string          `xml:"deliveryDate"`
	DeliveryTime      string          `xml:"deliveryTime"`
	CargoHistory      []cargoEventXML `xml:"invDocCargoDAMVOArray>InvDocCargoDAMVO"`
}

type cargoEventXML struct {
	UnitName   string `xml:"unitName"`
	EventName  string `xml:"eventName"`
	ReasonName string `xml:"reasonName"`
	EventDate  string `xml:"eventDate"`
	EventTime  string `xml:"eventTime"`
	CityName   string `xml:"cityName"`
	TownName   string `xml:"townName"`
}

// QueryShipment sends a query shipment SOAP request and returns the result.
func QueryShipment(client *http.Client, endpoint, username, password, language string, keys []string, keyType int, addHistoricalData bool, onlyTracking bool) (*models.QueryResult, error) {
	soapXML := buildQueryShipmentXML(username, password, language, keys, keyType, addHistoricalData, onlyTracking)

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

	var envelope queryResponseEnvelope
	if err := xml.Unmarshal(body, &envelope); err != nil {
		return nil, fmt.Errorf("failed to parse response XML: %w", err)
	}

	result := &models.QueryResult{
		OutFlag:      envelope.Body.QueryResponse.QueryResult.OutFlag,
		OutResult:    envelope.Body.QueryResponse.QueryResult.OutResult,
		SenderCustId: envelope.Body.QueryResponse.QueryResult.SenderCustId,
		Count:        envelope.Body.QueryResponse.QueryResult.Count,
	}

	for _, d := range envelope.Body.QueryResponse.QueryResult.Details {
		detail := models.QueryDetail{
			CargoKey:         d.CargoKey,
			InvoiceKey:       d.InvoiceKey,
			OperationStatus:  d.OperationStatus,
			OperationMessage: d.OperationMessage,
			ErrCode:          d.ErrCode,
			ErrMessage:       d.ErrMessage,
		}

		if d.ItemDetail != nil {
			itemDetail := &models.QueryItemDetail{
				TrackingUrl:       d.ItemDetail.TrackingUrl,
				ReceiverCustName:  d.ItemDetail.ReceiverCustName,
				DepartureUnitName: d.ItemDetail.DepartureUnitName,
				DeliveryDate:      d.ItemDetail.DeliveryDate,
				DeliveryTime:      d.ItemDetail.DeliveryTime,
			}

			for _, e := range d.ItemDetail.CargoHistory {
				itemDetail.CargoHistory = append(itemDetail.CargoHistory, models.CargoEvent{
					UnitName:   e.UnitName,
					EventName:  e.EventName,
					ReasonName: e.ReasonName,
					EventDate:  e.EventDate,
					EventTime:  e.EventTime,
					CityName:   e.CityName,
					TownName:   e.TownName,
				})
			}

			detail.ItemDetail = itemDetail
		}

		result.Details = append(result.Details, detail)
	}

	return result, nil
}
