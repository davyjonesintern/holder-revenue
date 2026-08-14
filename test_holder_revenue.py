import json
import unittest
from pathlib import Path
from io import BytesIO

import holder_revenue


class FakeResp:
    def __init__(self, payload):
        self._payload = json.dumps(payload).encode()

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class HolderRevenueTest(unittest.TestCase):
    def setUp(self):
        raw = json.loads(Path(__file__).with_name("testdata").joinpath("snapshot.json").read_text())
        self.payloads = raw

    def opener(self, req, timeout=30):
        url = req.full_url
        slug = url.split("/fees/")[1].split("?")[0]
        kind = "holders" if "Holders" in url else "protocol"
        # rebuild llama chart from totals is not needed; use canned charts
        data = self.payloads[slug][kind]
        return FakeResp(data)

    def test_uniswap_matches(self):
        row = holder_revenue.summarise("uniswap", opener=self.opener)
        self.assertTrue(row["paid"])
        self.assertGreater(row["holders"]["total"], 0)

    def test_aave_unpaid(self):
        row = holder_revenue.summarise("aave", opener=self.opener)
        self.assertFalse(row["paid"])
        self.assertEqual(row["holders"]["total"], 0)

    def test_render_lists_slugs(self):
        rows = [holder_revenue.summarise(s, opener=self.opener) for s in ("aave", "uniswap", "lido")]
        text = holder_revenue.render(rows)
        self.assertIn("aave", text)
        self.assertIn("uniswap", text)
        self.assertIn("lido", text)


if __name__ == "__main__":
    unittest.main()
