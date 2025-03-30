import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import json
import requests

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import vpn

class MockResponse:
    """Mock class for requests.Response"""
    
    def __init__(self, json_data, status_code, raise_for_status=None):
        self.json_data = json_data
        self.status_code = status_code
        self.raise_for_status = raise_for_status or (lambda: None)
    
    def json(self):
        return self.json_data

class TestVpnUtils(unittest.TestCase):
    """Test cases for VPN utility functions"""
    
    @patch('subprocess.run')
    def test_is_vpn_running_true(self, mock_run):
        """Test is_vpn_running when VPN is running"""
        # Mock the subprocess.run to return a successful exit code (0)
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        # Call the function and check the result
        result = vpn.is_vpn_running()
        
        # Verify subprocess.run was called with correct arguments
        mock_run.assert_called_once_with(["pgrep", "openvpn"], stdout=-1)
        
        # Check that the function returns True
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_is_vpn_running_false(self, mock_run):
        """Test is_vpn_running when VPN is not running"""
        # Mock the subprocess.run to return a non-zero exit code
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_run.return_value = mock_process
        
        # Call the function and check the result
        result = vpn.is_vpn_running()
        
        # Verify subprocess.run was called with correct arguments
        mock_run.assert_called_once_with(["pgrep", "openvpn"], stdout=-1)
        
        # Check that the function returns False
        self.assertFalse(result)
    
    @patch('requests.get')
    def test_get_ip_info_success(self, mock_get):
        """Test get_ip_info with successful response"""
        # Sample IP info response
        ip_info = {
            "ip": "203.0.113.1",
            "hostname": "example.host.com",
            "city": "New York",
            "region": "NY",
            "country": "US",
            "loc": "40.7128,-74.0060",
            "org": "Example ISP"
        }
        
        # Mock the requests.get to return a successful response
        mock_response = MockResponse(ip_info, 200)
        mock_get.return_value = mock_response
        
        # Call the function and check the result
        result = vpn.get_ip_info()
        
        # Verify requests.get was called with correct URL
        mock_get.assert_called_once_with("https://ipinfo.io")
        
        # Check that the function returns the expected IP info
        self.assertEqual(result, ip_info)
    
    @patch('requests.get')
    def test_get_ip_info_connection_error(self, mock_get):
        """Test get_ip_info with connection error"""
        # Mock the requests.get to raise a ConnectionError
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection error")
        
        # Call the function and check the result
        result = vpn.get_ip_info()
        
        # Check that the function returns an error dictionary
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Failed to get IP info")
    
    @patch('requests.get')
    def test_get_ip_info_rate_limit(self, mock_get):
        """Test get_ip_info with rate limit response"""
        # Mock the requests.get to raise a RequestException with 429 status code
        mock_response = MockResponse({}, 429)
        def raise_for_status():
            raise requests.exceptions.RequestException("Rate limited")
        mock_response.raise_for_status = raise_for_status
        mock_get.return_value = mock_response
        
        # Call the function and check the result (with mocked time.sleep to avoid actual waiting)
        with patch('time.sleep') as mock_sleep:
            result = vpn.get_ip_info()
        
        # Check that the function returns an error dictionary after retries
        self.assertIn("error", result)
    
    @patch('utils.vpn.is_vpn_running')
    @patch('utils.vpn.get_ip_info')
    @patch('time.sleep')
    def test_wait_for_vpn_and_get_ip_info_success(self, mock_sleep, mock_get_ip_info, mock_is_vpn_running):
        """Test wait_for_vpn_and_get_ip_info with successful scenario"""
        # Mock is_vpn_running to return True
        mock_is_vpn_running.return_value = True
        
        # Sample IP info response
        ip_info = {
            "ip": "203.0.113.1",
            "city": "New York",
            "region": "NY",
            "country": "US",
            "loc": "40.7128,-74.0060"
        }
        
        # Mock get_ip_info to return the sample IP info
        mock_get_ip_info.return_value = ip_info
        
        # Call the function and check the result
        result = vpn.wait_for_vpn_and_get_ip_info()
        
        # Verify is_vpn_running and get_ip_info were called
        mock_is_vpn_running.assert_called_once()
        mock_get_ip_info.assert_called_once()
        
        # Verify time.sleep was not called (no waiting needed)
        mock_sleep.assert_not_called()
        
        # Check that the function returns the expected IP info
        self.assertEqual(result, ip_info)
    
    @patch('utils.vpn.is_vpn_running')
    @patch('utils.vpn.get_ip_info')
    @patch('time.sleep')
    def test_wait_for_vpn_and_get_ip_info_retry(self, mock_sleep, mock_get_ip_info, mock_is_vpn_running):
        """Test wait_for_vpn_and_get_ip_info with retry scenario"""
        # Mock is_vpn_running to return False then True
        mock_is_vpn_running.side_effect = [False, True]
        
        # Sample IP info response
        ip_info = {
            "ip": "203.0.113.1",
            "city": "New York",
            "region": "NY",
            "country": "US",
            "loc": "40.7128,-74.0060"
        }
        
        # Mock get_ip_info to return the sample IP info
        mock_get_ip_info.return_value = ip_info
        
        # Call the function and check the result
        result = vpn.wait_for_vpn_and_get_ip_info()
        
        # Verify is_vpn_running was called twice
        self.assertEqual(mock_is_vpn_running.call_count, 2)
        
        # Verify get_ip_info was called once
        mock_get_ip_info.assert_called_once()
        
        # Verify time.sleep was called once
        mock_sleep.assert_called_once()
        
        # Check that the function returns the expected IP info
        self.assertEqual(result, ip_info)
    
    @patch('utils.vpn.is_vpn_running')
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_vpn_process_with_region(self, mock_exists, mock_run, mock_is_vpn_running):
        """Test vpn_process with a specified region"""
        # Mock is_vpn_running to return False (VPN not running)
        mock_is_vpn_running.return_value = False
        
        # Mock os.path.exists to return True for both config and auth files
        mock_exists.return_value = True
        
        # Call the function with a region
        region = "us1234"
        
        # Need to patch time.sleep to avoid actual waiting and patch multiprocessing
        with patch('time.sleep') as mock_sleep:
            vpn.vpn_process(region)
        
        # Verify subprocess.run was called with the correct arguments
        # (Since the VPN was not running, we should only have one call to start the VPN)
        mock_run.assert_called_once_with([
            "sudo", "openvpn", "--config", 
            f"nordvpn/ovpn_udp/{region}.nordvpn.com.udp.ovpn", 
            "--auth-user-pass", "nordvpn/auth.txt"
        ])
    
    @patch('utils.vpn.is_vpn_running')
    @patch('subprocess.run')
    @patch('time.sleep')
    def test_vpn_process_stop_and_restart(self, mock_sleep, mock_run, mock_is_vpn_running):
        """Test vpn_process when VPN is already running"""
        # Mock is_vpn_running to return True (VPN running)
        mock_is_vpn_running.return_value = True
        
        # Mock os.path.exists to return True for both config and auth files
        with patch('os.path.exists', return_value=True):
            # Call the function with a region
            region = "us1234"
            vpn.vpn_process(region)
        
        # Verify subprocess.run was called twice
        # First call to kill the running VPN, second call to start a new one
        self.assertEqual(mock_run.call_count, 2)
        
        # Verify the first call was to kill the VPN
        mock_run.assert_any_call(["sudo", "pkill", "openvpn"])
        
        # Verify the second call was to start the VPN with the new region
        mock_run.assert_any_call([
            "sudo", "openvpn", "--config", 
            f"nordvpn/ovpn_udp/{region}.nordvpn.com.udp.ovpn", 
            "--auth-user-pass", "nordvpn/auth.txt"
        ])
        
        # Verify time.sleep was called to wait for the VPN to stop
        mock_sleep.assert_called_once_with(5)

if __name__ == '__main__':
    unittest.main()
