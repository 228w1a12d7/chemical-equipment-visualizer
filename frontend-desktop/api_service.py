"""
API Service for Chemical Equipment Visualizer Desktop App
Handles all communication with the Django REST API backend
"""

import requests
from typing import Optional, Dict, Any, List


class APIService:
    """Service class for API communication with the backend."""
    
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.session = requests.Session()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for authenticated requests."""
        headers = {
            "Content-Type": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        return headers
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> requests.Response:
        """Make HTTP request to the API."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        # Don't set Content-Type for file uploads
        if files:
            headers.pop("Content-Type", None)
        
        response = self.session.request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            files=files,
            json=json_data
        )
        return response
    
    # Authentication endpoints
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login user and store token."""
        response = self._make_request(
            "POST",
            "/auth/login/",
            json_data={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token")
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": response.json().get("error", "Login failed")}
    
    def register(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Register a new user."""
        response = self._make_request(
            "POST",
            "/auth/register/",
            json_data={
                "username": username, 
                "email": email, 
                "password": password,
                "password_confirm": password
            }
        )
        
        if response.status_code == 201:
            data = response.json()
            self.token = data.get("token")
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": response.json()}
    
    def logout(self) -> Dict[str, Any]:
        """Logout user and clear token."""
        response = self._make_request("POST", "/auth/logout/")
        self.token = None
        return {"success": response.status_code == 200}
    
    def get_user(self) -> Dict[str, Any]:
        """Get current user information."""
        response = self._make_request("GET", "/auth/user/")
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": "Failed to get user"}
    
    # Data endpoints
    def upload_csv(self, file_path: str) -> Dict[str, Any]:
        """Upload a CSV file for analysis."""
        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_path.split("/")[-1], f, "text/csv")}
                response = self._make_request("POST", "/upload/", files=files)
            
            if response.status_code in [200, 201]:
                return {"success": True, "data": response.json()}
            else:
                error = response.json().get("error", "Upload failed")
                return {"success": False, "error": error}
        except FileNotFoundError:
            return {"success": False, "error": "File not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_history(self) -> Dict[str, Any]:
        """Get upload history (last 5 datasets)."""
        response = self._make_request("GET", "/datasets/")
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": "Failed to fetch history"}
    
    def get_dataset(self, dataset_id: int) -> Dict[str, Any]:
        """Get a specific dataset by ID."""
        response = self._make_request("GET", f"/datasets/{dataset_id}/")
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": "Dataset not found"}
    
    def delete_dataset(self, dataset_id: int) -> Dict[str, Any]:
        """Delete a dataset."""
        response = self._make_request("DELETE", f"/datasets/{dataset_id}/delete/")
        
        if response.status_code in [200, 204]:
            return {"success": True}
        else:
            return {"success": False, "error": "Failed to delete dataset"}
    
    def download_pdf(self, dataset_id: int, save_path: str) -> Dict[str, Any]:
        """Download PDF report for a dataset."""
        url = f"{self.base_url}/datasets/{dataset_id}/pdf/"
        headers = self._get_headers()
        headers.pop("Content-Type", None)
        
        try:
            response = self.session.get(url, headers=headers)
            
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                return {"success": True, "path": save_path}
            else:
                return {"success": False, "error": "Failed to generate PDF"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.token is not None
    
    def set_token(self, token: str) -> None:
        """Set authentication token."""
        self.token = token
    
    def clear_token(self) -> None:
        """Clear authentication token."""
        self.token = None


# Global API instance
api = APIService()
