import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import network


class MockResponse:
    """Mock class for requests.Response"""

    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            raise requests.exceptions.HTTPError(response=self)


class TestNetworkUtils(unittest.TestCase):
    """Test cases for network utility functions"""

    @patch('utils.network.PROXY_URL', 'socks5://proxy:1080')
    def test_is_proxy_configured_true(self):
        """Test is_proxy_configured when PROXY_URL is set"""
        self.assertTrue(network.is_proxy_configured())

    @patch('utils.network.PROXY_URL', None)
    def test_is_proxy_configured_false(self):
        """Test is_proxy_configured when PROXY_URL is not set"""
        self.assertFalse(network.is_proxy_configured())

    @patch('utils.network.PROXY_URL', 'socks5://proxy:1080')
    def test_get_proxy_url(self):
        """Test get_proxy_url returns the configured URL"""
        self.assertEqual(network.get_proxy_url(), 'socks5://proxy:1080')

    @patch('utils.network.PROXY_URL', None)
    def test_get_proxy_url_none(self):
        """Test get_proxy_url returns None when not configured"""
        self.assertIsNone(network.get_proxy_url())

    @patch('requests.get')
    def test_get_ip_info_success(self, mock_get):
        """Test get_ip_info with successful response"""
        ip_info = {
            "ip": "203.0.113.1",
            "city": "New York",
            "region": "NY",
            "country": "US",
            "loc": "40.7128,-74.0060",
            "org": "Example ISP",
        }
        mock_get.return_value = MockResponse(ip_info, 200)

        result = network.get_ip_info()

        mock_get.assert_called_once_with("https://ipinfo.io", proxies=None, timeout=10)
        self.assertEqual(result, ip_info)

    @patch('requests.get')
    def test_get_ip_info_with_proxy(self, mock_get):
        """Test get_ip_info routes through proxy when provided"""
        ip_info = {"ip": "10.0.0.1", "country": "DE"}
        mock_get.return_value = MockResponse(ip_info, 200)

        proxy_url = "socks5://proxy:1080"
        result = network.get_ip_info(proxy_url)

        expected_proxies = {"http": proxy_url, "https": proxy_url}
        mock_get.assert_called_once_with("https://ipinfo.io", proxies=expected_proxies, timeout=10)
        self.assertEqual(result, ip_info)

    @patch('requests.get')
    def test_get_ip_info_connection_error(self, mock_get):
        """Test get_ip_info with connection error"""
        import requests as req
        mock_get.side_effect = req.exceptions.ConnectionError("Connection error")

        result = network.get_ip_info()

        self.assertIn("error", result)
        self.assertEqual(result["error"], "Failed to get IP info")


class TestBrowserManager(unittest.TestCase):
    """Test cases for BrowserManager"""

    def test_singleton(self):
        """Test that get_instance returns the same instance"""
        from utils.browser import BrowserManager
        instance1 = BrowserManager.get_instance()
        instance2 = BrowserManager.get_instance()
        self.assertIs(instance1, instance2)

        # Reset singleton for other tests
        BrowserManager._instance = None
        BrowserManager._browser = None
        BrowserManager._playwright = None


if __name__ == '__main__':
    unittest.main()
