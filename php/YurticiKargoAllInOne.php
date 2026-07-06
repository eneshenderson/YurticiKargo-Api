<?php
/**
 * Yurtiçi Kargo PHP API Client - All In One
 * 
 * Tek dosyada tüm fonksiyonları içeren bağımsız istemci.
 * Hiçbir external require gerektirmez.
 * 
 * @requires PHP 8.0+, ext-soap
 * @version 1.0.0
 * 
 * Kullanım:
 *   require_once 'YurticiKargoAllInOne.php';
 *   $client = new YurticiKargoAllInOne('YKTEST', 'YK', 'TR', true);
 */

class YurticiKargoAllInOne
{
    private const WSDL_TEST = 'https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl';
    private const WSDL_LIVE = 'https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl';

    private SoapClient $soapClient;
    private string $username;
    private string $password;
    private string $language;
    private bool $testMode;

    /** CancelShipment durum kodları */
    public const STATUS_NOP = 0; // İşlem yapılmadı
    public const STATUS_IND = 1; // Kargo teslimattadır
    public const STATUS_ISR = 2; // Düzenlenmiş, fatura prosedürü tamamlanmamış
    public const STATUS_CNL = 3; // Kargo çıkışı engellendi
    public const STATUS_ISC = 4; // Kargo zaten iptal edilmiş
    public const STATUS_DLV = 5; // Teslim edildi
    public const STATUS_BI  = 6; // YK acente tarafından iptal edildi

    /** QueryShipment key tipleri */
    public const KEY_TYPE_CARGO = 0;
    public const KEY_TYPE_INVOICE = 1;

    /**
     * @param string $username API kullanıcı adı
     * @param string $password API şifresi
     * @param string $language Dil (TR, EN)
     * @param bool $testMode Test ortamı mı?
     * @param array $soapOptions Ek SOAP istemci ayarları
     * @throws SoapFault
     */
    public function __construct(
        string $username,
        string $password,
        string $language = 'TR',
        bool $testMode = true,
        array $soapOptions = []
    ) {
        $this->username = $username;
        $this->password = $password;
        $this->language = $language;
        $this->testMode = $testMode;

        $wsdl = $testMode ? self::WSDL_TEST : self::WSDL_LIVE;

        $defaultOptions = [
            'trace' => true,
            'exceptions' => true,
            'encoding' => 'UTF-8',
            'soap_version' => SOAP_1_1,
            'connection_timeout' => 30,
            'location' => $testMode
                ? 'https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices'
                : 'https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices',
            'stream_context' => stream_context_create([
                'ssl' => [
                    'verify_peer' => false,
                    'verify_peer_name' => false,
                    'allow_self_signed' => true,
                ]
            ]),
        ];

        $options = array_merge($defaultOptions, $soapOptions);

        $this->soapClient = new SoapClient($wsdl, $options);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // createShipment - Gönderi Oluşturma
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * Gönderi oluşturur.
     *
     * @param array $shipments Gönderi dizisi. Her eleman şu zorunlu alanları içermelidir:
     *   - cargoKey (string, max 20): Benzersiz kargo anahtarı
     *   - invoiceKey (string, max 20): Fatura anahtarı
     *   - receiverCustName (string, max 100): Alıcı adı
     *   - receiverAddress (string, max 500): Alıcı adresi
     *   - receiverPhone1 (string, max 20): Alıcı telefon
     * 
     * Opsiyonel:
     *   receiverPhone2, receiverPhone3, cityName, townName, custProdId, desi, kg,
     *   cargoCount, waybillNo, specialField1, specialField2, specialField3,
     *   ttCollectionType, ttInvoiceAmount, ttDocumentId, ttDocumentSaveType,
     *   orgReceiverCustId, description, taxNumber, taxOfficeId, taxOfficeName,
     *   orgGeoCode, privilegeOrder, dcSelectedCredit, dcCreditRule, emailAddress
     *
     * @return object {outFlag, outResult, jobId, count, details[], isSuccess()}
     * @throws SoapFault|InvalidArgumentException
     */
    public function createShipment(array $shipments): object
    {
        if (empty($shipments)) {
            throw new \InvalidArgumentException('En az bir gönderi bilgisi gereklidir.');
        }

        $requiredFields = ['cargoKey', 'invoiceKey', 'receiverCustName', 'receiverAddress', 'receiverPhone1'];
        $optionalFields = [
            'receiverPhone2', 'receiverPhone3', 'cityName', 'townName',
            'custProdId', 'desi', 'kg', 'cargoCount', 'waybillNo',
            'specialField1', 'specialField2', 'specialField3',
            'ttCollectionType', 'ttInvoiceAmount', 'ttDocumentId', 'ttDocumentSaveType',
            'orgReceiverCustId', 'description', 'taxNumber', 'taxOfficeId', 'taxOfficeName',
            'orgGeoCode', 'privilegeOrder', 'dcSelectedCredit', 'dcCreditRule', 'emailAddress'
        ];

        $shippingOrderList = [];

        foreach ($shipments as $index => $shipment) {
            foreach ($requiredFields as $field) {
                if (empty($shipment[$field])) {
                    throw new \InvalidArgumentException("Gönderi #{$index}: '{$field}' alanı zorunludur.");
                }
            }

            $order = new \stdClass();
            $order->cargoKey = (string) $shipment['cargoKey'];
            $order->invoiceKey = (string) $shipment['invoiceKey'];
            $order->receiverCustName = (string) $shipment['receiverCustName'];
            $order->receiverAddress = (string) $shipment['receiverAddress'];
            $order->receiverPhone1 = (string) $shipment['receiverPhone1'];

            // Opsiyonel string alanlar - WSDL tüm property'leri bekler
            $optionalStringFields = [
                'receiverPhone2', 'receiverPhone3', 'cityName', 'townName',
                'custProdId', 'waybillNo',
                'specialField1', 'specialField2', 'specialField3',
                'ttCollectionType', 'ttDocumentId', 'ttDocumentSaveType',
                'orgReceiverCustId', 'description', 'taxNumber', 'taxOfficeName',
                'orgGeoCode', 'privilegeOrder', 'emailAddress'
            ];

            foreach ($optionalStringFields as $field) {
                $order->$field = isset($shipment[$field]) && $shipment[$field] !== ''
                    ? (string) $shipment[$field]
                    : '';
            }

            // Numeric alanlar
            $order->desi = isset($shipment['desi']) && $shipment['desi'] !== '' ? (float) $shipment['desi'] : 0;
            $order->kg = isset($shipment['kg']) && $shipment['kg'] !== '' ? (float) $shipment['kg'] : 0;
            $order->cargoCount = isset($shipment['cargoCount']) && $shipment['cargoCount'] !== '' ? (int) $shipment['cargoCount'] : 0;
            $order->ttInvoiceAmount = isset($shipment['ttInvoiceAmount']) && $shipment['ttInvoiceAmount'] !== '' ? (float) $shipment['ttInvoiceAmount'] : 0;
            $order->taxOfficeId = isset($shipment['taxOfficeId']) && $shipment['taxOfficeId'] !== '' ? (int) $shipment['taxOfficeId'] : 0;
            $order->dcSelectedCredit = isset($shipment['dcSelectedCredit']) && $shipment['dcSelectedCredit'] !== '' ? (int) $shipment['dcSelectedCredit'] : 0;
            $order->dcCreditRule = isset($shipment['dcCreditRule']) && $shipment['dcCreditRule'] !== '' ? (int) $shipment['dcCreditRule'] : 0;

            $shippingOrderList[] = $order;
        }

        $params = new \stdClass();
        $params->wsUserName = $this->username;
        $params->wsPassword = $this->password;
        $params->userLanguage = $this->language;
        $params->ShippingOrderVO = $shippingOrderList;

        $response = $this->soapClient->__soapCall('createShipment', [$params]);

        return $this->parseCreateShipmentResponse($response);
    }

    private function parseCreateShipmentResponse(object $response): object
    {
        $result = new \stdClass();
        $data = $response->ShippingOrderResultVO ?? $response;

        $result->outFlag = (int) ($data->outFlag ?? 2);
        $result->outResult = (string) ($data->outResult ?? '');
        $result->jobId = (int) ($data->jobId ?? 0);
        $result->count = (int) ($data->count ?? 0);
        $result->details = [];

        if (isset($data->shippingOrderDetailVO)) {
            $details = is_array($data->shippingOrderDetailVO)
                ? $data->shippingOrderDetailVO
                : [$data->shippingOrderDetailVO];

            foreach ($details as $detail) {
                $item = new \stdClass();
                $item->cargoKey = (string) ($detail->cargoKey ?? '');
                $item->invoiceKey = (string) ($detail->invoiceKey ?? '');
                $item->errCode = (int) ($detail->errCode ?? 0);
                $item->errMessage = (string) ($detail->errMessage ?? '');
                $result->details[] = $item;
            }
        }

        $result->isSuccess = fn() => $result->outFlag === 0;
        return $result;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // cancelShipment - Gönderi İptal
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * Gönderileri iptal eder.
     * Gönderi düzenlendikten sonra iptal yapılamaz.
     *
     * @param array $cargoKeys İptal edilecek kargo anahtarları
     * @return object {outFlag, outResult, senderCustId, count, details[], isSuccess()}
     * @throws SoapFault|InvalidArgumentException
     */
    public function cancelShipment(array $cargoKeys): object
    {
        if (empty($cargoKeys)) {
            throw new \InvalidArgumentException('En az bir kargo anahtarı gereklidir.');
        }

        $cargoKeysStr = implode(',', array_map('strval', $cargoKeys));

        $params = new \stdClass();
        $params->wsUserName = $this->username;
        $params->wsPassword = $this->password;
        $params->userLanguage = $this->language;
        $params->cargoKeys = $cargoKeysStr;

        $response = $this->soapClient->__soapCall('cancelShipment', [$params]);

        return $this->parseCancelShipmentResponse($response);
    }

    private function parseCancelShipmentResponse(object $response): object
    {
        $result = new \stdClass();
        $data = $response->ShippingOrderResultVO ?? $response;

        $result->outFlag = (int) ($data->outFlag ?? 2);
        $result->outResult = (string) ($data->outResult ?? '');
        $result->senderCustId = (int) ($data->senderCustId ?? 0);
        $result->count = (int) ($data->count ?? 0);
        $result->details = [];

        if (isset($data->shippingCancelDetailVO)) {
            $details = is_array($data->shippingCancelDetailVO)
                ? $data->shippingCancelDetailVO
                : [$data->shippingCancelDetailVO];

            foreach ($details as $detail) {
                $item = new \stdClass();
                $item->cargoKey = (string) ($detail->cargoKey ?? '');
                $item->invoiceKey = (string) ($detail->invoiceKey ?? '');
                $item->jobId = (int) ($detail->jobId ?? 0);
                $item->docId = (string) ($detail->docId ?? '');
                $item->operationCode = (int) ($detail->operationCode ?? 0);
                $item->operationMessage = (string) ($detail->operationMessage ?? '');
                $item->operationStatus = (string) ($detail->operationStatus ?? '');
                $item->errCode = (int) ($detail->errCode ?? 0);
                $item->errMessage = (string) ($detail->errMessage ?? '');
                $result->details[] = $item;
            }
        }

        $result->isSuccess = fn() => $result->outFlag === 0;
        return $result;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // queryShipment - Gönderi Sorgulama
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * Gönderi sorgulama yapar.
     *
     * @param array $keys Sorgulanacak anahtar değerleri
     * @param int $keyType 0=cargoKey, 1=invoiceKey
     * @param bool $addHistoricalData Hareket geçmişi dahil edilsin mi
     * @param bool $onlyTracking Sadece takip URL'si dönsün mü
     * @return object {outFlag, outResult, senderCustId, count, details[], isSuccess()}
     * @throws SoapFault|InvalidArgumentException
     */
    public function queryShipment(array $keys, int $keyType = 0, bool $addHistoricalData = false, bool $onlyTracking = false): object
    {
        if (empty($keys)) {
            throw new \InvalidArgumentException('En az bir anahtar değeri gereklidir.');
        }

        if (!in_array($keyType, [0, 1], true)) {
            throw new \InvalidArgumentException('keyType 0 (cargoKey) veya 1 (invoiceKey) olmalıdır.');
        }

        $keysStr = implode(',', array_map('strval', $keys));

        $params = new \stdClass();
        $params->wsUserName = $this->username;
        $params->wsPassword = $this->password;
        $params->wsLanguage = $this->language;
        $params->keys = $keysStr;
        $params->keyType = $keyType;
        $params->addHistoricalData = $addHistoricalData;
        $params->onlyTracking = $onlyTracking;

        $response = $this->soapClient->__soapCall('queryShipment', [$params]);

        return $this->parseQueryShipmentResponse($response);
    }

    private function parseQueryShipmentResponse(object $response): object
    {
        $result = new \stdClass();
        $data = $response->ShippingDeliveryVO ?? $response;

        $result->outFlag = (int) ($data->outFlag ?? 2);
        $result->outResult = (string) ($data->outResult ?? '');
        $result->senderCustId = (int) ($data->senderCustId ?? 0);
        $result->count = (int) ($data->count ?? 0);
        $result->details = [];

        if (isset($data->shippingDeliveryDetailVO)) {
            $details = is_array($data->shippingDeliveryDetailVO)
                ? $data->shippingDeliveryDetailVO
                : [$data->shippingDeliveryDetailVO];

            foreach ($details as $detail) {
                $item = new \stdClass();
                $item->cargoKey = (string) ($detail->cargoKey ?? '');
                $item->invoiceKey = (string) ($detail->invoiceKey ?? '');
                $item->jobId = (int) ($detail->jobId ?? 0);
                $item->docId = (string) ($detail->docId ?? '');
                $item->operationCode = (int) ($detail->operationCode ?? 0);
                $item->operationMessage = (string) ($detail->operationMessage ?? '');
                $item->operationStatus = (string) ($detail->operationStatus ?? '');
                $item->errCode = (int) ($detail->errCode ?? 0);
                $item->errMessage = (string) ($detail->errMessage ?? '');
                $item->itemDetail = null;

                if (isset($detail->shippingDeliveryItemDetailVO)) {
                    $itemDetail = $detail->shippingDeliveryItemDetailVO;
                    $item->itemDetail = new \stdClass();
                    $item->itemDetail->trackingUrl = (string) ($itemDetail->trackingUrl ?? '');
                    $item->itemDetail->receiverCustName = (string) ($itemDetail->receiverCustName ?? '');
                    $item->itemDetail->departureUnitName = (string) ($itemDetail->departureUnitName ?? '');
                    $item->itemDetail->deliveryDate = (string) ($itemDetail->deliveryDate ?? '');
                    $item->itemDetail->deliveryTime = (string) ($itemDetail->deliveryTime ?? '');
                    $item->itemDetail->totalDesi = (float) ($itemDetail->totalDesi ?? 0);
                    $item->itemDetail->cargoHistory = [];

                    if (isset($itemDetail->invDocCargoVOArray)) {
                        $events = is_array($itemDetail->invDocCargoVOArray)
                            ? $itemDetail->invDocCargoVOArray
                            : [$itemDetail->invDocCargoVOArray];

                        foreach ($events as $event) {
                            $item->itemDetail->cargoHistory[] = [
                                'unitName'   => (string) ($event->unitName ?? ''),
                                'eventName'  => (string) ($event->eventName ?? ''),
                                'reasonName' => (string) ($event->reasonName ?? ''),
                                'eventDate'  => (string) ($event->eventDate ?? ''),
                                'eventTime'  => (string) ($event->eventTime ?? ''),
                                'cityName'   => (string) ($event->cityName ?? ''),
                                'townName'   => (string) ($event->townName ?? ''),
                            ];
                        }
                    }
                }

                $item->isSuccess = fn() => $item->errCode === 0;
                $result->details[] = $item;
            }
        }

        $result->isSuccess = fn() => $result->outFlag === 0;
        return $result;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // saveReturnShipmentCode - İade Kodu Oluşturma
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * İade kodu oluşturur.
     *
     * @param string $returnCode Benzersiz iade kodu
     * @param string $startDate Geçerlilik başlangıç tarihi (YYYYMMDD)
     * @param string $endDate Geçerlilik bitiş tarihi (YYYYMMDD)
     * @param int $maxCount Kullanım adedi
     * @param string|null $fieldName Özel alan (null ise test/canlı'ya göre otomatik)
     * @return object {outFlag, outResult, errCode, isSuccess()}
     * @throws SoapFault|InvalidArgumentException
     */
    public function saveReturnShipmentCode(string $returnCode, string $startDate, string $endDate, int $maxCount = 1, ?string $fieldName = null): object
    {
        if (empty($returnCode)) {
            throw new \InvalidArgumentException('returnCode boş olamaz.');
        }

        if (!preg_match('/^\d{8}$/', $startDate)) {
            throw new \InvalidArgumentException('startDate YYYYMMDD formatında olmalıdır.');
        }

        if (!preg_match('/^\d{8}$/', $endDate)) {
            throw new \InvalidArgumentException('endDate YYYYMMDD formatında olmalıdır.');
        }

        if ($maxCount < 1) {
            throw new \InvalidArgumentException('maxCount en az 1 olmalıdır.');
        }

        if ($fieldName === null) {
            $fieldName = $this->testMode ? '53' : '16';
        }

        if (empty($fieldName)) {
            throw new \InvalidArgumentException('fieldName boş olamaz.');
        }

        $params = new \stdClass();
        $params->wsUserName = $this->username;
        $params->wsPassword = $this->password;
        $params->wsLanguage = $this->language;
        $params->returnCode = $returnCode;
        $params->startDate = $startDate;
        $params->endDate = $endDate;
        $params->maxCount = $maxCount;
        $params->fieldName = $fieldName;

        $response = $this->soapClient->__soapCall('saveReturnShipmentCode', [$params]);

        return $this->parseSaveReturnShipmentCodeResponse($response);
    }

    private function parseSaveReturnShipmentCodeResponse(object $response): object
    {
        $result = new \stdClass();
        $data = $response->ExtendedBaseResultVO ?? $response;

        $result->outFlag = (int) ($data->outFlag ?? 2);
        $result->outResult = (string) ($data->outResult ?? '');
        $result->errCode = (int) ($data->errCode ?? 0);

        $result->isSuccess = fn() => $result->outFlag === 0;
        return $result;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Debug & Utility Metotları
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * Son SOAP isteğini döndürür.
     */
    public function getLastRequest(): ?string
    {
        return $this->soapClient->__getLastRequest();
    }

    /**
     * Son SOAP yanıtını döndürür.
     */
    public function getLastResponse(): ?string
    {
        return $this->soapClient->__getLastResponse();
    }

    /**
     * SOAP servisinin desteklediği fonksiyonları listeler.
     */
    public function getFunctions(): array
    {
        return $this->soapClient->__getFunctions();
    }

    /**
     * SOAP servisinin desteklediği tipleri listeler.
     */
    public function getTypes(): array
    {
        return $this->soapClient->__getTypes();
    }

    /**
     * Test modunda mı çalışıyor?
     */
    public function isTestMode(): bool
    {
        return $this->testMode;
    }

    /**
     * Kullanılan WSDL URL'sini döndürür.
     */
    public function getWsdlUrl(): string
    {
        return $this->testMode ? self::WSDL_TEST : self::WSDL_LIVE;
    }

    /**
     * Operasyon durum kodunun açıklamasını döndürür.
     */
    public static function getStatusDescription(int $code): string
    {
        return match ($code) {
            self::STATUS_NOP => 'İşlem yapılmadı, düzenlenmemiş',
            self::STATUS_IND => 'Kargo teslimattadır',
            self::STATUS_ISR => 'Düzenlenmiş, fatura prosedürü tamamlanmamış',
            self::STATUS_CNL => 'Kargo çıkışı engellendi',
            self::STATUS_ISC => 'Kargo zaten iptal edilmiş',
            self::STATUS_DLV => 'Teslim edildi',
            self::STATUS_BI  => 'YK acente tarafından iptal edildi',
            default => 'Bilinmeyen durum kodu',
        };
    }
}

// ═════════════════════════════════════════════════════════════════════════════════
// KULLANIM ÖRNEKLERİ (Bu kısım doğrudan çalıştırıldığında demo olarak çalışır)
// ═════════════════════════════════════════════════════════════════════════════════

if (php_sapi_name() === 'cli' && realpath($argv[0] ?? '') === realpath(__FILE__)) {
    echo "╔══════════════════════════════════════════════════════════════╗\n";
    echo "║  Yurtiçi Kargo PHP API Client - All In One Demo            ║\n";
    echo "╚══════════════════════════════════════════════════════════════╝\n\n";

    try {
        $client = new YurticiKargoAllInOne(
            username: 'YKTEST',
            password: 'YK',
            language: 'TR',
            testMode: true
        );

        echo "[OK] Test ortamına bağlantı kuruldu.\n";
        echo "WSDL: {$client->getWsdlUrl()}\n\n";

        // 1. Gönderi Oluşturma
        echo "━━━ 1. createShipment ━━━\n";
        $cargoKey = 'DEMO' . time();
        $result = $client->createShipment([
            [
                'cargoKey'         => $cargoKey,
                'invoiceKey'       => 'DINV' . time(),
                'receiverCustName' => 'Demo Alıcı',
                'receiverAddress'  => 'Maslak Mah. Büyükdere Cad. No:3 Sarıyer/İstanbul',
                'receiverPhone1'   => '02123652426',
                'cityName'         => 'İstanbul',
                'townName'         => 'Sarıyer',
            ]
        ]);
        echo "  outFlag: {$result->outFlag} | outResult: {$result->outResult}\n";
        echo "  jobId: {$result->jobId} | Başarılı: " . (($result->isSuccess)() ? 'Evet' : 'Hayır') . "\n";
        foreach ($result->details as $d) {
            echo "  → cargoKey={$d->cargoKey}, errCode={$d->errCode}, msg={$d->errMessage}\n";
        }

        // 2. Gönderi Sorgulama
        echo "\n━━━ 2. queryShipment ━━━\n";
        $qResult = $client->queryShipment(keys: [$cargoKey], keyType: 0, addHistoricalData: true);
        echo "  outFlag: {$qResult->outFlag} | outResult: {$qResult->outResult}\n";
        foreach ($qResult->details as $d) {
            echo "  → cargoKey={$d->cargoKey}, status={$d->operationStatus}, msg={$d->operationMessage}\n";
        }

        // 3. Gönderi İptali
        echo "\n━━━ 3. cancelShipment ━━━\n";
        $cResult = $client->cancelShipment([$cargoKey]);
        echo "  outFlag: {$cResult->outFlag} | outResult: {$cResult->outResult}\n";
        foreach ($cResult->details as $d) {
            echo "  → cargoKey={$d->cargoKey}, status={$d->operationStatus}, msg={$d->operationMessage}\n";
            echo "    Açıklama: " . YurticiKargoAllInOne::getStatusDescription($d->operationCode) . "\n";
        }

        // 4. İade Kodu Oluşturma
        echo "\n━━━ 4. saveReturnShipmentCode ━━━\n";
        $rResult = $client->saveReturnShipmentCode(
            returnCode: 'RMA-DEMO-' . time(),
            startDate: date('Ymd'),
            endDate: date('Ymd', strtotime('+30 days')),
            maxCount: 1
        );
        echo "  outFlag: {$rResult->outFlag} | outResult: {$rResult->outResult} | errCode: {$rResult->errCode}\n";
        echo "  Başarılı: " . (($rResult->isSuccess)() ? 'Evet' : 'Hayır') . "\n";

        echo "\n[DONE] Demo tamamlandı.\n";

    } catch (SoapFault $e) {
        echo "[SOAP ERROR] {$e->getMessage()}\n";
    } catch (\Exception $e) {
        echo "[ERROR] {$e->getMessage()}\n";
    }
}
