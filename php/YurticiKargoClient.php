<?php
/**
 * Yurtiçi Kargo PHP API Client
 * 
 * Yurtiçi Kargo SOAP Web Service entegrasyonu için ana istemci sınıfı.
 * Tüm fonksiyonları birleştirir ve tek bir arayüz sunar.
 * 
 * @requires PHP 8.0+, ext-soap
 */

require_once __DIR__ . '/functions/CreateShipment.php';
require_once __DIR__ . '/functions/CancelShipment.php';
require_once __DIR__ . '/functions/QueryShipment.php';
require_once __DIR__ . '/functions/SaveReturnShipmentCode.php';

class YurticiKargoClient
{
    private const WSDL_TEST = 'https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl';
    private const WSDL_LIVE = 'https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl';

    private SoapClient $soapClient;
    private string $username;
    private string $password;
    private string $language;
    private bool $testMode;

    private CreateShipment $createShipmentService;
    private CancelShipment $cancelShipmentService;
    private QueryShipment $queryShipmentService;
    private SaveReturnShipmentCode $saveReturnShipmentCodeService;

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

        // Servisleri başlat
        $this->createShipmentService = new CreateShipment($this->soapClient, $this->username, $this->password, $this->language);
        $this->cancelShipmentService = new CancelShipment($this->soapClient, $this->username, $this->password, $this->language);
        $this->queryShipmentService = new QueryShipment($this->soapClient, $this->username, $this->password, $this->language);
        $this->saveReturnShipmentCodeService = new SaveReturnShipmentCode($this->soapClient, $this->username, $this->password, $this->language);
    }

    /**
     * Gönderi oluşturur.
     *
     * @param array $shipments Gönderi dizisi
     * @return object
     * @throws SoapFault|InvalidArgumentException
     */
    public function createShipment(array $shipments): object
    {
        return $this->createShipmentService->execute($shipments);
    }

    /**
     * Gönderileri iptal eder.
     *
     * @param array $cargoKeys İptal edilecek kargo anahtarları
     * @return object
     * @throws SoapFault|InvalidArgumentException
     */
    public function cancelShipment(array $cargoKeys): object
    {
        return $this->cancelShipmentService->execute($cargoKeys);
    }

    /**
     * Gönderi sorgulama yapar.
     *
     * @param array $keys Sorgulanacak anahtarlar
     * @param int $keyType 0=cargoKey, 1=invoiceKey
     * @param bool $addHistoricalData Hareket geçmişi dahil edilsin mi
     * @param bool $onlyTracking Sadece takip URL'si
     * @return object
     * @throws SoapFault|InvalidArgumentException
     */
    public function queryShipment(array $keys, int $keyType = 0, bool $addHistoricalData = false, bool $onlyTracking = false): object
    {
        return $this->queryShipmentService->execute($keys, $keyType, $addHistoricalData, $onlyTracking);
    }

    /**
     * İade kodu oluşturur.
     *
     * @param string $returnCode İade kodu
     * @param string $startDate Başlangıç tarihi (YYYYMMDD)
     * @param string $endDate Bitiş tarihi (YYYYMMDD)
     * @param int $maxCount Kullanım adedi
     * @param string|null $fieldName Özel alan (null ise test/canlı'ya göre otomatik atanır)
     * @return object
     * @throws SoapFault|InvalidArgumentException
     */
    public function saveReturnShipmentCode(string $returnCode, string $startDate, string $endDate, int $maxCount = 1, ?string $fieldName = null): object
    {
        if ($fieldName === null) {
            $fieldName = $this->testMode ? '53' : '16';
        }

        return $this->saveReturnShipmentCodeService->execute($returnCode, $startDate, $endDate, $maxCount, $fieldName);
    }

    // ─── Debug Metotları ───────────────────────────────────────────────────────

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
}
