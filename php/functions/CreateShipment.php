<?php
/**
 * Yurtiçi Kargo - CreateShipment (Gönderi Oluşturma)
 * 
 * Müşterinin kargo bilgilerini Yurtiçi Kargo sistemine ileten servis.
 * 
 * @requires PHP 8.0+, ext-soap
 */

class CreateShipment
{
    private SoapClient $soapClient;
    private string $username;
    private string $password;
    private string $language;

    public function __construct(SoapClient $soapClient, string $username, string $password, string $language = 'TR')
    {
        $this->soapClient = $soapClient;
        $this->username = $username;
        $this->password = $password;
        $this->language = $language;
    }

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
     * Opsiyonel alanlar:
     *   - receiverPhone2, receiverPhone3, cityName, townName, custProdId,
     *   - desi, kg, cargoCount, waybillNo, specialField1, specialField2, specialField3,
     *   - ttCollectionType, ttInvoiceAmount, ttDocumentId, ttDocumentSaveType,
     *   - orgReceiverCustId, description, taxNumber, taxOfficeId, taxOfficeName,
     *   - orgGeoCode, privilegeOrder, dcSelectedCredit, dcCreditRule, emailAddress
     *
     * @return object Response object with outFlag, outResult, jobId, count, details
     * @throws SoapFault
     * @throws InvalidArgumentException
     */
    public function execute(array $shipments): object
    {
        if (empty($shipments)) {
            throw new \InvalidArgumentException('En az bir gönderi bilgisi gereklidir.');
        }

        $requiredFields = ['cargoKey', 'invoiceKey', 'receiverCustName', 'receiverAddress', 'receiverPhone1'];

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

            // Opsiyonel string alanlar - WSDL tüm property'leri bekler, boş gönderilmeli
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

            // Numeric alanlar - varsayılan 0
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
}
