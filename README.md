# dotHIV ClickCounter Backend

[![Build Status](https://travis-ci.org/dothiv/clickcounter-backend.svg)](https://travis-ci.org/dothiv/clickcounter-backend)

The Google App Engine cloud app that supports the Click Counter.

## Atomic nbd.put()


Data objects are modified in the handlers and then all the modifications are
sent to the storage together by NBD's put() method, which in itself is consistent.
See [Storing Data in Python](https://developers.google.com/appengine/docs/python/storage).


## IPv6 compatibility

[This means that all App Engine apps will become accessible over IPv6 to anyone participating in the program!](http://googleappengine.blogspot.de/2010/03/app-engine-joins-google-over-ipv6.html)


## Data storage comparision

See [Storing Data in Python](https://developers.google.com/appengine/docs/python/storage).

> Strongly consistent except when performing global queries.

> The App Engine Datastore offers a free quota with daily limits. Paid accounts offer unlimited storage, read, and write operations.


## NOTES

The technical specification is available [here](https://docs.google.com/document/d/18N4WNGfieNwkS7Nfb518ok7tvOO4bGWwl-0EqdoqIrM).

## API

### Static files

Serve static files without authentication: 

 * `/banner.min.js`
 * `/banner-top.html`
 * `/banner-right.html`
 * `/banner-center.html`

### Endpoints

#### configure a domain name

save the domain data, setup the domain with clicks 0, status 0 and money to 0 if the domain config exist already override it.

    request:
        URL: /config/{domain}
        method: POST
        headers:
          Authorization: Basic OnNvbWVzZWNyZXQ= // equivalent to Base64(":somesecret")
        body: what_ever_content
    response:
        headers:
          content-type: text/plain
          code: 204
        body:

#### get a domain name details

return the data about the domain name.
    
    request:
        URL: /config/{domainname}
        method: GET
        headers:
          Authorization: Basic OnNvbWVzZWNyZXQ= // equivalent to Base64(":somesecret")
        body:
    response:
        headers:
          content-type: text/plain
          code: 200
        body: what_ever_content


#### delete a domain name
     
    request:
        URL: /config/{domainname}
        method: DELELTE
        headers:
          Authorization: Basic OnNvbWVzZWNyZXQ= // equivalent to Base64(":somesecret")
        body:
    response:
        headers:
          code: 204
        body:

#### increment counter per domain

increment the number of visit for the domain name if fistvisit is true and from is "inside". Other compute the new money amount and status.

    request:
        URL: /c
        method: POST
        headers:
        query variables:
        {
          domain: "domainname",
          from: "inside/outside",
          firstvist: true/false,
        }
    response:
        headers:
          content-type: application/json
          code: 200
        body:
        {
          what_ever_content,
          "clickcount": 12312321,
          "money": 1213123, # inc by 0.1 per click
          "status": 1212 # 500 000 == 100%
        }

### Authorization

Configuration updating endpoints are protected with basic auth. The password is generated on the first access
of the endpoint and can be changed via the AppEngine Console's DataStore Viewer. Look for a `Config` entity with the
key `auth_secret`.
