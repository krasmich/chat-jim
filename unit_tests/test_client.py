import sys
import os
import unittest
sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from client import presence_message, processing_answer


class TestClass(unittest.TestCase):
    """
    Класс, который тестирует клиентскую часть
    """

    def test_def_presense(self):
        test = presence_message()
        test[TIME] = 1.1
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'krasmich'}})

    def test_200_ans(self):
        self.assertEqual(processing_answer({RESPONSE: 200}), '200 : OK')

    def test_400_ans(self):
        self.assertEqual(processing_answer({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_no_response(self):
        self.assertRaises(ValueError, processing_answer, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
