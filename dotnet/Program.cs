using YurticiKargo.Tests;

Console.WriteLine("╔══════════════════════════════════════════╗");
Console.WriteLine("║   Yurtiçi Kargo .NET API Client Tests    ║");
Console.WriteLine("╚══════════════════════════════════════════╝\n");

await CreateShipmentTest.RunAsync();
await CancelShipmentTest.RunAsync();
await QueryShipmentTest.RunAsync();
await SaveReturnShipmentCodeTest.RunAsync();

Console.WriteLine("All tests completed.");
