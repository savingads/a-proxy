"""
Unit tests for BrowserManager._write_memento / _memento_paths.

These cover the shared persist pipeline extracted from archive_page,
archive_session_page, and capture_as_persona. They use a stub page and a
temporary working directory, so they need no real browser and no network
(requests.get is mocked). This is the first coverage of the archive/capture
persistence logic, which the browser-driving methods can't unit-test directly.
"""
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _read_json(path):
    with open(path) as f:
        return json.load(f)


class _StubPage:
    """Minimal stand-in for a Playwright Page."""

    def __init__(self, html="<html>hello</html>", title="Hello", url="https://example.com/"):
        self._html = html
        self._title = title
        self.url = url

    def title(self):
        return self._title

    def content(self):
        return self._html

    def screenshot(self, path, full_page=False):
        with open(path, "wb") as f:
            f.write(b"\x89PNG-stub")


class _FakeResponse:
    status_code = 200
    headers = {"Content-Type": "text/html; charset=utf-8"}
    content = b"abcdef"


class WriteMementoTest(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self._tmp = tempfile.mkdtemp()
        os.chdir(self._tmp)  # archives/ is created relative to cwd

    def tearDown(self):
        os.chdir(self._cwd)

    def _manager(self):
        from utils.browser import BrowserManager
        return BrowserManager.get_instance()

    def test_writes_artifacts_and_merges_extra_metadata(self):
        mgr = self._manager()
        page = _StubPage()
        with mock.patch("utils.browser.requests.get", return_value=_FakeResponse()):
            result = mgr._write_memento(
                page, "https://example.com/",
                locale="en-US", persona_id=7,
                extra_metadata={"language": "en-US", "geolocation": None},
                save_to_db=False,
            )

        md = result["memento_location"]
        self.assertTrue(os.path.exists(os.path.join(md, "content.html")))
        self.assertTrue(os.path.exists(os.path.join(md, "screenshot.png")))

        meta = _read_json(os.path.join(md, "metadata.json"))
        self.assertEqual(meta["url"], "https://example.com/")
        self.assertEqual(meta["title"], "Hello")
        self.assertEqual(meta["persona_id"], 7)
        self.assertEqual(meta["http_status"], 200)
        self.assertEqual(meta["content_type"], "text/html; charset=utf-8")
        self.assertEqual(meta["language"], "en-US")  # extra_metadata merged in
        self.assertIsNone(meta["geolocation"])

        # URL-level index records this memento's timestamp.
        url_meta = _read_json(os.path.join(os.path.dirname(md), "metadata.json"))
        self.assertIn(meta["timestamp"], url_meta["mementos"])

        # save_to_db=False -> no DB identifiers in the result.
        self.assertNotIn("archived_website_id", result)
        self.assertNotIn("memento_id", result)
        self.assertEqual(result["title"], "Hello")
        self.assertEqual(result["http_status"], 200)

    def test_honors_precomputed_memento_dir(self):
        """capture_as_persona pre-creates the dir (for HAR/video) and passes it in."""
        mgr = self._manager()
        url_dir, memento_dir, ts = mgr._memento_paths("https://example.com/x")
        self.assertTrue(os.path.isdir(memento_dir))

        page = _StubPage(url="https://example.com/x")
        with mock.patch("utils.browser.requests.get", return_value=_FakeResponse()):
            result = mgr._write_memento(
                page, "https://example.com/x",
                memento_dir=memento_dir, timestamp=ts, save_to_db=False,
                extra_metadata={"final_url": "https://example.com/x"},
            )

        self.assertEqual(result["memento_location"], memento_dir)
        meta = _read_json(os.path.join(memento_dir, "metadata.json"))
        self.assertEqual(meta["timestamp"], ts)
        self.assertEqual(meta["final_url"], "https://example.com/x")

    def test_survives_http_fetch_failure(self):
        """A failed requests.get must not abort the memento write."""
        mgr = self._manager()
        page = _StubPage()
        with mock.patch("utils.browser.requests.get", side_effect=Exception("no network")):
            result = mgr._write_memento(
                page, "https://example.com/", save_to_db=False,
            )
        self.assertIsNone(result["http_status"])
        self.assertTrue(os.path.exists(os.path.join(result["memento_location"], "content.html")))


if __name__ == "__main__":
    unittest.main()
