<?php
/**
 * Yurtiçi Kargo - QueryShipment (Gönderi Sorgulama)
 * 
 * Müşterinin kendi referans kodu ile gönderi geçmişini raporlayan servis.
 * 
 * @requires PHP 8.0+, ext-soap
 */

class QueryShipment
{
    private SoapClient $soapClient;
    private string $username;
    private string $password;
    private string $language;

    /** Key tipleri */
    public const KEY_TYPE_CARGO = 0;
    public const KEY_TYPE_INVOICE = 1;

    /** Operasyon durum kodları */
    public const STATUS_NOP = 0;
    public const STATUS_IND = 1;
    public const STATUS_ISR = 2;
    public const STATUS_CNL = 3;
    public const STATUS_ISC = 4;
    public const STATUS_DLV = 5;
    public const STATUS_BI  = 6;

    public function __construct(SoapClient $soapClient, string $username, string $password, string $language = 'TR')
    {
        $this->soapClient = $soapClient;
        $this->username = $username;
        $this->password = $password;
        $this->language = $language;
    }

    /**
     * Gönderi sorgulama yapar.
     *
     * @param array $keys Sorgulanacak anahtar değerleri
     * @param int $keyType 0=cargoKey, 1=invoiceKey
     * @param bool $addHistoricalData Hareket geçmişi dahil edilsin mi
     * @param bool $onlyTracking Sadece takip URL'si dönsün mü
     * @return object Response object
     * @throws SoapFault
     * @throws InvalidArgumentException
     */
    public function execute(array $keys, int $keyType = 0, bool $addHistoricalData = false, bool $onlyTracking = false): object
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

        return $this->parseResponse($response);
    }

    /**
     * SOAP yanıtını parse eder.
     */
    private function parseResponse(object $response): object
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
                                'unitName'  => (string) ($event->unitName ?? ''),
                                'eventName' => (string) ($event->eventName ?? ''),
                                'reasonName' => (string) ($event->reasonName ?? ''),
                                'eventDate' => (string) ($event->eventDate ?? ''),
                                'eventTime' => (string) ($event->eventTime ?? ''),
                                'cityName'  => (string) ($event->cityName ?? ''),
                                'townName'  => (string) ($event->townName ?? ''),
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

    /**
     * Durum kodunun açıklamasını döndürür.
     */
    public static function getStatusDescription(int $code): string
    {
        return match ($code) {
            self::STATUS_NOP => 'İşlem yapılmadı, düzenlenmemiş',
            self::STATUS_IND => 'Kargo teslimattadır',
            self::STATUS_ISR => 'Düzenlenmiş, fatura prosedürü tamamlanmamış',
            self::STATUS_CNL => 'Çıkış engellendi',
            self::STATUS_ISC => 'İptal edilmiş',
            self::STATUS_DLV => 'Teslim edildi',
            self::STATUS_BI  => 'YK acente tarafından iptal edildi',
            default => 'Bilinmeyen durum kodu',
        };
    }
}
