package main

import (
	"fmt"
	"os"

	yurticikargo "github.com/yurticikargo/api-client"
	"github.com/yurticikargo/api-client/models"
)

func main() {
	// Create client in test mode
	client := yurticikargo.NewYurticiKargoClient("YKTEST", "YK", "TR", true)

	fmt.Println("=== Yurtiçi Kargo API Client Demo ===")
	fmt.Printf("Endpoint: %s\n\n", client.GetEndpoint())

	// 1. Create Shipment
	fmt.Println("--- 1. CreateShipment ---")
	shipmentResult, err := client.CreateShipment([]models.ShipmentOrder{
		{
			CargoKey:         "GOTEST001",
			InvoiceKey:       "GOINV001",
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
	queryResult, err := client.QueryShipment([]string{"GOTEST001"}, 0, true, false)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
	} else {
		fmt.Printf("OutFlag: %d, OutResult: %s\n", queryResult.OutFlag, queryResult.OutResult)
		for _, d := range queryResult.Details {
			fmt.Printf("  CargoKey: %s, Status: %s, Message: %s\n", d.CargoKey, d.OperationStatus, d.OperationMessage)
			if d.ItemDetail != nil {
				fmt.Printf("    TrackingUrl: %s\n", d.ItemDetail.TrackingUrl)
				fmt.Printf("    Receiver: %s\n", d.ItemDetail.ReceiverCustName)
				for _, event := range d.ItemDetail.CargoHistory {
					fmt.Printf("    → %s %s | %s | %s\n", event.EventDate, event.EventTime, event.UnitName, event.EventName)
				}
			}
		}
	}
	fmt.Println()

	// 3. Cancel Shipment
	fmt.Println("--- 3. CancelShipment ---")
	cancelResult, err := client.CancelShipment([]string{"GOTEST001"})
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
	returnResult, err := client.SaveReturnShipmentCode("RMA-GO-001", "20240101", "20240131", 1, "53")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
	} else {
		fmt.Printf("OutFlag: %d, OutResult: %s, ErrCode: %d\n", returnResult.OutFlag, returnResult.OutResult, returnResult.ErrCode)
	}

	fmt.Println("\n=== Demo Complete ===")
	os.Exit(0)
}
