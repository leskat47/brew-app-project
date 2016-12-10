
from server import app
from model import db
from model import User, Brew

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

        u = User(first_name='Jane', last_name='Smith', email='jsmith@example.com', username='jsmith', password='test')
        db.session.add(u)
        db.session.commit()
        self.login('jsmith', 'test')

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

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
        self.assertIn('<div style="display: inline; width: 50px; height: 20px; background-color: #f39c00">&nbsp; &nbsp;</div>',
                      result.data)
        # TODO: Add tests for color calc on Explore page

    def test_myrecipes(self):
        result = self.app.get('/myrecipes')
        self.assertIn('Beer Styles', result.data)

    def test_brew(self):
        result = self.app.get("/addbrew/Nate's%20Citrus%20Bomb%20IPA", follow_redirects=True)
        # Does the correct color display for Nate's Citrus Bomb?
        self.assertIn('<div style="width: 25px; height: 25px; background-color: #f39c00;">',
                      result.data)

        result = self.app.get("/brew/1")
        self.assertIn('<div style="width: 25px; height: 25px; background-color: #f39c00;">',
                      result.data)

    def test_mybrews_color(self):
        self.app.get("/addbrew/Nate's%20Citrus%20Bomb%20IPA")
        result = self.app.get("/mybrews")
        self.assertIn('<td rowspan="5" style="width: 5px; background-color: #f39c00;"></td>', result.data)

    # TODO: Add test for ajax call trying color calculation display.

if __name__ == '__main__':
    # If called like a script, run our tests

    unittest.main()
