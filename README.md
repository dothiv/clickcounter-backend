# dotHIV ClickCounter Backend

[![Build Status](https://travis-ci.org/dothiv/clickcounter-backend.svg)](https://travis-ci.org/dothiv/clickcounter-backend)

The Google App Engine cloud app that supports the Click Counter.

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

increment the number of visit for the domain and populate domain configuration.

    request:
        URL: /c
        method: POST
        headers:
        query variables:
        {
          domain: "domainname",
          from: "inside/outside",
          pt: "" or integer,
          ct: integer
        }
    response:
        headers:
          content-type: application/json
          code: 200
        body: …

See [#5](https://github.com/dothiv/clickcounter-backend/pull/5) for an explanation of the request parameters.

See [banner's demo.json](https://github.com/dothiv/banner/blob/master/src/demo.json) for an example response.

#### Fetch configured .hiv domain redirects

We provide a ruleset file which list redirects from regular domains to their .hiv equivalent.

    request:
        URL: /redirects
        method: GET
        headers:
            Accept: application/json
    response:
        headers:
            Code: 200
            Content-type: application/json
            Last-Modified: …
            ETag: …
        body: [example](https://github.com/dothiv/banner/blob/master/example/redirects.json)

### Authorization

Configuration updating endpoints are protected with basic auth. The password is generated on the first access
of the endpoint and can be changed via the AppEngine Console's DataStore Viewer. Look for a `Config` entity with the
key `auth_secret`.
