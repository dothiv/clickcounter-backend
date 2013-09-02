clickcounter-backend
====================

The Google App Engine cloud app that supports the Click Counter.

ISSUES
------

- hypertext references in banner HTML/JS
  - templates/page.html references "/static/banner.min.js" . this could be
    prefixed with the proper host name, but this page is either served from
    the customer domain where we have no control over the 'page template'
    or, for testing, locally from the app engine server. so prefixing seems
    pointless.

  - static/banner.min.js is served from the app engine server and should
    reference the banner HTML (position = [center|top|right]) using the
    name of the app engine server as host.
    currently, the banner JS references the HTML relative to the host by
    "/static/banner-${position}.html", which, i believe, would make the
    user's browser try to get the resource from the customer's domain,
    because the originating page which includes the banner JS comes
    from there. but the banner HTML only exists on the app engine server.
    this probably needs to be hardcoded once we know the host name of the
    app engine server to be used.

  - similarly, static/banner.min.js and static/banner-${position}.html call
    the /c endpoint relatively at the moment. also, this could be hardcoded
    once we know the host name.

  - alternatively, the 'static' files could become templates where we
    dynamically prefix the host name and don't have to worry about hardcoding
    it. this comes with a small performance hit, of course. one we would
    possibly never feel until we reach millions of requests/minute. but since
    the client wants to use a cloud solution, it is probably wiser to not
    take the hit.

  - to summarise this block: probably best to leave the paths hardcoded.


- /c not protected by HTTP Basic Auth
  - the notes further below state that /c should be protected by HTTP Basic
    Auth. but the request to /c is issued by the user's browser (at least in
    the way the banner JS works at the moment), but the user is not
    supposed to know the secret, right? hence /c should not be protected.
    it would be trivial to enable it, though: just add the basic_auth
    decorator as done in the Config handler.

- additional user info not stored
  - during the phone meeting, it was mentioned to store additional user
    information, like IP address, user agent, etc. but none of that is
    mentioned in
    https://docs.google.com/document/d/18N4WNGfieNwkS7Nfb518ok7tvOO4bGWwl-0EqdoqIrM
  - to add it, i suggest to add another method to be called in the post
    method in the Count handler, right after the call to increment.
    a new model would also be required and it seems that most of the wanted
    data can be grabbed from os.environ (when using webapp2).

- POST to static files
  - should the static JS/HTML files really be 'uploaded' by POSTing to their
    URL? wouldn't it be more maintainable to have a git hook that will deploy
    to the app engine server automatically once these files have been changed
    in the repository?

NOTES
-----
specification available here: https://docs.google.com/document/d/18N4WNGfieNwkS7Nfb518ok7tvOO4bGWwl-0EqdoqIrM

1) serve static files /banner.min.js, /banner-top.html, /banner-right.html and /banner-center.html without authentication.

2) serve the following API calls:
  configure a domain name
     behavior: save the domain data, setup the domain with clicks 0, status 0 and money to 0
     if the domain config exist already override it.
     request:
         URL: /config/{domain}
         method: POST
         headers:
          Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ== //equivalent to Base64("Aladdin:open sesame")
         body: what_ever_content
     response:
         headers:
          content-type: text/plain
          code: 204
         body:

   get a domain name details:
     behavior: return the data about the domain name.
     request:
         URL: /config/{domainname}
         method: GET
         headers:
          Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ== //equivalent to Base64("Aladdin:open sesame")
         body:
     response:
         headers:
          content-type: text/plain
          code: 200
         body: what_ever_content


   delete a domain name:
     behavior: delete a domain name.
     request:
         URL: /config/{domainname}
         method: DELELTE
         headers:
          Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ== //equivalent to Base64("Aladdin:open sesame")
         body:
     response:
         headers:
          code: 204
         body:

   increment counter per domain:
     behavior: increment the number of visit for the domain name if fistvisit is true and from is "inside".
      Other compute the new money amount and status.
     request:
         URL: /c
         method: POST
         headers:
          Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ== //equivalent to Base64("Aladdin:open sesame")
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
