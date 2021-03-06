'''
Created on Apr 18, 2016

@author: ivan
'''
import unittest
from app.utils import create_token, verify_token
from app.model import User
from .basecase import TestCase


class Test(TestCase):

    def test_jwt(self):
        user = User(id=55, user_name='kulich', email='kulich@example.com')
        secret = 'ZZigIKCHuSNeSHwfU+TAbyNX4nwyMUDRXnv0aZgBlOM'
        token = create_token(user, secret)
        claim = verify_token(token, secret)
        self.assertEqual(user.id, claim['id'])
        self.assertEqual(user.user_name, claim['user_name'])
        self.assertEqual(user.email, claim['email'])
        self.assertTrue(verify_token(token, 'bad secret') is None)
        token2 = create_token(user, secret, -30)
        self.assertTrue(verify_token(token2, secret) is None)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_jwt']
    unittest.main()
