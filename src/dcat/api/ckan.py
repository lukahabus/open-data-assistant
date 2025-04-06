"""
CKAN API client for interacting with CKAN portals.
"""

import json
from typing import Any, Dict, List, Optional
import urllib.parse
import requests
from requests.exceptions import RequestException


class CKANError(Exception):
    """Base exception for CKAN API errors."""

    pass


class CKANClient:
    """Client for interacting with CKAN API."""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """Initialize CKAN client.

        Args:
            base_url: Base URL of the CKAN instance
            api_key: Optional API key for authenticated requests
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": api_key})

    def _make_request(
        self, action: str, data: Optional[Dict[str, Any]] = None, method: str = "GET"
    ) -> Dict[str, Any]:
        """Make a request to the CKAN API.

        Args:
            action: CKAN API action
            data: Request data
            method: HTTP method

        Returns:
            API response

        Raises:
            CKANError: If the request fails
        """
        url = f"{self.base_url}/api/3/action/{action}"

        try:
            if method == "GET":
                if data:
                    query_string = urllib.parse.urlencode(data)
                    url = f"{url}?{query_string}"
                response = self.session.get(url)
            else:
                response = self.session.post(url, json=data)

            response.raise_for_status()
            result = response.json()

            if not result["success"]:
                raise CKANError(
                    f"CKAN API error: {result.get('error', {}).get('message', 'Unknown error')}"
                )

            return result["result"]

        except RequestException as e:
            raise CKANError(f"Request failed: {str(e)}")
        except json.JSONDecodeError:
            raise CKANError("Invalid JSON response")
        except KeyError:
            raise CKANError("Unexpected response format")

    def get_package_list(self) -> List[str]:
        """Get list of all package names."""
        return self._make_request("package_list")

    def get_package(self, package_id: str) -> Dict[str, Any]:
        """Get package metadata."""
        return self._make_request("package_show", {"id": package_id})

    def get_organization_list(self, all_fields: bool = True) -> List[Dict[str, Any]]:
        """Get list of organizations."""
        return self._make_request("organization_list", {"all_fields": all_fields})

    def get_organization(
        self, org_id: str, include_datasets: bool = True
    ) -> Dict[str, Any]:
        """Get organization details."""
        return self._make_request(
            "organization_show", {"id": org_id, "include_datasets": include_datasets}
        )

    def search_packages(
        self,
        q: Optional[str] = None,
        fq: Optional[str] = None,
        rows: int = 10,
        start: int = 0,
        sort: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Search for packages.

        Args:
            q: Search query
            fq: Filter query
            rows: Number of results to return
            start: Result offset
            sort: Sort order
            **kwargs: Additional search parameters

        Returns:
            Search results
        """
        data = {"rows": rows, "start": start}

        if q:
            data["q"] = q
        if fq:
            data["fq"] = fq
        if sort:
            data["sort"] = sort

        data.update(kwargs)

        return self._make_request("package_search", data)

    def create_package(self, package_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new package."""
        return self._make_request("package_create", package_dict, method="POST")

    def update_package(self, package_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing package."""
        return self._make_request("package_update", package_dict, method="POST")

    def delete_package(self, package_id: str) -> Dict[str, Any]:
        """Delete a package."""
        return self._make_request("package_delete", {"id": package_id}, method="POST")

    def get_resource(self, resource_id: str) -> Dict[str, Any]:
        """Get resource metadata."""
        return self._make_request("resource_show", {"id": resource_id})

    def create_resource(
        self, package_id: str, resource_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new resource."""
        resource_dict["package_id"] = package_id
        return self._make_request("resource_create", resource_dict, method="POST")

    def update_resource(self, resource_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing resource."""
        return self._make_request("resource_update", resource_dict, method="POST")

    def delete_resource(self, resource_id: str) -> Dict[str, Any]:
        """Delete a resource."""
        return self._make_request("resource_delete", {"id": resource_id}, method="POST")

    def get_tag_list(self) -> List[Dict[str, Any]]:
        """Get list of all tags."""
        return self._make_request("tag_list", {"all_fields": True})

    def get_group_list(self) -> List[Dict[str, Any]]:
        """Get list of all groups."""
        return self._make_request("group_list", {"all_fields": True})

    def get_license_list(self) -> List[Dict[str, Any]]:
        """Get list of all licenses."""
        return self._make_request("license_list")

    def get_site_stats(self) -> Dict[str, Any]:
        """Get site statistics."""
        return self._make_request("site_read")

    def check_if_package_exists(self, package_id: str) -> bool:
        """Check if a package exists."""
        try:
            self.get_package(package_id)
            return True
        except CKANError:
            return False

    def get_package_revisions(self, package_id: str) -> List[Dict[str, Any]]:
        """Get revision history of a package."""
        return self._make_request("package_revision_list", {"id": package_id})

    def get_organization_packages(
        self, org_id: str, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all packages for an organization."""
        return self._make_request(
            "organization_show",
            {"id": org_id, "include_datasets": True, "limit": limit, "offset": offset},
        )["packages"]
