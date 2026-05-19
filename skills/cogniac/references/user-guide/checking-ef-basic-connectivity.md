# Checking EF basic connectivity

****Checking EF basic connectivity****

For EdgeFlows successful operation EdgeFlow needs basic networking services like DNS and reachability to certain FQDNs at certain ports

Currently the requirement -

Source IP - EdgeFlow IP

Source Port  - any

Destination FQDN - api.cogniac.io

Destination Ports - 443 / 5000 / 5001 / 5002

If you connect the laptop (machine) where the EF is supposed to be connected (even the cable and switch-port just to be sure) and make sure the EF IP configuration setup is duplicated on this laptop then we can run the following tests.

First to test whether FQDN api.cogniac.io can be resolved via DNS or not run

nslookup api.cogniac.io

Generic

The results should be something like (server IP address might be different based on individual EdgeFlow configuration)

Server: <DNS SERVER IP ADDRESS>

Address: <DNS SERVER IP ADDRESS>#53

Non-authoritative answer:

Name: api.cogniac.io

Address: 52.53.41.133

Name: api.cogniac.io

Address: 13.52.206.75

Generic

Once we determine that resolution of the FQDN to IP is working then we can test connectivity

To test :443 connectivity run

curl https://api.cogniac.io/1/version

Generic

You should get the output like -

{"build": "30934413", "api\_version": "1"}

Generic

This means we are able to connect to port 443

To test the connectivity to port 5000 / 5001 and 5002 run the commands

curl -I https://api.cogniac.io:5000/healthz

curl -I https://api.cogniac.io:5001/

curl -I https://api.cogniac.io:5002/

Generic

You should get an HTTP/1.1 200 OK response for all these

Sample responses are like below

curl -I https://api.cogniac.io:5000/healthz

HTTP/1.1 200 OK

Date: Tue, 20 Oct 2020 18:17:04 GMT

Content-Type: text/plain; charset=utf-8

Content-Length: 2

Connection: keep-alive

Strict-Transport-Security: max-age=15724800; includeSubDomains

curl -I https://api.cogniac.io:5001/

HTTP/1.1 200 OK

Server: nginx/1.17.10

Date: Sat, 10 Oct 2020 04:49:00 GMT

Content-Type: application/json

Connection: keep-alive

Vary: Accept-Encoding

Cache-Control: no-cache, no-store, must-revalidate

Expires: Wed 24 Feb 1982 18:42:00 GMT

X-Api-Schemas: https://api.cogniac.io:5001/meta/schemas

X-Content-Type-Options: nosniff

X-Frame-Options: deny

Strict-Transport-Security: max-age=15724800; includeSubDomains

Access-Control-Allow-Origin: \*

Access-Control-Allow-Credentials: true

Access-Control-Allow-Methods: GET, PUT, POST, DELETE, PATCH, OPTIONS

Access-Control-Allow-Headers: DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization

curl -I https://api.cogniac.io:5002/

HTTP/1.1 200 OK

Cache-Control: no-cache

Date: Sat, 10 Oct 2020 04:49:07 GMT
