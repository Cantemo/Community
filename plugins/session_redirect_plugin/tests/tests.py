import urllib

from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import override_settings
from mock import patch

# This is an example of tests for portal. To run these tests, start by installing all the test requirements:
#
# /opt/cantemo/python/bin/pip install -r /opt/cantemo/portal/test-requirements.pip
#
# Then run:
#
# /opt/cantemo/portal/manage.py test portal.plugins.session_redirect_plugin
from portal.utils.test_utils import PortalTestCase


@override_settings(
    SESSION_REDIRECT_COOKIE_NAME='test_cookie',
    SESSION_REDIRECT_COOKIE_DOMAIN='.example.com'
)
class TestSessionRedirectAuthenticated(PortalTestCase):

    def setUp(self):
        super(TestSessionRedirectAuthenticated, self).setUp()
        self.client.login(username=settings.VIDISPINE_USERNAME, password=settings.VIDISPINE_PASSWORD)

    def tearDown(self):
        super(TestSessionRedirectAuthenticated, self).tearDown()
        # Do any teardown here

    def test_next_required(self):
        response = self.client.get(reverse("session_redirect_plugin:index"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, "next is a required parameter")

    def test_next_wrong_domain(self):
        response = self.client.get(reverse("session_redirect_plugin:index") + "?next=http://otherexample.com")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, "next parameter not a subdomain of the correct domain")

    def test_next_wrong_method(self):
        response = self.client.get(reverse("session_redirect_plugin:index") + "?next=mailto:user@example.com")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, "next parameter must be a url with http or https")

    def test_next_redirect_correct(self):
        """
        Verify that we get redirected back to the correct url and that we get the session cookie set correctly.
        """
        response = self.client.get(reverse("session_redirect_plugin:index") + "?next=http://www.example.com/foo/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://www.example.com/foo/')
        cookie = response.cookies[settings.SESSION_REDIRECT_COOKIE_NAME]
        self.assertEqual(cookie['domain'], settings.SESSION_REDIRECT_COOKIE_DOMAIN)
        self.assertEqual(cookie.value, response.client.cookies['sessionid'].value)


class TestSessionRedirectUnAuthenticated(PortalTestCase):
    def test_requires_auth(self):

        test_url = reverse("session_redirect_plugin:index") + "?next=http://example.com/test/"
        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 302)
        # Make sure the login page redirects us back
        self.assertEqual(response['Location'], settings.LOGIN_URL + "?next=" + urllib.quote(test_url))
