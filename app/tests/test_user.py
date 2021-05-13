import unittest
import uuid

import web.user_manager
import utils.db_models


class UserTests(unittest.TestCase):
    """
    Test whether set password matches correctly.
    """
    def test_valid_password(self):
        # hash("pythonrocks")
        valid_passwd_hash = b'$2b$12$dtP6BnwbTMsfdga7Jbcg6e/' \
                            b'3pCxMX1I6Jg3tgGPMsAjOWqVwHrOfC'
        user_mdl = utils.db_models.User(password=valid_passwd_hash)
        self.assertTrue(web.user_manager.check_user_passwd(user_mdl,
                                                           "pythonrocks"))

    """
    Test whether set password fails properly.
    """
    def test_invalid_password(self):
        # hash("pythonrocks")
        valid_passwd_hash = b'$2b$12$dtP6BnwbTMsfdga7Jbcg6e/' \
                            b'3pCxMX1I6Jg3tgGPMsAjOWqVwHrOfC'
        user_mdl = utils.db_models.User(password=valid_passwd_hash)
        self.assertFalse(web.user_manager.check_user_passwd(user_mdl,
                                                            "pythonsucks"))

    """
    Test whether random hashes of the same string match correcly.
    """
    def test_hash_comparison_valid(self):
        rand_password = str(uuid.uuid4())
        hash = web.user_manager.hash_passwd(rand_password)
        user_mdl = utils.db_models.User(password=hash)

        self.assertTrue(web.user_manager.check_user_passwd(user_mdl,
                                                           rand_password))

    """
    Test whether random hashes of the different strings fail properly.
    """
    def test_hash_comparison_invalid(self):
        rand_password = str(uuid.uuid4())
        rand_password2 = str(uuid.uuid4())

        hash = web.user_manager.hash_passwd(rand_password)
        user_mdl = utils.db_models.User(password=hash)

        self.assertFalse(web.user_manager.check_user_passwd(user_mdl,
                                                            rand_password2))

    """
    Test whether passwords requirement test isn't broken.
    """
    def test_password_requirements(self):
        rand_password = str(uuid.uuid4())
        bad_password = "abcd"

        self.assertTrue(web.user_manager
                        .check_password_requirements(rand_password))
        self.assertFalse(web.user_manager
                         .check_password_requirements(bad_password))



if __name__ == '__main__':
    unittest.main()
