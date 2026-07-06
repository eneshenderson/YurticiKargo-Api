package models

// ShipmentOrder represents a shipment order to be created.
type ShipmentOrder struct {
	CargoKey           string  `xml:"cargoKey"`
	InvoiceKey         string  `xml:"invoiceKey"`
	ReceiverCustName   string  `xml:"receiverCustName"`
	ReceiverAddress    string  `xml:"receiverAddress"`
	ReceiverPhone1     string  `xml:"receiverPhone1"`
	ReceiverPhone2     string  `xml:"receiverPhone2,omitempty"`
	ReceiverPhone3     string  `xml:"receiverPhone3,omitempty"`
	CityName           string  `xml:"cityName,omitempty"`
	TownName           string  `xml:"townName,omitempty"`
	CustProdId         string  `xml:"custProdId,omitempty"`
	Desi               string  `xml:"desi,omitempty"`
	Kg                 string  `xml:"kg,omitempty"`
	CargoCount         int     `xml:"cargoCount,omitempty"`
	WaybillNo          string  `xml:"waybillNo,omitempty"`
	SpecialField1      string  `xml:"specialField1,omitempty"`
	SpecialField2      string  `xml:"specialField2,omitempty"`
	SpecialField3      string  `xml:"specialField3,omitempty"`
	TtCollectionType   string  `xml:"ttCollectionType,omitempty"`
	TtInvoiceAmount    string  `xml:"ttInvoiceAmount,omitempty"`
	TtDocumentId       string  `xml:"ttDocumentId,omitempty"`
	TtDocumentSaveType string  `xml:"ttDocumentSaveType,omitempty"`
	DcSelectedCredit   string  `xml:"dcSelectedCredit,omitempty"`
	DcCreditRule       string  `xml:"dcCreditRule,omitempty"`
	OrgReceiverCustId  string  `xml:"orgReceiverCustId,omitempty"`
	Description        string  `xml:"description,omitempty"`
	TaxNumber          string  `xml:"taxNumber,omitempty"`
	TaxOfficeId        string  `xml:"taxOfficeId,omitempty"`
	TaxOfficeName      string  `xml:"taxOfficeName,omitempty"`
	OrgGeoCode         string  `xml:"orgGeoCode,omitempty"`
	PrivilegeOrder     string  `xml:"privilegeOrder,omitempty"`
	EmailAddress       string  `xml:"emailAddress,omitempty"`
}

// ShipmentDetail represents the result detail for a single shipment.
type ShipmentDetail struct {
	CargoKey   string `xml:"cargoKey"`
	InvoiceKey string `xml:"invoiceKey"`
	ErrCode    int    `xml:"errCode"`
	ErrMessage string `xml:"errMessage"`
}

// ShipmentResult represents the response from createShipment.
type ShipmentResult struct {
	OutFlag   int              `xml:"outFlag"`
	OutResult string           `xml:"outResult"`
	JobId     int              `xml:"jobId"`
	Count     int              `xml:"count"`
	Details   []ShipmentDetail `xml:"shippingOrderDetailVO"`
}

// IsSuccess returns true if the operation was successful.
func (r *ShipmentResult) IsSuccess() bool {
	return r.OutFlag == 0
}

// GetErrors returns details with non-zero error codes.
func (r *ShipmentResult) GetErrors() []ShipmentDetail {
	var errors []ShipmentDetail
	for _, d := range r.Details {
		if d.ErrCode != 0 {
			errors = append(errors, d)
		}
	}
	return errors
}
