package models

// CargoEvent represents a single cargo history event.
type CargoEvent struct {
	UnitName   string `xml:"unitName"`
	EventName  string `xml:"eventName"`
	ReasonName string `xml:"reasonName"`
	EventDate  string `xml:"eventDate"`
	EventTime  string `xml:"eventTime"`
	CityName   string `xml:"cityName"`
	TownName   string `xml:"townName"`
}

// QueryItemDetail represents the detailed item information for a query.
type QueryItemDetail struct {
	TrackingUrl       string       `xml:"trackingUrl"`
	ReceiverCustName  string       `xml:"receiverCustName"`
	DepartureUnitName string       `xml:"departureUnitName"`
	DeliveryDate      string       `xml:"deliveryDate"`
	DeliveryTime      string       `xml:"deliveryTime"`
	CargoHistory      []CargoEvent `xml:"invDocCargoDAMVOArray>InvDocCargoDAMVO"`
}

// QueryDetail represents the result detail for a single query.
type QueryDetail struct {
	CargoKey         string           `xml:"cargoKey"`
	InvoiceKey       string           `xml:"invoiceKey"`
	OperationStatus  string           `xml:"operationStatus"`
	OperationMessage string           `xml:"operationMessage"`
	ErrCode          int              `xml:"errCode"`
	ErrMessage       string           `xml:"errMessage"`
	ItemDetail       *QueryItemDetail `xml:"invDocCargoVO"`
}

// IsSuccess returns true if this detail has no error.
func (d *QueryDetail) IsSuccess() bool {
	return d.ErrCode == 0
}

// QueryResult represents the response from queryShipment.
type QueryResult struct {
	OutFlag      int           `xml:"outFlag"`
	OutResult    string        `xml:"outResult"`
	SenderCustId int           `xml:"senderCustId"`
	Count        int           `xml:"count"`
	Details      []QueryDetail `xml:"shippingDeliveryDetailVO"`
}

// IsSuccess returns true if the operation was successful.
func (r *QueryResult) IsSuccess() bool {
	return r.OutFlag == 0
}
