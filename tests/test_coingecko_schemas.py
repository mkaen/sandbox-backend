import unittest

from src.constants import CryptoSentiment
from src.providers.coingecko.schemas import CoinGeckoGlobalResponse


class CoinGeckoGlobalResponseTests(unittest.TestCase):
    def test_parses_fear_and_greed_from_global_payload(self):
        payload = {
            "data": {
                "active_cryptocurrencies": 21258,
                "updated_at": 1795553626,
                "fear_and_greed_index": {"value": 19, "sentiment": "extreme_fear"},
            }
        }
        parsed = CoinGeckoGlobalResponse.model_validate(payload)
        self.assertEqual(parsed.data.fear_and_greed_index.value, 19)
        self.assertEqual(parsed.data.fear_and_greed_index.sentiment, CryptoSentiment.EXTREME_FEAR)
        self.assertEqual(parsed.data.updated_at, 1795553626)


if __name__ == "__main__":
    unittest.main()