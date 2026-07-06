<?php
/**
 * Yurtiçi Kargo - SaveReturnShipmentCode (İade Kodu Oluşturma)
 * 
 * İade müşterilerinin YK birimine ileterek iade işlemini tamamlayacakları kodu oluşturur.
 * 
 * @requires PHP 8.0+, ext-soap
 */

class SaveReturnShipmentCode
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
     * İade kodu oluşturur.
     *
     * @param string $returnCode Benzersiz iade kodu
     * @param string $startDate Geçerlilik başlangıç tarihi (YYYYMMDD)
     * @param string $endDate Geçerlilik bitiş tarihi (YYYYMMDD)
     * @param int $maxCount Kullanım adedi
     * @param string $fieldName Özel alan bilgisi (test: 53 veya 3, canlı: 16)
     * @return object Response object with outFlag, outResult, errCode
     * @throws SoapFault
     * @throws InvalidArgumentException
     */
    public function execute(string $returnCode, string $startDate, string $endDate, int $maxCount, string $fieldName): object
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

        return $this->parseResponse($response);
    }

    /**
     * SOAP yanıtını parse eder.
     */
    private function parseResponse(object $response): object
    {
        $result = new \stdClass();

        $data = $response->ExtendedBaseResultVO ?? $response;

        $result->outFlag = (int) ($data->outFlag ?? 2);
        $result->outResult = (string) ($data->outResult ?? '');
        $result->errCode = (int) ($data->errCode ?? 0);

        $result->isSuccess = fn() => $result->outFlag === 0;

        return $result;
    }
}
