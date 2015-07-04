#!flask/bin/python
import os
import unittest

from server import app
from model import db
from model import User

from sqlalchemy import exc


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
        self.assertTrue('Login' in rv.data)

        rv = self.login('jsmith', 'testb')
        self.assertTrue('User name and password do not match' in rv.data)

        rv = self.login('jsmithc', 'test')
        self.assertTrue('This username is not registered - please create an account' in rv.data)

    # ==============================================================================
    # Testing Login/Logout Views
    # ==============================================================================


if __name__ == '__main__':
    unittest.main()
