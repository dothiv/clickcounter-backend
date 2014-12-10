# dotHIV ClickCounter Backend

[![Build Status](https://travis-ci.org/dothiv/clickcounter-backend.svg)](https://travis-ci.org/dothiv/clickcounter-backend)

The Google App Engine cloud app that supports the Click Counter.

The technical specification is available [here](https://docs.google.com/document/d/18N4WNGfieNwkS7Nfb518ok7tvOO4bGWwl-0EqdoqIrM).

## API

### Static files

Serve static files in `/static` without authentication.

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

See [click-counter's demo.json](https://github.com/dothiv/clickcounter/blob/master/develop/demo.json) for an example response.

#### Fetch global clickcount

This returns the global click count of all .hiv domains as an integer value

    request:
        URL: /stats/clickcount
        method: GET
    response:
        headers:
          content-type: text/plain
          code: 200
        body: 123456789

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
        body: …

You can query this endpoint live:  
`curl -H "Accept: application/json" https://dothiv-registry.appspot.com/redirects`

##### Inverse mapping as CSV

There is also the reverse version of this list, mapping hiv domain to redirect as a CSV list:

    request:
        URL: /redirects
        method: GET
        headers:
            Accept: text/csv
    response:
        headers:
            Code: 200
            Content-type: text/csv
        body:
            beratung.hiv,http://www.aidshilfe-beratung.de
            sixt.hiv,http://www.sixt.de
            …


You can query this endpoint live:  
`curl -H "Accept: text/csv" https://dothiv-registry.appspot.com/redirects`

### Authorization

Configuration updating endpoints are protected with basic auth. The password is generated on the first access
of the endpoint and can be changed via the AppEngine Console's DataStore Viewer. Look for a `Config` entity with the
key `auth_secret`.
