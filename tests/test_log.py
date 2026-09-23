from unittest import TestCase
from datetime import datetime

from src.log import Check


class TestLog(TestCase):
    def test(self):
        self.assertEqual(Check.size(), 8)

        check1 = Check(ts_min=3538919, track_id=24, ok=1)

        self.assertEqual(check1.timestamp, datetime(2026, 9, 23, 13, 59))

        self.assertEqual(check1.pack(), b'\xe7\xff5\x00\x18\x00\x01\x00')
        self.assertEqual(
            Check.unpack(b'\xe7\xff5\x00\x18\x00\x01\x00'), check1
        )

        check2 = Check(ts_min=3538920, track_id=24, ok=0)

        self.assertListEqual(
            list(Check.iter_load(
                b'\xe7\xff5\x00\x18\x00\x01\x00\xe8\xff5\x00\x18\x00\x00\x00'
            )), [check1, check2]
        )
