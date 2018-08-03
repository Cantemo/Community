# Session Redirect Plugin


This is an example plugin which allows you to create a login redirect page
which exports the Portal session cookie to a trusted external site.

This can be used for example when you want to build an external GUI but
wants to call the Portal REST APIs as the user authenticated to Portal.

## Settings

This plugin requires two settings to be added to the Django settings object.
The easiest way to accomplish this is to add it to the file 
`/opt/cantemo/portal/portal/localsettings.py` which is loaded when Portal starts.

* SESSION_REDIRECT_COOKIE_NAME - The name of the external cookie which the session id
  will be added to.

* SESSION_REDIRECT_COOKIE_DOMAIN - The domain which the external cookie will be
  set for. 

Example content of localsettings.py:

    SESSION_REDIRECT_COOKIE_NAME = '`'
    SESSION_REDIRECT_COOKIE_DOMAIN = '.example.com'

Usage
-----

In your external application you can now do a check if the user supplies a cookie
with the name `external_session_id`. If they do you can use that to 
authenticate your own calls to Portal's REST api with the cookie `sessionid` set to 
the value of the `external_session_id` cookie.

If the user does not supply such a cookie, or if you get a 401 response from portal
when trying to use it, you will have to redirect the user to 
http://portalserver/session_redirect_plugin/?next=http://testserver.example.com/the_page_the_user_was_accessing/
This will cause Portal to authenticate the user via whichever mechanism is configured
in your Portal installation, and then redirect the user back to the external application.

Please note that the `next` parameter must either be http or https. All other methods are
disallowed for security reasons. Likewise, the hostname of the `next` parameter also
must match the value of the SESSION_REDIRECT_COOKIE_DOMAIN setting.

Trouble shooting
----------------

This plugin tries to leave good feedback if incorrect settings or
input data is sent to the request. One thing to take note of is that
many browsers have protection against so called 3rd-party cookies
which prevents a site from setting a cookie for another, unrelated
site. This means that you may have to take note of the domain scope
the SESSION_REDIRECT_COOKIE_DOMAIN and make sure it's compatible with
the hostname of the portal server.