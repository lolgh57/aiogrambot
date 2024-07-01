import unittest
from app.handlers import filter_answers


class FilterAnswersTestCase(unittest.TestCase):
    def test_filter_answers(self):
        data = {
            'age': '14',
            'played': 'Нет',
            'players': '5',
            'scary': 'Страшный'
        }

        # Call the function
        filtered_quests = filter_answers(data)

        # Assert the result
        self.assertEqual(len(filtered_quests), 1)
        self.assertEqual(filtered_quests[0]['name'], 'Оно')


if __name__ == '__main__':
    unittest.main()
