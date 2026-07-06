using YurticiKargo;
using YurticiKargo.Models;

namespace YurticiKargo.Tests;

public static class CreateShipmentTest
{
    public static async Task RunAsync()
    {
        Console.WriteLine("=== CreateShipment Test ===\n");

        using var client = new YurticiKargoClient(
            username: "YKTEST",
            password: "YK",
            language: "TR",
            testMode: true
        );

        var shipments = new List<Dictionary<string, string>>
        {
            new Dictionary<string, string>
            {
                ["cargoKey"] = "TEST" + DateTime.Now.Ticks.ToString()[^8..],
                ["invoiceKey"] = "INV" + DateTime.Now.Ticks.ToString()[^8..],
                ["receiverCustName"] = "Mehmet Yılmaz",
                ["receiverAddress"] = "Eski Büyükdere Cad. No:3 Maslak İstanbul",
                ["receiverPhone1"] = "02123652426",
                ["cityName"] = "İstanbul",
                ["townName"] = "Maslak"
            }
        };

        try
        {
            var result = await client.CreateShipmentAsync(shipments);

            Console.WriteLine($"OutFlag: {result.OutFlag}");
            Console.WriteLine($"OutResult: {result.OutResult}");
            Console.WriteLine($"JobId: {result.JobId}");
            Console.WriteLine($"Success: {result.IsSuccess()}");
            Console.WriteLine($"Count: {result.Count}");

            foreach (var detail in result.Details)
            {
                Console.WriteLine($"  CargoKey: {detail.CargoKey}, ErrCode: {detail.ErrCode}, Msg: {detail.ErrMessage}");
            }

            if (result.GetErrors().Any())
            {
                Console.WriteLine("\nErrors:");
                foreach (var err in result.GetErrors())
                {
                    Console.WriteLine($"  [{err.ErrCode}] {err.ErrMessage}");
                }
            }

            Console.WriteLine("\n--- SOAP Request ---");
            Console.WriteLine(client.GetLastRequest()[..Math.Min(500, client.GetLastRequest().Length)] + "...");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Exception: {ex.Message}");
        }

        Console.WriteLine();
    }
}
