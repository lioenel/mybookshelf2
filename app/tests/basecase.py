'''
Created on Apr 23, 2016

@author: ivan
'''
import unittest
from app import app, db
from flask_testing import TestCase as BaseTestCase
from settings import Testing
import os.path
import logging
logging.basicConfig(level=logging.DEBUG)


class TestCase(BaseTestCase):

    INIT_FILES = ['../data/create_ts.sql',  # text search config
                  # create other sql  procedures
                  '../data/create_functions.sql',
                  '../data/dump/basic.sql',  # basic stuff
                  '../data/dump/test_data.sql'  # test data = random 100 ebooks
                  ]

    def create_app(self):
        app.config.from_object(Testing)
        return app

    def setUp(self):
        db.drop_all()
        db.create_all()
        connection = db.engine.raw_connection()
        try:
            c = connection.cursor()

            for f in self.INIT_FILES:
                script = open(
                    os.path.join(os.path.dirname(__file__), f), 'rt', encoding='utf-8-sig').read()
                # print(script)
                res = c.execute(script)
                connection.commit()

        finally:
            pass
            connection.close()

    def tearDown(self):
        db.session.rollback()
        db.session.remove()
        # db.drop_all()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_db']
    unittest.main()
