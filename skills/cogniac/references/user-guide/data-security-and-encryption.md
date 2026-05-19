# Data Security and Encryption

****Data Security and Encryption****

****How does Cogniac ensure security of customer data****

Cogniac treats customer data with the utmost care with an emphasis on Data Security during transfers and at rest.

When customers upload data ("media" in the Cogniac system) the transfers occur via a secure HTTP TLS endpoint (https:/api.cogniac.io).  This ensures that the customer data is end-to-end secure and encrypted during transfer.

You can refer to [Cogniac API documentation](/docs/api-overview) for further details regarding authentication.

Once the data is in the Cogniac CloudCore system Cogniac uses Amazon S3 AES-256 encryption to ensure the data is secure at rest.

Here is the screenshot showing CloudCore AES-256 encryption configuration in Amazon S3.

![A screenshot of a computer  Description automatically generated](../../../assets/media/images/data-security-and-encryption-image-20s3nzlz.png)
