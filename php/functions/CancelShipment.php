<?php
/**
 * Yurtiçi Kargo - CancelShipment (Gönderi İptal)
 * 
 * Web servis ile sisteme gönderilmiş bilgilerin iptal edilmesini sağlar.
 * Gönderi düzenlendikten sonra iptal yapılamaz.
 * 
 * @requires PHP 8.0+, ext-soap
 */

class CancelShipment
{
    private SoapClient $soapClient;
    private string $username;
    private string $password;
    private string $language;

    /** Durum kodları */
    public const STATUS_NOP = 0; // İşlem yapılmadı
    public const STATUS_IND = 1; // Kargo teslimattadır
    public const STATUS_ISR = 2; // Düzenlenmiş, fatura prosedürü tamamlanmamış
    public const STATUS_CNL = 3; // Kargo çıkışı engellendi (başarılı iptal)
    public const STATUS_ISC = 4; // Kargo zaten iptal edilmiş
    public const STATUS_DLV = 5; // Teslim edildi
    public const STATUS_BI  = 6; // YK acente tarafından iptal edildi

    public function __construct(SoapClient $soapClient, string $username, string $password, string $language = 'TR')
    {
        $this->soapClient = $soapClient;
        $this->username = $username;
        $this->password = $password;
        $this->language = $language;
    }

    /**
     * Gönderileri iptal eder.
     *
     * @param array $cargoKeys İptal edilecek kargo anahtarları dizisi
     * @return object Response object with outFlag, outResult, senderCustId, count, details
     * @throws SoapFault
     * @throws InvalidArgumentException
     */
    public function execute(array $cargoKeys): object
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

        return $this->parseResponse($response);
    }

    /**
     * SOAP yanıtını parse eder.
     */
    private function parseResponse(object $response): object
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

    /**
     * Durum kodunun açıklamasını döndürür.
     */
    public static function getStatusDescription(int $code): string
    {
        return match ($code) {
            self::STATUS_NOP => 'İşlem yapılmadı, düzenlenmemiş',
            self::STATUS_IND => 'Kargo teslimattadır',
            self::STATUS_ISR => 'Düzenlenmiş, fatura prosedürü tamamlanmamış',
            self::STATUS_CNL => 'Kargo çıkışı engellendi (başarılı iptal)',
            self::STATUS_ISC => 'Kargo zaten iptal edilmiş',
            self::STATUS_DLV => 'Teslim edildi',
            self::STATUS_BI  => 'YK acente tarafından iptal edildi',
            default => 'Bilinmeyen durum kodu',
        };
    }
}
