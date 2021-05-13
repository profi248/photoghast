import unittest

import web.user_manager
import utils.db_models


class UserTests(unittest.TestCase):
    def test_valid_password(self):
        # hash("pythonrocks")
        valid_passwd_hash = b'$2b$12$dtP6BnwbTMsfdga7Jbcg6e/' \
                            b'3pCxMX1I6Jg3tgGPMsAjOWqVwHrOfC'
        user_mdl = utils.db_models.User(password=valid_passwd_hash)
        self.assertTrue(web.user_manager.check_user_passwd(user_mdl,
                                                           "pythonrocks"))

    def test_invalid_password(self):
        # hash("pythonrocks")
        valid_passwd_hash = b'$2b$12$dtP6BnwbTMsfdga7Jbcg6e/' \
                            b'3pCxMX1I6Jg3tgGPMsAjOWqVwHrOfC'
        user_mdl = utils.db_models.User(password=valid_passwd_hash)
        self.assertFalse(web.user_manager.check_user_passwd(user_mdl,
                                                            "pythonsucks"))


if __name__ == '__main__':
    unittest.main()
