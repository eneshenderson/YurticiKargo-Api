package yurticikargo

import (
	"crypto/tls"
	"net/http"
	"time"

	"github.com/yurticikargo/api-client/functions"
	"github.com/yurticikargo/api-client/models"
)

const (
	TestWSDL = "https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl"
	LiveWSDL = "https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl"
)

// YurticiKargoClient is the main client for Yurtiçi Kargo SOAP API.
type YurticiKargoClient struct {
	Username   string
	Password   string
	Language   string
	TestMode   bool
	httpClient *http.Client
}

// NewYurticiKargoClient creates a new client instance.
func NewYurticiKargoClient(username, password, language string, testMode bool) *YurticiKargoClient {
	transport := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
		},
	}

	client := &http.Client{
		Transport: transport,
		Timeout:   30 * time.Second,
	}

	return &YurticiKargoClient{
		Username:   username,
		Password:   password,
		Language:   language,
		TestMode:   testMode,
		httpClient: client,
	}
}

// GetEndpoint returns the SOAP endpoint URL based on test mode.
func (c *YurticiKargoClient) GetEndpoint() string {
	if c.TestMode {
		return TestWSDL
	}
	return LiveWSDL
}

// CreateShipment creates one or more shipments.
func (c *YurticiKargoClient) CreateShipment(shipments []models.ShipmentOrder) (*models.ShipmentResult, error) {
	return functions.CreateShipment(c.httpClient, c.GetEndpoint(), c.Username, c.Password, c.Language, shipments)
}

// CancelShipment cancels one or more shipments by cargo keys.
func (c *YurticiKargoClient) CancelShipment(cargoKeys []string) (*models.CancelResult, error) {
	return functions.CancelShipment(c.httpClient, c.GetEndpoint(), c.Username, c.Password, c.Language, cargoKeys)
}

// QueryShipment queries shipment status by keys.
func (c *YurticiKargoClient) QueryShipment(keys []string, keyType int, addHistoricalData bool, onlyTracking bool) (*models.QueryResult, error) {
	return functions.QueryShipment(c.httpClient, c.GetEndpoint(), c.Username, c.Password, c.Language, keys, keyType, addHistoricalData, onlyTracking)
}

// SaveReturnShipmentCode creates a return shipment code.
func (c *YurticiKargoClient) SaveReturnShipmentCode(returnCode, startDate, endDate string, maxCount int, fieldName string) (*models.ReturnCodeResult, error) {
	return functions.SaveReturnShipmentCode(c.httpClient, c.GetEndpoint(), c.Username, c.Password, c.Language, returnCode, startDate, endDate, maxCount, fieldName)
}
