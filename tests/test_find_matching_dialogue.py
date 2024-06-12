import unittest
from unittest.mock import patch
import utils  # Replace 'your_module' with the name of your Python file containing the functions.


class TestFindMatchingDialogue(unittest.TestCase):
    @patch("your_module.ast.literal_eval")
    @patch("your_module.TfidfVectorizer")
    def test_find_matching_dialogue(self, mock_vectorizer, mock_literal_eval):
        # Setup mock
        mock_literal_eval.return_value = [
            {"text": "Who will last the longest", "start": 10, "duration": 5},
            {"text": "Keep your hand on the Lamborghini", "start": 15, "duration": 7},
            {"text": "This is the final challenge", "start": 22, "duration": 5},
        ]
        instance = mock_vectorizer.return_value
        instance.fit.return_value = instance
        instance.transform.return_value = [
            "vector1",
            "vector2",
            "vector3",
            "key_phrase_vector",
        ]
        instance.cosine_similarity.return_value = [[0.1, 0.9, 0.2]]

        # Call function
        result = utils.find_matching_dialogue(
            '[{"text": "Who will last the longest", "start": 10, "duration": 5}, {"text": "Keep your hand on the Lamborghini", "start": 15, "duration": 7}, {"text": "This is the final challenge", "start": 22, "duration": 5}]',
            "nywT2SenPIo",
            "Lamborghini",
            2,
        )

        # Assert
        self.assertIn("https://www.youtube.com/watch?v=nywT2SenPIo&t=10s", result)
        self.assertIn(
            "Who will last the longest Keep your hand on the Lamborghini", result
        )


if __name__ == "__main__":
    unittest.main()
