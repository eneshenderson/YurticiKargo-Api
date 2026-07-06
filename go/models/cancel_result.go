package models

// CancelDetail represents the result detail for a single cancel operation.
type CancelDetail struct {
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

// CancelResult represents the response from cancelShipment.
type CancelResult struct {
	OutFlag      int            `xml:"outFlag"`
	OutResult    string         `xml:"outResult"`
	SenderCustId int            `xml:"senderCustId"`
	Count        int            `xml:"count"`
	Details      []CancelDetail `xml:"cancelShipmentDetailVO"`
}

// IsSuccess returns true if the operation was successful.
func (r *CancelResult) IsSuccess() bool {
	return r.OutFlag == 0
}
