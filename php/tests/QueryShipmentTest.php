<?php
/**
 * QueryShipment Test
 * 
 * Yurtiçi Kargo test ortamına bağlanarak gönderi sorgulama testi yapar.
 * 
 * Çalıştırma: php tests/QueryShipmentTest.php
 */

require_once __DIR__ . '/../YurticiKargoClient.php';

echo "=== QueryShipment Test ===\n\n";

try {
    $client = new YurticiKargoClient(
        username: 'YKTEST',
        password: 'YK',
        language: 'TR',
        testMode: true
    );

    echo "[OK] SOAP bağlantısı kuruldu.\n";

    // Önce sorgulayacağımız bir gönderi oluştur
    echo "\n--- Ön Hazırlık: Gönderi Oluşturma ---\n";

    $cargoKey = 'QRY' . time();
    $invoiceKey = 'QINV' . time();

    $createResult = $client->createShipment([
        [
            'cargoKey'         => $cargoKey,
            'invoiceKey'       => $invoiceKey,
            'receiverCustName' => 'Sorgu Test Alıcı',
            'receiverAddress'  => 'Maslak Mahallesi Büyükdere Cad. No:5',
            'receiverPhone1'   => '02123652426',
            'cityName'         => 'İstanbul',
            'townName'         => 'Sarıyer',
        ]
    ]);

    echo "Gönderi oluşturma - outFlag: {$createResult->outFlag}, outResult: {$createResult->outResult}\n";

    // Test 1: Cargo Key ile sorgulama
    echo "\n--- Test 1: Cargo Key ile Sorgulama ---\n";

    $result = $client->queryShipment(
        keys: [$cargoKey],
        keyType: 0,
        addHistoricalData: true,
        onlyTracking: false
    );

    echo "outFlag: {$result->outFlag}\n";
    echo "outResult: {$result->outResult}\n";
    echo "count: {$result->count}\n";

    if (($result->isSuccess)()) {
        echo "[PASS] Sorgulama başarılı.\n";
    } else {
        echo "[INFO] outFlag={$result->outFlag}: {$result->outResult}\n";
    }

    if (!empty($result->details)) {
        foreach ($result->details as $detail) {
            echo "  - cargoKey: {$detail->cargoKey}\n";
            echo "    operationStatus: {$detail->operationStatus}\n";
            echo "    operationMessage: {$detail->operationMessage}\n";
            echo "    Açıklama: " . QueryShipment::getStatusDescription($detail->operationCode) . "\n";

            if ($detail->itemDetail) {
                $item = $detail->itemDetail;
                echo "    trackingUrl: {$item->trackingUrl}\n";
                echo "    receiverCustName: {$item->receiverCustName}\n";
                echo "    departureUnitName: {$item->departureUnitName}\n";
                echo "    deliveryDate: {$item->deliveryDate}\n";
                echo "    totalDesi: {$item->totalDesi}\n";

                if (!empty($item->cargoHistory)) {
                    echo "    Hareket Geçmişi:\n";
                    foreach ($item->cargoHistory as $event) {
                        echo "      → {$event['eventDate']} {$event['eventTime']} | {$event['unitName']} | {$event['eventName']}\n";
                    }
                }
            }
        }
    }

    // Test 2: Invoice Key ile sorgulama
    echo "\n--- Test 2: Invoice Key ile Sorgulama ---\n";

    $result2 = $client->queryShipment(
        keys: [$invoiceKey],
        keyType: 1
    );

    echo "outFlag: {$result2->outFlag}\n";
    echo "outResult: {$result2->outResult}\n";

    if (($result2->isSuccess)()) {
        echo "[PASS] Invoice Key sorgulama başarılı.\n";
    } else {
        echo "[INFO] outFlag={$result2->outFlag}: {$result2->outResult}\n";
    }

    // Test 3: Mevcut olmayan anahtar
    echo "\n--- Test 3: Mevcut Olmayan Anahtar ---\n";

    $result3 = $client->queryShipment(
        keys: ['NONEXIST_' . time()],
        keyType: 0
    );

    echo "outFlag: {$result3->outFlag}\n";
    echo "outResult: {$result3->outResult}\n";

    if (!empty($result3->details)) {
        foreach ($result3->details as $detail) {
            echo "  - cargoKey: {$detail->cargoKey}, errCode: {$detail->errCode}, errMessage: {$detail->errMessage}\n";
        }
    }

    // Test 4: Validasyon
    echo "\n--- Test 4: Validasyon (Boş Keys) ---\n";

    try {
        $client->queryShipment(keys: [], keyType: 0);
        echo "[FAIL] Hata beklendi ama alınmadı.\n";
    } catch (\InvalidArgumentException $e) {
        echo "[PASS] Doğru hata yakalandı: {$e->getMessage()}\n";
    }

    // Test 5: Geçersiz keyType
    echo "\n--- Test 5: Geçersiz keyType ---\n";

    try {
        $client->queryShipment(keys: ['test'], keyType: 5);
        echo "[FAIL] Hata beklendi ama alınmadı.\n";
    } catch (\InvalidArgumentException $e) {
        echo "[PASS] Doğru hata yakalandı: {$e->getMessage()}\n";
    }

} catch (SoapFault $e) {
    echo "[ERROR] SOAP Hatası: {$e->getMessage()}\n";
} catch (\Exception $e) {
    echo "[ERROR] Genel Hata: {$e->getMessage()}\n";
}

echo "\n=== Test Tamamlandı ===\n";
