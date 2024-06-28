"""
Various web page clicks

TODO:
 - This will grow rapidly, so look into ways of splitting up
 - The hardcoded URLs are fragile
"""

from django.contrib.auth.models import User
from django.test import TestCase


class TestBasicCalls(TestCase):
    """General control flow through site"""

    fixtures = ['basic-db-users.json', 'basic-db.json']

    #
    # Potential TODO:
    #  - force Space for search
    #  - force Space for create page
    #  - check rev matches WikiName for archive stuff (not urgent, just seems odd right now)
    #  -
    #

    def setUp(self):
        self._test_user = 'testuser'
        self._test_pass = 'testpass123'
        self._sess_key_space = 'sess_space_key'


    # Home page ---------------------------------------------------------------

    def test_homepage_load(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'default/home.html')

    # WikiPage pages-----------------------------------------------------------

    # View page

    def test_success_for_real_wikipage(self):
        response = self.client.get('/wiki/AvrilLavigne')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wiki/wiki_page.html')
        # TODO assert session set

    # Create page

    def test_require_login_for_create_not_logged_in(self):
        response = self.client.get('/wiki/ThisNoExist')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/wiki/ThisNoExist')

    # Edit page

    def test_get_edit_form_if_logged_in(self):
        self.client.login(username=self._test_user, password=self._test_pass)
        response = self.client.get('/wiki/AvrilLavigne/edit')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wiki/wiki_page_edit.html')

    # WikiSpace pages ---------------------------------------------------------

    # TODO

    # Search page -------------------------------------------------------------

    def test_request_search_with_space_in_session(self):

        session = self.client.session

        session[self._sess_key_space] = 'ThreeHundredSongs'
        session.save()

        response = self.client.get('/wiki/search?q=avril')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wiki/search.html')


    def test_request_search_with_no_space(self):

        session = self.client.session
        self.assertFalse(session.get(self._sess_key_space))

        response = self.client.get('/wiki/search?q=Avril+Lavigne')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/wiki/space/select?next=/wiki/search?q=Avril+Lavigne')
