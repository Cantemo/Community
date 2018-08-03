"""
This is where you can write a lot of the code that responds to URLS - such as a page request from a browser
or a HTTP request from another application.

From here you can follow the Cantemo Portal Developers documentation for specific code, or for generic 
framework code refer to the Django developers documentation. 

"""
import logging
import urlparse

from django.http import HttpResponseRedirect, HttpResponseServerError, HttpResponseBadRequest

from portal.api.decorators import validate_query_params
from portal.generic.baseviews import CView
from django.conf import settings

log = logging.getLogger(__name__)


class SessionRedirectView(CView):
    """ Show the page. Add your python code here to show dynamic content or feed information in
        to external apps

        ---
        responseMessages:
          - code: 400
            message: Bad request
          - code: 403
            message: Insufficient rights to call this procedure
        parameters:
          - name: next
            description: Where to redirect the user after the authentication is done
            type: string
            paramType: query
            required: true
    """

    @validate_query_params()
    def get(self, request):
        """
        This view authenticates the user and then redirects them to the page specified in the `next`
        parameter, setting the portal session cookie
        """

        log.debug("%s Viewing page" % request.user)
        session_id = request.COOKIES.get('sessionid')

        next_url = request.query_params.get('next')

        if not next_url:
            return HttpResponseBadRequest("next is a required parameter")

        parsed_url = urlparse.urlparse(next_url)
        cookie_name = getattr(settings, 'SESSION_REDIRECT_COOKIE_NAME', None)
        cookie_domain = getattr(settings, 'SESSION_REDIRECT_COOKIE_DOMAIN', None)

        if not cookie_name:
            return HttpResponseServerError("SESSION_REDIRECT_COOKIE_NAME not configured in django settings")

        if not cookie_domain:
            return HttpResponseServerError("SESSION_REDIRECT_COOKIE_DOMAIN not configured in django settings")

        # Only allow if the request is for a full url, and that url is a subdomain of settings.FMC_COOKIE_DOMAIN
        if parsed_url.scheme not in ["http", "https"]:
            return HttpResponseBadRequest("next parameter must be a url with http or https")

        if parsed_url.hostname and parsed_url.hostname.endswith(cookie_domain):
            response = HttpResponseRedirect(redirect_to=next_url)
            if session_id:
                response.set_cookie(cookie_name, session_id, domain=cookie_domain)

            return response
        else:
            return HttpResponseBadRequest("next parameter not a subdomain of the correct domain")
