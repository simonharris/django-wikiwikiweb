"""
Various web page clicks

TODO:
 - This will grow rapidly, so look into ways of splitting up
 - The hardcoded URLs are fragile
"""

from django.contrib.auth.models import User
from django.test import TestCase

from ..models import WikiPage


class TestBasicCalls(TestCase):
    """General control flow through site"""

    fixtures = ['basic-db.json']

    #
    # Potential TODO:
    #  - force Space for create page - done but lacks test
    #  - check rev matches WikiName for archive stuff (not urgent, just seems odd right now) See #11
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

    def test_get_create_form_if_logged_in(self):
        self._populate_session()

        response = self.client.get('/wiki/ImaginaryPage')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wiki/wiki_page_create.html')

    # TODO: test invalid form data

    def test_create_form_post(self):
        self._populate_session()

        newpagename = 'MyNewPage' # nb. not in fixture db

        # nb. 'name' will soon be retired, see #18
        formdata = {'name': newpagename,
                    'content': 'Some page content',
                    'edit_reason': 'Created1'}

        newpageurl = '/wiki/' + newpagename

        response = self.client.post(newpageurl, data=formdata)
        self.assertRedirects(response, newpageurl + '?win=yes') # fragile, but works for now

        newpage = WikiPage.objects.get(pk=newpagename)

        self.assertEqual(newpage.created_by, self._get_user(self._test_user))
        self.assertEqual(newpage.updated_by, self._get_user(self._test_user))


    # Edit page

    def test_get_edit_form_if_logged_in(self):
        self._populate_session()

        response = self.client.get('/wiki/AvrilLavigne/edit')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wiki/wiki_page_edit.html')


    def test_edit_form_post(self):
        self._populate_session()

        editpagename = 'JoniMitchell' # nb. is in fixture db; created by user 4/otheruser

        # nb. 'name' will soon be retired, see #18
        formdata = {'name': editpagename,
                    'content': 'Some edited page content',
                    'edit_reason': 'Edited1'}

        viewpageurl = '/wiki/' + editpagename
        editpageurl = viewpageurl + '/edit'

        response = self.client.post(editpageurl, data=formdata)
        self.assertRedirects(response, viewpageurl + '?win=yes') # fragile, but works for now

        newpage = WikiPage.objects.get(pk=editpagename)

        # check this hasn't changed...
        self.assertEqual(newpage.created_by, self._get_user('otheruser'))

        # ...but this has
        self.assertEqual(newpage.updated_by, self._get_user(self._test_user))



    # WikiSpace pages ---------------------------------------------------------

    # TODO

    # Search page -------------------------------------------------------------

    def test_request_search_with_space_in_session(self):

        self._populate_session()

        response = self.client.get('/wiki/search?q=avril')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wiki/search.html')

    def test_request_search_with_no_space(self):

        session = self.client.session
        self.assertFalse(session.get(self._sess_key_space))

        response = self.client.get('/wiki/search?q=Avril+Lavigne')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/wiki/space/select?next=/wiki/search?q=Avril+Lavigne')

    # Private methods ----------------------------------------------------------

    def _populate_session(self):
        """Ensure user logged in, and valid WikiSpace in session"""

        self.client.login(username=self._test_user, password=self._test_pass)

        session = self.client.session
        session[self._sess_key_space] = 'ThreeHundredSongs'
        session.save()

    def _get_user(self, username):
        return User.objects.get(username=username)

