
from server import app
from model import db
from model import User

from seed import seed_db

import feeder
import unittest
import doctest



# def load_tests(loader, tests, ignore):

#     tests.addTests(doctest.DocTestSuite(feeder))
#     tests.addTests(doctest.DocFileSuite("tests.txt"))
#     return tests



class MyAppIntegrationTestCase(unittest.TestCase):

    def setUp(self):
        """
        Setup a testing only database
        """
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///testingdb'
        db.app = app
        db.init_app(app)
        db.create_all()
        seed_db()

    def tearDown(self):
        """
        Delete our testing database
        """
        db.session.remove()
        db.drop_all()

    def test_upload(self):
        self.assertEqual(feeder.load_recipes("olddata/samplerecipe.xml"), ("success", "Tester Recipe"))

    def test_recipe(self):
        result = self.app.get("/recipe/Nate's%20Citrus%20Bomb%20IPA")
        self.assertIn("Citrus Bomb IPA</h3>", result.data)

    def test_myrecipes(self):
        result = self.app.get('/myrecipes')
        self.assertIn('Beer Styles', result.data)

if __name__ == '__main__':
    # If called like a script, run our tests

    unittest.main()
