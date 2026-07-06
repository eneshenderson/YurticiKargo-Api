using YurticiKargo;
using YurticiKargo.Models;

namespace YurticiKargo.Tests;

public static class CancelShipmentTest
{
    public static async Task RunAsync()
    {
        Console.WriteLine("=== CancelShipment Test ===\n");

        using var client = new YurticiKargoClient(
            username: "YKTEST",
            password: "YK",
            language: "TR",
            testMode: true
        );

        var cargoKeys = new List<string> { "0000113", "0000114" };

        try
        {
            var result = await client.CancelShipmentAsync(cargoKeys);

            Console.WriteLine($"OutFlag: {result.OutFlag}");
            Console.WriteLine($"OutResult: {result.OutResult}");
            Console.WriteLine($"SenderCustId: {result.SenderCustId}");
            Console.WriteLine($"Success: {result.IsSuccess()}");
            Console.WriteLine($"Count: {result.Count}");

            foreach (var detail in result.Details)
            {
                Console.WriteLine($"  CargoKey: {detail.CargoKey}");
                Console.WriteLine($"    Status: {detail.OperationStatus} ({detail.OperationCode})");
                Console.WriteLine($"    Message: {detail.OperationMessage}");
                Console.WriteLine($"    ErrCode: {detail.ErrCode} - {detail.ErrMessage}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Exception: {ex.Message}");
        }

        Console.WriteLine();
    }
}
