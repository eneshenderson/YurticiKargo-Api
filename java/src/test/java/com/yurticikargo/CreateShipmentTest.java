package com.yurticikargo;

import com.yurticikargo.models.ShipmentResult;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * CreateShipment test — YKTEST ortamına bağlanır.
 *
 * Çalıştırma: java -cp out com.yurticikargo.CreateShipmentTest
 */
public class CreateShipmentTest {

    public static void main(String[] args) {
        System.out.println("=== CreateShipment Test ===\n");

        YurticiKargoClient client = new YurticiKargoClient("YKTEST", "YK", "TR", true);

        // Benzersiz cargo key oluştur (timestamp ile)
        String uniqueKey = "TEST" + System.currentTimeMillis() % 100000;

        Map<String, String> shipment = new HashMap<>();
        shipment.put("cargoKey", uniqueKey);
        shipment.put("invoiceKey", "INV" + uniqueKey);
        shipment.put("receiverCustName", "Test Alıcı");
        shipment.put("receiverAddress", "Eski Büyükdere Cad. No:3 Maslak İstanbul");
        shipment.put("receiverPhone1", "02123652426");
        shipment.put("cityName", "İstanbul");
        shipment.put("townName", "Maslak");

        try {
            // Debug: SOAP XML'i görüntüle
            System.out.println("--- SOAP Request XML ---");
            System.out.println(client.getCreateShipmentRequestXml(List.of(shipment)));
            System.out.println();

            // İsteği gönder
            ShipmentResult result = client.createShipment(List.of(shipment));

            System.out.println("--- Sonuç ---");
            System.out.println("outFlag: " + result.getOutFlag());
            System.out.println("outResult: " + result.getOutResult());
            System.out.println("jobId: " + result.getJobId());
            System.out.println("count: " + result.getCount());
            System.out.println("isSuccess: " + result.isSuccess());
            System.out.println();

            if (result.isSuccess()) {
                System.out.println("[PASS] createShipment başarılı!");
                for (ShipmentResult.ShipmentDetail detail : result.getDetails()) {
                    System.out.println("  cargoKey=" + detail.getCargoKey() +
                                     ", invoiceKey=" + detail.getInvoiceKey() +
                                     ", errCode=" + detail.getErrCode() +
                                     ", errMessage=" + detail.getErrMessage());
                }
            } else {
                System.out.println("[INFO] Yanıt alındı (outFlag=" + result.getOutFlag() + ")");
                System.out.println("  " + result.getOutResult());
                for (ShipmentResult.ShipmentDetail detail : result.getDetails()) {
                    System.out.println("  [" + detail.getErrCode() + "] " + detail.getErrMessage());
                }
            }

        } catch (Exception e) {
            System.out.println("[FAIL] Exception: " + e.getMessage());
            e.printStackTrace();
        }

        System.out.println("\n=== Test Bitti ===");
    }
}
