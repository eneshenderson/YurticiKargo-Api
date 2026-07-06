package com.yurticikargo;

import com.yurticikargo.models.QueryResult;

/**
 * QueryShipment test — YKTEST ortamına bağlanır.
 *
 * Çalıştırma: java -cp out com.yurticikargo.QueryShipmentTest
 */
public class QueryShipmentTest {

    public static void main(String[] args) {
        System.out.println("=== QueryShipment Test ===\n");

        YurticiKargoClient client = new YurticiKargoClient("YKTEST", "YK", "TR", true);

        String[] keys = {"12520", "12521"};
        int keyType = 0; // 0=CargoKey
        boolean addHistoricalData = true;
        boolean onlyTracking = false;

        try {
            // Debug: SOAP XML'i görüntüle
            System.out.println("--- SOAP Request XML ---");
            System.out.println(client.getQueryShipmentRequestXml(keys, keyType, addHistoricalData, onlyTracking));
            System.out.println();

            // İsteği gönder
            QueryResult result = client.queryShipment(keys, keyType, addHistoricalData, onlyTracking);

            System.out.println("--- Sonuç ---");
            System.out.println("outFlag: " + result.getOutFlag());
            System.out.println("outResult: " + result.getOutResult());
            System.out.println("isSuccess: " + result.isSuccess());
            System.out.println();

            if (result.isSuccess()) {
                System.out.println("[PASS] queryShipment başarılı!");
            } else {
                System.out.println("[INFO] Yanıt alındı (outFlag=" + result.getOutFlag() + ")");
            }

            for (QueryResult.QueryDetail detail : result.getDetails()) {
                System.out.println("\n  cargoKey=" + detail.getCargoKey() +
                                 ", operationStatus=" + detail.getOperationStatus() +
                                 ", errCode=" + detail.getErrCode());

                if (detail.getItemDetail() != null) {
                    QueryResult.QueryItemDetail item = detail.getItemDetail();
                    System.out.println("    trackingUrl: " + item.getTrackingUrl());
                    System.out.println("    receiverCustName: " + item.getReceiverCustName());
                    System.out.println("    departureUnitName: " + item.getDepartureUnitName());
                    System.out.println("    deliveryDate: " + item.getDeliveryDate());

                    if (!item.getCargoHistory().isEmpty()) {
                        System.out.println("    --- Hareket Geçmişi ---");
                        for (QueryResult.CargoEvent event : item.getCargoHistory()) {
                            System.out.println("      " + event.getEventDate() + " " +
                                             event.getEventTime() + " | " +
                                             event.getUnitName() + " | " +
                                             event.getEventName());
                        }
                    }
                }
            }

        } catch (Exception e) {
            System.out.println("[FAIL] Exception: " + e.getMessage());
            e.printStackTrace();
        }

        System.out.println("\n=== Test Bitti ===");
    }
}
