from django.test import TestCase
from ..models import WikiPage, WikiSpace


class TrivialModelTestCase(TestCase):

    fixtures = ['basic-db.json']

    def Xtest_to_str(self):

        wikiname = 'LedZeppelin'

        space = WikiSpace.objects.create(name=wikiname)
        self.assertEqual(space.__str__(), wikiname)

        page = WikiPage.objects.create(name=wikiname, space=space)
        self.assertEqual(page.__str__(), wikiname)
