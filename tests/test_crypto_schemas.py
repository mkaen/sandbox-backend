import unittest
from datetime import datetime

from src.constants import CryptoSentiment
from src.features.crypto.schemas import FearAndGreedIndexRespone


class FearAndGreedIndexResponseSchemaTests(unittest.TestCase):
    def test_serializes_from_orm_attributes(self):
        class OrmRow:
            created_at = datetime(2026, 11, 24, 13, 30, 0)  # UTC naive
            value = 19
            sentiment = CryptoSentiment.EXTREME_FEAR

        payload = FearAndGreedIndexRespone.model_validate(OrmRow()).model_dump(by_alias=True)
        self.assertEqual(
            payload,
            {
                "updatedAt": "15:30 24.11.2026",
                "value": 19,
                "sentiment": "EXTREME_FEAR",
            },
        )


if __name__ == "__main__":
    unittest.main()