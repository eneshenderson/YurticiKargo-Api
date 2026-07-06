package models

// ReturnCodeResult represents the response from saveReturnShipmentCode.
type ReturnCodeResult struct {
	OutFlag   int    `xml:"outFlag"`
	OutResult string `xml:"outResult"`
	ErrCode   int    `xml:"errCode"`
}

// IsSuccess returns true if the operation was successful.
func (r *ReturnCodeResult) IsSuccess() bool {
	return r.OutFlag == 0
}
