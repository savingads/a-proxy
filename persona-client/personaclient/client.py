"""
API client for interacting with the Persona Service
"""
import json
import logging
from typing import Dict, List, Optional, Union, Any
import requests
from pydantic import BaseModel, ValidationError
from personaclient.exceptions import (
    PersonaClientError,
    PersonaNotFoundError,
    PersonaValidationError,
    PersonaAPIError
)

# Set up logging
logger = logging.getLogger(__name__)


class PersonaClient:
    """Client for interacting with the Persona API Service"""

    def __init__(
            self,
            base_url: str = "http://localhost:5050",
            api_version: str = "v1",
            timeout: int = 10,
            auth_token: Optional[str] = None
    ):
        """
        Initialize the Persona API client

        Args:
            base_url: Base URL of the Persona API service
            api_version: API version to use
            timeout: Request timeout in seconds
            auth_token: JWT authentication token (if required)
        """
        self.base_url = base_url.rstrip("/")
        self.api_version = api_version
        self.timeout = timeout
        self.auth_token = auth_token
        self.api_url = f"{self.base_url}/api/{self.api_version}"

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers including auth token if available"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    def _handle_response(self, response: requests.Response, persona_id: Optional[int] = None) -> Dict:
        """
        Handle API response and handle errors appropriately

        Args:
            response: Response object from requests
            persona_id: ID of the persona being requested (for 404 errors)

        Returns:
            Response data as dictionary

        Raises:
            PersonaNotFoundError: When persona is not found (404)
            PersonaValidationError: When there's a validation error (400)
            PersonaAPIError: For other API errors
        """
        try:
            data = response.json()
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response: {response.text}")
            raise PersonaAPIError(
                f"Invalid JSON response from API: {response.text[:100]}...",
                response.status_code,
                response
            )

        if response.status_code >= 400:
            message = data.get("message", "Unknown error")
            errors = data.get("errors")

            if response.status_code == 404 and persona_id:
                raise PersonaNotFoundError(persona_id, response.status_code, response)
            elif response.status_code == 400:
                raise PersonaValidationError(message, errors, response.status_code, response)
            else:
                raise PersonaAPIError(message, response.status_code, response)

        return data

    def get_all_personas(self, page: int = 1, per_page: int = 20) -> Dict:
        """
        Get all personas with pagination

        Args:
            page: Page number
            per_page: Number of items per page

        Returns:
            Dictionary with personas and pagination info
        """
        url = f"{self.api_url}/personas"
        params = {"page": page, "per_page": per_page}

        try:
            response = requests.get(
                url,
                params=params,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise PersonaClientError(f"Request failed: {str(e)}")

    def get_persona(self, persona_id: int) -> Dict:
        """
        Get a specific persona by ID

        Args:
            persona_id: ID of the persona to retrieve

        Returns:
            Persona data as dictionary

        Raises:
            PersonaNotFoundError: When persona is not found
        """
        url = f"{self.api_url}/personas/{persona_id}"

        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            return self._handle_response(response, persona_id)
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise PersonaClientError(f"Request failed: {str(e)}")

    def create_persona(self, persona_data: Dict) -> Dict:
        """
        Create a new persona

        Args:
            persona_data: Dictionary with persona data

        Returns:
            Created persona data

        Raises:
            PersonaValidationError: When data validation fails
        """
        url = f"{self.api_url}/personas"

        try:
            response = requests.post(
                url,
                json=persona_data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise PersonaClientError(f"Request failed: {str(e)}")

    def update_persona(self, persona_id: int, persona_data: Dict) -> Dict:
        """
        Update an existing persona

        Args:
            persona_id: ID of the persona to update
            persona_data: Dictionary with updated persona data

        Returns:
            Updated persona data

        Raises:
            PersonaNotFoundError: When persona is not found
            PersonaValidationError: When data validation fails
        """
        url = f"{self.api_url}/personas/{persona_id}"

        try:
            response = requests.put(
                url,
                json=persona_data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            return self._handle_response(response, persona_id)
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise PersonaClientError(f"Request failed: {str(e)}")

    def delete_persona(self, persona_id: int) -> Dict:
        """
        Delete a persona

        Args:
            persona_id: ID of the persona to delete

        Returns:
            Response message

        Raises:
            PersonaNotFoundError: When persona is not found
        """
        url = f"{self.api_url}/personas/{persona_id}"

        try:
            response = requests.delete(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            return self._handle_response(response, persona_id)
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise PersonaClientError(f"Request failed: {str(e)}")

    # Methods for demographic data
    def get_demographic_data(self, persona_id: int) -> Dict:
        """Get demographic data for a persona"""
        url = f"{self.api_url}/personas/{persona_id}/demographic"

        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            return self._handle_response(response, persona_id)
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise PersonaClientError(f"Request failed: {str(e)}")

    def update_demographic_data(self, persona_id: int, demographic_data: Dict) -> Dict:
        """Update demographic data for a persona"""
        url = f"{self.api_url}/personas/{persona_id}/demographic"

        try:
            response = requests.put(
                url,
                json=demographic_data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            return self._handle_response(response, persona_id)
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise PersonaClientError(f"Request failed: {str(e)}")

    # Methods for psychographic data
    def get_psychographic_data(self, persona_id: int) -> Dict:
        """Get psychographic data for a persona"""
        url = f"{self.api_url}/personas/{persona_id}/psychographic"

        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            return self._handle_response(response, persona_id)
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise PersonaClientError(f"Request failed: {str(e)}")

    def update_psychographic_data(self, persona_id: int, psychographic_data: Dict) -> Dict:
        """Update psychographic data for a persona"""
        url = f"{self.api_url}/personas/{persona_id}/psychographic"

        try:
            response = requests.put(
                url,
                json=psychographic_data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            return self._handle_response(response, persona_id)
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise PersonaClientError(f"Request failed: {str(e)}")

    # Methods for behavioral data
    def get_behavioral_data(self, persona_id: int) -> Dict:
        """Get behavioral data for a persona"""
        url = f"{self.api_url}/personas/{persona_id}/behavioral"

        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            return self._handle_response(response, persona_id)
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise PersonaClientError(f"Request failed: {str(e)}")

    def update_behavioral_data(self, persona_id: int, behavioral_data: Dict) -> Dict:
        """Update behavioral data for a persona"""
        url = f"{self.api_url}/personas/{persona_id}/behavioral"

        try:
            response = requests.put(
                url,
                json=behavioral_data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            return self._handle_response(response, persona_id)
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise PersonaClientError(f"Request failed: {str(e)}")

    # Methods for contextual data
    def get_contextual_data(self, persona_id: int) -> Dict:
        """Get contextual data for a persona"""
        url = f"{self.api_url}/personas/{persona_id}/contextual"

        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            return self._handle_response(response, persona_id)
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise PersonaClientError(f"Request failed: {str(e)}")

    def update_contextual_data(self, persona_id: int, contextual_data: Dict) -> Dict:
        """Update contextual data for a persona"""
        url = f"{self.api_url}/personas/{persona_id}/contextual"

        try:
            response = requests.put(
                url,
                json=contextual_data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            return self._handle_response(response, persona_id)
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise PersonaClientError(f"Request failed: {str(e)}")
