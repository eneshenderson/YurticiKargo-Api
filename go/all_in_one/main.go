package main

import (
	"bytes"
	"crypto/tls"
	"encoding/xml"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"
)

// ========== CONSTANTS ==========

const (
	TestEndpoint = "https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices"
	LiveEndpoint = "https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices"
	SOAPNs       = "http://yurticikargo.com.tr/ShippingOrderDispatcherServices"
)

// ========== MODELS ==========

type ShipmentOrder struct {
	CargoKey           string
	InvoiceKey         string
	ReceiverCustName   string
	ReceiverAddress    string
	ReceiverPhone1     string
	ReceiverPhone2     string
	ReceiverPhone3     string
	CityName           string
	TownName           string
	CustProdId         string
	Desi               string
	Kg                 string
	CargoCount         int
	WaybillNo          string
	SpecialField1      string
	SpecialField2      string
	SpecialField3      string
	TtCollectionType   string
	TtInvoiceAmount    string
	TtDocumentId       string
	TtDocumentSaveType string
	DcSelectedCredit   string
	DcCreditRule       string
	OrgReceiverCustId  string
	Description        string
	TaxNumber          string
	TaxOfficeId        string
	TaxOfficeName      string
	OrgGeoCode         string
	PrivilegeOrder     string
	EmailAddress       string
}

type ShipmentDetail struct {
	CargoKey   string
	InvoiceKey string
	ErrCode    int
	ErrMessage string
}

type ShipmentResult struct {
	OutFlag   int
	OutResult string
	JobId     int
	Count     int
	Details   []ShipmentDetail
}

func (r *ShipmentResult) IsSuccess() bool { return r.OutFlag == 0 }

type CancelDetail struct {
	CargoKey         string
	InvoiceKey       string
	JobId            int
	DocId            string
	OperationCode    int
	OperationMessage string
	OperationStatus  string
	ErrCode          int
	ErrMessage       string
}

type CancelResult struct {
	OutFlag      int
	OutResult    string
	SenderCustId int
	Count        int
	Details      []CancelDetail
}

func (r *CancelResult) IsSuccess() bool { return r.OutFlag == 0 }

type CargoEvent struct {
	UnitName   string
	EventName  string
	ReasonName string
	EventDate  string
	EventTime  string
	CityName   string
	TownName   string
}

type QueryItemDetail struct {
	TrackingUrl       string
	ReceiverCustName  string
	DepartureUnitName string
	DeliveryDate      string
	DeliveryTime      string
	CargoHistory      []CargoEvent
}

type QueryDetail struct {
	CargoKey         string
	InvoiceKey       string
	OperationStatus  string
	OperationMessage string
	ErrCode          int
	ErrMessage       string
	ItemDetail       *QueryItemDetail
}

func (d *QueryDetail) IsSuccess() bool { return d.ErrCode == 0 }

type QueryResult struct {
	OutFlag      int
	OutResult    string
	SenderCustId int
	Count        int
	Details      []QueryDetail
}

func (r *QueryResult) IsSuccess() bool { return r.OutFlag == 0 }

type ReturnCodeResult struct {
	OutFlag   int
	OutResult string
	ErrCode   int
}

func (r *ReturnCodeResult) IsSuccess() bool { return r.OutFlag == 0 }

// ========== CLIENT ==========

type YurticiKargoClient struct {
	Username   string
	Password   string
	Language   string
	TestMode   bool
	httpClient *http.Client
}

func NewYurticiKargoClient(username, password, language string, testMode bool) *YurticiKargoClient {
	transport := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
		},
	}
	return &YurticiKargoClient{
		Username:   username,
		Password:   password,
		Language:   language,
		TestMode:   testMode,
		httpClient: &http.Client{Transport: transport, Timeout: 30 * time.Second},
	}
}

func (c *YurticiKargoClient) GetEndpoint() string {
	if c.TestMode {
		return TestEndpoint
	}
	return LiveEndpoint
}

func (c *YurticiKargoClient) doRequest(soapXML string) ([]byte, error) {
	req, err := http.NewRequest("POST", c.GetEndpoint(), bytes.NewBufferString(soapXML))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}
	req.Header.Set("Content-Type", "text/xml; charset=utf-8")
	req.Header.Set("SOAPAction", "")

	resp, err := c.httpClient.Do(req)
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

	return body, nil
}

// ========== HELPERS ==========

func xmlEscape(s string) string {
	s = strings.ReplaceAll(s, "&", "&amp;")
	s = strings.ReplaceAll(s, "<", "&lt;")
	s = strings.ReplaceAll(s, ">", "&gt;")
	s = strings.ReplaceAll(s, "\"", "&quot;")
	s = strings.ReplaceAll(s, "'", "&apos;")
	return s
}

func boolToString(b bool) string {
	if b {
		return "1"
	}
	return "0"
}

// ========== CREATE SHIPMENT ==========

func (c *YurticiKargoClient) CreateShipment(shipments []ShipmentOrder) (*ShipmentResult, error) {
	var sb strings.Builder
	sb.WriteString(`<?xml version="1.0" encoding="UTF-8"?>`)
	sb.WriteString(`<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ship="` + SOAPNs + `">`)
	sb.WriteString(`<soapenv:Header/>`)
	sb.WriteString(`<soapenv:Body>`)
	sb.WriteString(`<ship:createShipment>`)
	sb.WriteString(fmt.Sprintf(`<wsUserName>%s</wsUserName>`, xmlEscape(c.Username)))
	sb.WriteString(fmt.Sprintf(`<wsPassword>%s</wsPassword>`, xmlEscape(c.Password)))
	sb.WriteString(fmt.Sprintf(`<userLanguage>%s</userLanguage>`, xmlEscape(c.Language)))
	for _, s := range shipments {
		sb.WriteString(`<ShippingOrderVO>`)
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
		sb.WriteString(`</ShippingOrderVO>`)
	}

	sb.WriteString(`</ship:createShipment>`)
	sb.WriteString(`</soapenv:Body>`)
	sb.WriteString(`</soapenv:Envelope>`)

	body, err := c.doRequest(sb.String())
	if err != nil {
		return nil, err
	}

	type shipmentDetailXML struct {
		CargoKey   string `xml:"cargoKey"`
		InvoiceKey string `xml:"invoiceKey"`
		ErrCode    int    `xml:"errCode"`
		ErrMessage string `xml:"errMessage"`
	}
	type envelope struct {
		XMLName xml.Name `xml:"Envelope"`
		Body    struct {
			Response struct {
				Result struct {
					OutFlag   int                 `xml:"outFlag"`
					OutResult string              `xml:"outResult"`
					JobId     int                 `xml:"jobId"`
					Count     int                 `xml:"count"`
					Details   []shipmentDetailXML `xml:"shippingOrderDetailVO"`
				} `xml:"ShippingOrderResultVO"`
			} `xml:"createShipmentResponse"`
		} `xml:"Body"`
	}

	var env envelope
	if err := xml.Unmarshal(body, &env); err != nil {
		return nil, fmt.Errorf("failed to parse response XML: %w", err)
	}

	result := &ShipmentResult{
		OutFlag:   env.Body.Response.Result.OutFlag,
		OutResult: env.Body.Response.Result.OutResult,
		JobId:     env.Body.Response.Result.JobId,
		Count:     env.Body.Response.Result.Count,
	}
	for _, d := range env.Body.Response.Result.Details {
		result.Details = append(result.Details, ShipmentDetail{
			CargoKey: d.CargoKey, InvoiceKey: d.InvoiceKey,
			ErrCode: d.ErrCode, ErrMessage: d.ErrMessage,
		})
	}
	return result, nil
}

// ========== CANCEL SHIPMENT ==========

func (c *YurticiKargoClient) CancelShipment(cargoKeys []string) (*CancelResult, error) {
	var sb strings.Builder
	sb.WriteString(`<?xml version="1.0" encoding="UTF-8"?>`)
	sb.WriteString(`<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ship="` + SOAPNs + `">`)
	sb.WriteString(`<soapenv:Header/>`)
	sb.WriteString(`<soapenv:Body>`)
	sb.WriteString(`<ship:cancelShipment>`)
	sb.WriteString(fmt.Sprintf(`<wsUserName>%s</wsUserName>`, xmlEscape(c.Username)))
	sb.WriteString(fmt.Sprintf(`<wsPassword>%s</wsPassword>`, xmlEscape(c.Password)))
	sb.WriteString(fmt.Sprintf(`<userLanguage>%s</userLanguage>`, xmlEscape(c.Language)))
	for _, key := range cargoKeys {
		sb.WriteString(fmt.Sprintf(`<cargoKeys>%s</cargoKeys>`, xmlEscape(key)))
	}
	sb.WriteString(`</ship:cancelShipment>`)
	sb.WriteString(`</soapenv:Body>`)
	sb.WriteString(`</soapenv:Envelope>`)

	body, err := c.doRequest(sb.String())
	if err != nil {
		return nil, err
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
	type envelope struct {
		XMLName xml.Name `xml:"Envelope"`
		Body    struct {
			Response struct {
				Result struct {
					OutFlag      int               `xml:"outFlag"`
					OutResult    string            `xml:"outResult"`
					SenderCustId int               `xml:"senderCustId"`
					Count        int               `xml:"count"`
					Details      []cancelDetailXML `xml:"cancelShipmentDetailVO"`
				} `xml:"cancelShipmentResultVO"`
			} `xml:"cancelShipmentResponse"`
		} `xml:"Body"`
	}

	var env envelope
	if err := xml.Unmarshal(body, &env); err != nil {
		return nil, fmt.Errorf("failed to parse response XML: %w", err)
	}

	result := &CancelResult{
		OutFlag:      env.Body.Response.Result.OutFlag,
		OutResult:    env.Body.Response.Result.OutResult,
		SenderCustId: env.Body.Response.Result.SenderCustId,
		Count:        env.Body.Response.Result.Count,
	}
	for _, d := range env.Body.Response.Result.Details {
		result.Details = append(result.Details, CancelDetail{
			CargoKey: d.CargoKey, InvoiceKey: d.InvoiceKey,
			JobId: d.JobId, DocId: d.DocId,
			OperationCode: d.OperationCode, OperationMessage: d.OperationMessage,
			OperationStatus: d.OperationStatus,
			ErrCode: d.ErrCode, ErrMessage: d.ErrMessage,
		})
	}
	return result, nil
}

// ========== QUERY SHIPMENT ==========

func (c *YurticiKargoClient) QueryShipment(keys []string, keyType int, addHistoricalData bool, onlyTracking bool) (*QueryResult, error) {
	var sb strings.Builder
	sb.WriteString(`<?xml version="1.0" encoding="UTF-8"?>`)
	sb.WriteString(`<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ship="` + SOAPNs + `">`)
	sb.WriteString(`<soapenv:Header/>`)
	sb.WriteString(`<soapenv:Body>`)
	sb.WriteString(`<ship:queryShipment>`)
	sb.WriteString(fmt.Sprintf(`<wsUserName>%s</wsUserName>`, xmlEscape(c.Username)))
	sb.WriteString(fmt.Sprintf(`<wsPassword>%s</wsPassword>`, xmlEscape(c.Password)))
	sb.WriteString(fmt.Sprintf(`<wsLanguage>%s</wsLanguage>`, xmlEscape(c.Language)))
	sb.WriteString(fmt.Sprintf(`<keys>%s</keys>`, xmlEscape(strings.Join(keys, ","))))
	sb.WriteString(fmt.Sprintf(`<keyType>%d</keyType>`, keyType))
	sb.WriteString(fmt.Sprintf(`<addHistoricalData>%s</addHistoricalData>`, boolToString(addHistoricalData)))
	sb.WriteString(fmt.Sprintf(`<onlyTracking>%s</onlyTracking>`, boolToString(onlyTracking)))
	sb.WriteString(`</ship:queryShipment>`)
	sb.WriteString(`</soapenv:Body>`)
	sb.WriteString(`</soapenv:Envelope>`)

	body, err := c.doRequest(sb.String())
	if err != nil {
		return nil, err
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
	type queryItemDetailXML struct {
		TrackingUrl       string          `xml:"trackingUrl"`
		ReceiverCustName  string          `xml:"receiverCustName"`
		DepartureUnitName string          `xml:"departureUnitName"`
		DeliveryDate      string          `xml:"deliveryDate"`
		DeliveryTime      string          `xml:"deliveryTime"`
		CargoHistory      []cargoEventXML `xml:"invDocCargoDAMVOArray>InvDocCargoDAMVO"`
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
	type envelope struct {
		XMLName xml.Name `xml:"Envelope"`
		Body    struct {
			Response struct {
				Result struct {
					OutFlag      int              `xml:"outFlag"`
					OutResult    string           `xml:"outResult"`
					SenderCustId int              `xml:"senderCustId"`
					Count        int              `xml:"count"`
					Details      []queryDetailXML `xml:"shippingDeliveryDetailVO"`
				} `xml:"ShippingDeliveryResultVO"`
			} `xml:"queryShipmentResponse"`
		} `xml:"Body"`
	}

	var env envelope
	if err := xml.Unmarshal(body, &env); err != nil {
		return nil, fmt.Errorf("failed to parse response XML: %w", err)
	}

	result := &QueryResult{
		OutFlag:      env.Body.Response.Result.OutFlag,
		OutResult:    env.Body.Response.Result.OutResult,
		SenderCustId: env.Body.Response.Result.SenderCustId,
		Count:        env.Body.Response.Result.Count,
	}
	for _, d := range env.Body.Response.Result.Details {
		detail := QueryDetail{
			CargoKey: d.CargoKey, InvoiceKey: d.InvoiceKey,
			OperationStatus: d.OperationStatus, OperationMessage: d.OperationMessage,
			ErrCode: d.ErrCode, ErrMessage: d.ErrMessage,
		}
		if d.ItemDetail != nil {
			item := &QueryItemDetail{
				TrackingUrl:       d.ItemDetail.TrackingUrl,
				ReceiverCustName:  d.ItemDetail.ReceiverCustName,
				DepartureUnitName: d.ItemDetail.DepartureUnitName,
				DeliveryDate:      d.ItemDetail.DeliveryDate,
				DeliveryTime:      d.ItemDetail.DeliveryTime,
			}
			for _, e := range d.ItemDetail.CargoHistory {
				item.CargoHistory = append(item.CargoHistory, CargoEvent{
					UnitName: e.UnitName, EventName: e.EventName,
					ReasonName: e.ReasonName, EventDate: e.EventDate,
					EventTime: e.EventTime, CityName: e.CityName, TownName: e.TownName,
				})
			}
			detail.ItemDetail = item
		}
		result.Details = append(result.Details, detail)
	}
	return result, nil
}

// ========== SAVE RETURN SHIPMENT CODE ==========

func (c *YurticiKargoClient) SaveReturnShipmentCode(returnCode, startDate, endDate string, maxCount int, fieldName string) (*ReturnCodeResult, error) {
	var sb strings.Builder
	sb.WriteString(`<?xml version="1.0" encoding="UTF-8"?>`)
	sb.WriteString(`<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ship="` + SOAPNs + `">`)
	sb.WriteString(`<soapenv:Header/>`)
	sb.WriteString(`<soapenv:Body>`)
	sb.WriteString(`<ship:saveReturnShipmentCode>`)
	sb.WriteString(fmt.Sprintf(`<wsUserName>%s</wsUserName>`, xmlEscape(c.Username)))
	sb.WriteString(fmt.Sprintf(`<wsPassword>%s</wsPassword>`, xmlEscape(c.Password)))
	sb.WriteString(fmt.Sprintf(`<wsLanguage>%s</wsLanguage>`, xmlEscape(c.Language)))
	sb.WriteString(fmt.Sprintf(`<fieldName>%s</fieldName>`, xmlEscape(fieldName)))
	sb.WriteString(fmt.Sprintf(`<returnCode>%s</returnCode>`, xmlEscape(returnCode)))
	sb.WriteString(fmt.Sprintf(`<startDate>%s</startDate>`, xmlEscape(startDate)))
	sb.WriteString(fmt.Sprintf(`<endDate>%s</endDate>`, xmlEscape(endDate)))
	sb.WriteString(fmt.Sprintf(`<maxCount>%d</maxCount>`, maxCount))
	sb.WriteString(`</ship:saveReturnShipmentCode>`)
	sb.WriteString(`</soapenv:Body>`)
	sb.WriteString(`</soapenv:Envelope>`)

	body, err := c.doRequest(sb.String())
	if err != nil {
		return nil, err
	}

	type envelope struct {
		XMLName xml.Name `xml:"Envelope"`
		Body    struct {
			Response struct {
				Result struct {
					OutFlag   int    `xml:"outFlag"`
					OutResult string `xml:"outResult"`
					ErrCode   int    `xml:"errCode"`
				} `xml:"saveReturnShipmentCodeResultVO"`
			} `xml:"saveReturnShipmentCodeResponse"`
		} `xml:"Body"`
	}

	var env envelope
	if err := xml.Unmarshal(body, &env); err != nil {
		return nil, fmt.Errorf("failed to parse response XML: %w", err)
	}

	return &ReturnCodeResult{
		OutFlag:   env.Body.Response.Result.OutFlag,
		OutResult: env.Body.Response.Result.OutResult,
		ErrCode:   env.Body.Response.Result.ErrCode,
	}, nil
}

// ========== MAIN ==========

func main() {
	client := NewYurticiKargoClient("YKTEST", "YK", "TR", true)

	fmt.Println("=== Yurtiçi Kargo Go API Client (All-in-One) ===")
	fmt.Printf("Endpoint: %s\n\n", client.GetEndpoint())

	// 1. Create Shipment
	fmt.Println("--- 1. CreateShipment ---")
	shipmentResult, err := client.CreateShipment([]ShipmentOrder{
		{
			CargoKey:         "ALLINONE001",
			InvoiceKey:       "AIOINV001",
			ReceiverCustName: "Mehmet Yılmaz",
			ReceiverAddress:  "Eski Büyükdere Cad. No:3",
			ReceiverPhone1:   "02123652426",
			CityName:         "İstanbul",
			TownName:         "Maslak",
		},
	})
	if err != nil {
		fmt.Printf("Error: %v\n", err)
	} else {
		fmt.Printf("OutFlag: %d, OutResult: %s, JobId: %d\n", shipmentResult.OutFlag, shipmentResult.OutResult, shipmentResult.JobId)
		for _, d := range shipmentResult.Details {
			fmt.Printf("  CargoKey: %s, ErrCode: %d, ErrMessage: %s\n", d.CargoKey, d.ErrCode, d.ErrMessage)
		}
	}
	fmt.Println()

	// 2. Query Shipment
	fmt.Println("--- 2. QueryShipment ---")
	queryResult, err := client.QueryShipment([]string{"ALLINONE001"}, 0, true, false)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
	} else {
		fmt.Printf("OutFlag: %d, OutResult: %s\n", queryResult.OutFlag, queryResult.OutResult)
		for _, d := range queryResult.Details {
			fmt.Printf("  CargoKey: %s, Status: %s, Message: %s\n", d.CargoKey, d.OperationStatus, d.OperationMessage)
			if d.ItemDetail != nil {
				fmt.Printf("    TrackingUrl: %s\n", d.ItemDetail.TrackingUrl)
				for _, event := range d.ItemDetail.CargoHistory {
					fmt.Printf("    → %s %s | %s | %s\n", event.EventDate, event.EventTime, event.UnitName, event.EventName)
				}
			}
		}
	}
	fmt.Println()

	// 3. Cancel Shipment
	fmt.Println("--- 3. CancelShipment ---")
	cancelResult, err := client.CancelShipment([]string{"ALLINONE001"})
	if err != nil {
		fmt.Printf("Error: %v\n", err)
	} else {
		fmt.Printf("OutFlag: %d, OutResult: %s\n", cancelResult.OutFlag, cancelResult.OutResult)
		for _, d := range cancelResult.Details {
			fmt.Printf("  CargoKey: %s, Status: %s, Message: %s\n", d.CargoKey, d.OperationStatus, d.OperationMessage)
		}
	}
	fmt.Println()

	// 4. Save Return Shipment Code
	fmt.Println("--- 4. SaveReturnShipmentCode ---")
	returnResult, err := client.SaveReturnShipmentCode("RMA-AIO-001", "20240101", "20240131", 1, "53")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
	} else {
		fmt.Printf("OutFlag: %d, OutResult: %s, ErrCode: %d\n", returnResult.OutFlag, returnResult.OutResult, returnResult.ErrCode)
	}

	fmt.Println("\n=== Complete ===")
	os.Exit(0)
}
