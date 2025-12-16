"""
Tests for authentication endpoints.
"""
import pytest
from fastapi import status


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    def test_login_success(self, client, test_user_data):
        """Test successful user login."""
        response = client.post("/api/v1/auth/login", json=test_user_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        invalid_data = {
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", json=invalid_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_login_invalid_email_format(self, client):
        """Test login with invalid email format."""
        invalid_data = {
            "email": "invalid-email",
            "password": "password123"
        }
        response = client.post("/api/v1/auth/login", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_logout(self, client):
        """Test user logout."""
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Successfully logged out"
    
    def test_get_current_user_success(self, client, auth_headers):
        """Test getting current user with valid token."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "username" in data
        assert data["email"] == "test@example.com"
    
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_verify_token_valid(self, client, auth_headers):
        """Test token verification with valid token."""
        response = client.post("/api/v1/auth/verify-token", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["valid"] is True
    
    def test_verify_token_invalid(self, client):
        """Test token verification with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post("/api/v1/auth/verify-token", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["valid"] is False
    
    def test_change_password_success(self, client, auth_headers, test_user_data):
        """Test successful password change."""
        password_data = {
            "current_password": test_user_data["password"],
            "new_password": "NewPassword123"
        }
        response = client.post("/api/v1/auth/change-password", json=password_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Password changed successfully"
    
    def test_change_password_wrong_current(self, client, auth_headers):
        """Test password change with wrong current password."""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "NewPassword123"
        }
        response = client.post("/api/v1/auth/change-password", json=password_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Incorrect current password" in response.json()["detail"]
    
    def test_change_password_weak_new(self, client, auth_headers, test_user_data):
        """Test password change with weak new password."""
        password_data = {
            "current_password": test_user_data["password"],
            "new_password": "weak"
        }
        response = client.post("/api/v1/auth/change-password", json=password_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
