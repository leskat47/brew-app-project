#!flask/bin/python
import os
import unittest

from server import app
from model import db
from model import User

from seed import seed_db

from sqlalchemy import exc

import json

import feeder
import builder


class TestCase(unittest.TestCase):

    def setUp(self):
        """
        Setup a testing only database
        """
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
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

    # ==============================================================================
    # Testing User Model
    # ==============================================================================
    def test_user(self):
        # Make a user
        u = User(first_name='John', last_name='Smith', email='jsmith@example.com', username='jsmith', password='test')
        db.session.add(u)
        db.session.commit()
        self.assertEqual(u.first_name, 'John')

        # Duplicate critical information
        u = User(first_name='Jane', last_name='Smith', email='jsmith@example.com', username='jsmith', password='test')
        db.session.add(u)
        with self.assertRaises(exc.IntegrityError):
            db.session.commit()
        db.session.rollback()

        # See what happens if we are missing information
        u = User(first_name='Jane', last_name='Smith', email='jsmith@example.com', username='jsmith')
        db.session.add(u)
        with self.assertRaises(exc.IntegrityError):
            db.session.commit()
        db.session.rollback()


    # ==============================================================================
    # Testing Login/Logout Views
    # ==============================================================================
    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        u = User(first_name='John', last_name='Smith', email='jsmith@example.com', username='jsmith', password='test')
        db.session.add(u)
        db.session.commit()

        rv = self.login('jsmith', 'test')
        self.assertTrue('Logout' in rv.data)

        rv = self.logout()
        self.assertTrue('Log In' in rv.data)

        rv = self.login('jsmith', 'testb')
        self.assertTrue('User name and password do not match' in rv.data)

        rv = self.login('jsmithc', 'test')
        self.assertTrue('This username is not registered - please create an account' in rv.data)

    # ==============================================================================
    # Test Beer Edit Views
    # ==============================================================================
    def test_est_color(self):
        color_json = {u'units': u'gallons', u'extracts': [{u'name': u'extract', u'value': u'Ultralight Extract (MoreBeer)'}, {u'name': u'extract_amount', u'value': u'144.0'}, {u'name': u'extract-units', u'value': u'ounces'}, {u'name': u'extract', u'value': u'Dry Light Extract'}, {u'name': u'extract_amount', u'value': u'8.0'}, {u'name': u'extract-units', u'value': u'ounces'}], u'grains': [{u'name': u'grain', u'value': u'Crystal 15'}, {u'name': u'grain_amount', u'value': u'12.0'}, {u'name': u'grain_units', u'value': u'ounces'}], u'batch_size': u'5.28'}

        rv = self.app.post('/colorcalc', data=json.dumps(color_json), content_type='application/json')
        self.assertTrue("#f39c00" in rv.data)

    # ==============================================================================
    # Unit Test Recipe Upload
    # ==============================================================================
    def test_upload(self):
        self.assertEqual(feeder.load_recipes("olddata/samplerecipe.xml"), ("success", "Tester Recipe"))

    # ==============================================================================
    # Unit Test Get Ingredient Lists
    # ==============================================================================
    def test_feed_recipe_form(self):
        ingredient_lists = builder.feed_recipe_form()
        self.assertTrue("2-Row Black Malt" in ingredient_lists[0])
        self.assertTrue("Blond Dry" in ingredient_lists[1])
        self.assertTrue("Magnum" in ingredient_lists[2])
        self.assertTrue("Orange zest" in ingredient_lists[3])
        self.assertTrue("Windsor" in ingredient_lists[4])

        self.assertEqual(ingredient_lists[0][0], "2-Row Black Malt")


if __name__ == '__main__':
    unittest.main()
