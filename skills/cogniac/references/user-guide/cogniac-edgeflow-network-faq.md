# Cogniac EdgeFlow Network FAQ

## How does the EdgeFlow get its network configuration?

Via DHCP on the internet-facing wan0 ethernet port by default. Refer to the EdgeFlow Quickstart Guide or contact Cogniac Support for assistance in provisioning static IP addresses.

## What public IP hosts and ports does the gateway need to communicate with?

The Cogniac EdgeFlow communicates with the following hosts on the public internet:

|  | ****Source Address**** | ****Destination Address**** | ****Port**** | ****Protocol**** | ****Required**** | ****Comments**** |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  | EdgeFlow | api.cogniac.io   52.53.41.133   13.52.206.75 | TCP:443 | HTTPS | yes\* | Cogniac CloudCore Command and Control |  |
|  | EdgeFlow | api-sc-us.cogniac.io | TCP:443 | HTTPS | optional | Cogniac CloudCore in Azure South Central region |  |
|  | EdgeFlow | api.cogniac.io | TCP:5000 TCP:5002 | HTTPS | yes\* | Software and model upgrades |  |
|  | EdgeFlow | api.cogniac.io | TCP:5001 TCP:5006 | HTTPS | yes\* | Cluster management and upgrade operations |  |
|  | EdgeFlow | Local NTP server or ntp.ubuntu.com | UDP:123 | NTP | yes\* | Can specify local NTP server using standard DHCP mechanisms |  |
|  | EdgeFlow | Local DNS server | UDP:53 TCP:53 | DNS | yes\* | Standard DNS services; can be specified via DHCP or via static IP configuration |  |
|  | EdgeFlow | Contact Cogniac support | TCP:22 | SSH | optional | Temporary support access for authorized Cogniac personnel via secure bastion |  |
|  | EdgeFlow | logs-01.loggly.com | TCP:443 | HTTPS | optional | Logging for support purposes |  |
