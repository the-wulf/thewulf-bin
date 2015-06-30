import os.path
import unittest

from thewulf_bin.scripts import parse_card


resources = os.path.join(os.path.dirname(__file__), "resources")


class ConcertTestSuite(unittest.TestCase):
    def setUp(self):
        _card = os.path.join(resources, "concertcard.json")
        self.concert_card = parse_card.Card(_card)

    def test_card_ingestion(self):
        self.concert_card.parse()
        self.assertFalse(self.concert_card._has_errors)

    def test_card_with_errors(self):
        self.concert_card.parse()
        self.assertTrue(self.concert_card._loaded)
        # because i'm lazy i'm not going to write another one...
        self.concert_card._data["concert_date"] = ""
        with self.assertRaises(SystemExit):
            self.concert_card.check_data()

    def test_flush_card_with_errors(self):
        self.concert_card.parse()
        origional = self.concert_card.data["concert_date"]
        self.assertTrue(self.concert_card._loaded)
        # because i'm lazy i'm not going to write another one...
        self.concert_card._data["concert_date"] = ""
        with self.assertRaises(SystemExit):
            self.concert_card.check_data()

        data = self.concert_card.flush()
        self.assertEqual(data["concert_date"], origional)

    def test_time_tuples(self):
        times = self.concert_card.get_time_tuples()
        self.assertEqual(("02:50:10", "02:59:50"), times[0])

