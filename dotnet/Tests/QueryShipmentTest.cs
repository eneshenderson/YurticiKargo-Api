using YurticiKargo;
using YurticiKargo.Models;

namespace YurticiKargo.Tests;

public static class QueryShipmentTest
{
    public static async Task RunAsync()
    {
        Console.WriteLine("=== QueryShipment Test ===\n");

        using var client = new YurticiKargoClient(
            username: "YKTEST",
            password: "YK",
            language: "TR",
            testMode: true
        );

        var keys = new List<string> { "12520", "12521" };

        try
        {
            // Cargo Key ile sorgulama (keyType=0), hareket geçmişi dahil
            var result = await client.QueryShipmentAsync(
                keys: keys,
                keyType: 0,
                addHistoricalData: true,
                onlyTracking: false
            );

            Console.WriteLine($"OutFlag: {result.OutFlag}");
            Console.WriteLine($"OutResult: {result.OutResult}");
            Console.WriteLine($"Success: {result.IsSuccess()}");
            Console.WriteLine($"Count: {result.Count}");

            foreach (var detail in result.Details)
            {
                Console.WriteLine($"\n  CargoKey: {detail.CargoKey}");
                Console.WriteLine($"  Status: {detail.OperationStatus} ({detail.OperationCode})");
                Console.WriteLine($"  ErrCode: {detail.ErrCode} - {detail.ErrMessage}");

                if (detail.ItemDetail != null)
                {
                    var item = detail.ItemDetail;
                    Console.WriteLine($"  TrackingUrl: {item.TrackingUrl}");
                    Console.WriteLine($"  Receiver: {item.ReceiverCustName}");
                    Console.WriteLine($"  Departure: {item.DepartureUnitName}");
                    Console.WriteLine($"  Delivery: {item.DeliveryDate} {item.DeliveryTime}");

                    if (item.CargoHistory.Any())
                    {
                        Console.WriteLine("  History:");
                        foreach (var evt in item.CargoHistory)
                        {
                            Console.WriteLine($"    → {evt.EventDate} {evt.EventTime} | {evt.UnitName} | {evt.EventName} | {evt.ReasonName}");
                        }
                    }
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Exception: {ex.Message}");
        }

        Console.WriteLine();
    }
}
