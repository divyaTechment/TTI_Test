"""
Tests for user management endpoints.
"""
import pytest
from fastapi import status


class TestUserEndpoints:
    """Test user management endpoints."""
    
    def test_create_user_success(self, client):
        """Test successful user creation."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "NewPassword123"
        }
        response = client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        assert "hashed_password" not in data  # Password should not be returned
    
    def test_create_user_duplicate_email(self, client, test_user_data):
        """Test user creation with duplicate email."""
        response = client.post("/api/v1/users/", json=test_user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]
    
    def test_create_user_duplicate_username(self, client, test_user_data):
        """Test user creation with duplicate username."""
        user_data = test_user_data.copy()
        user_data["email"] = "different@example.com"
        response = client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already taken" in response.json()["detail"]
    
    def test_create_user_invalid_data(self, client):
        """Test user creation with invalid data."""
        user_data = {
            "email": "invalid-email",
            "username": "ab",  # Too short
            "password": "weak"  # Too weak
        }
        response = client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_users_success(self, client, auth_headers):
        """Test getting users list."""
        response = client.get("/api/v1/users/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the test user
    
    def test_get_users_with_filters(self, client, auth_headers):
        """Test getting users with filters."""
        response = client.get("/api/v1/users/?is_active=true", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # All returned users should be active
        for user in data:
            assert user["is_active"] is True
    
    def test_get_users_pagination(self, client, auth_headers):
        """Test getting users with pagination."""
        response = client.get("/api/v1/users/?skip=0&limit=1", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 1
    
    def test_get_my_profile(self, client, auth_headers):
        """Test getting current user profile."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
    
    def test_get_user_by_id_success(self, client, auth_headers, test_user):
        """Test getting user by ID."""
        response = client.get(f"/api/v1/users/{test_user.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
    
    def test_get_user_by_id_not_found(self, client, auth_headers):
        """Test getting non-existent user by ID."""
        response = client.get("/api/v1/users/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in response.json()["detail"]
    
    def test_get_user_by_id_forbidden(self, client, auth_headers):
        """Test getting another user's profile (should be forbidden for non-superusers)."""
        # Create another user
        user_data = {
            "email": "other@example.com",
            "username": "otheruser",
            "full_name": "Other User",
            "password": "OtherPassword123"
        }
        create_response = client.post("/api/v1/users/", json=user_data)
        other_user_id = create_response.json()["id"]
        
        # Try to access other user's profile
        response = client.get(f"/api/v1/users/{other_user_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json()["detail"]
    
    def test_update_my_profile_success(self, client, auth_headers):
        """Test updating current user profile."""
        update_data = {
            "full_name": "Updated Name"
        }
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == "Updated Name"
    
    def test_update_my_profile_duplicate_email(self, client, auth_headers):
        """Test updating profile with duplicate email."""
        # Create another user first
        user_data = {
            "email": "other@example.com",
            "username": "otheruser",
            "full_name": "Other User",
            "password": "OtherPassword123"
        }
        client.post("/api/v1/users/", json=user_data)
        
        # Try to update current user's email to the same as the other user
        update_data = {"email": "other@example.com"}
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]
    
    def test_update_user_superuser_success(self, client, superuser_headers, test_user):
        """Test updating user by superuser."""
        update_data = {
            "full_name": "Updated by Admin"
        }
        response = client.put(f"/api/v1/users/{test_user.id}", json=update_data, headers=superuser_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == "Updated by Admin"
    
    def test_update_user_non_superuser_forbidden(self, client, auth_headers, test_user):
        """Test updating user by non-superuser (should be forbidden)."""
        update_data = {
            "full_name": "Updated by Regular User"
        }
        response = client.put(f"/api/v1/users/{test_user.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json()["detail"]
    
    def test_delete_user_superuser_success(self, client, superuser_headers, test_user):
        """Test deleting user by superuser."""
        response = client.delete(f"/api/v1/users/{test_user.id}", headers=superuser_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "User deleted successfully"
    
    def test_delete_user_non_superuser_forbidden(self, client, auth_headers, test_user):
        """Test deleting user by non-superuser (should be forbidden)."""
        response = client.delete(f"/api/v1/users/{test_user.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json()["detail"]
    
    def test_delete_user_self_forbidden(self, client, superuser_headers, test_superuser):
        """Test deleting own account (should be forbidden)."""
        response = client.delete(f"/api/v1/users/{test_superuser.id}", headers=superuser_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot delete your own account" in response.json()["detail"]
    
    def test_activate_user_superuser_success(self, client, superuser_headers, test_user):
        """Test activating user by superuser."""
        response = client.post(f"/api/v1/users/{test_user.id}/activate", headers=superuser_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_active"] is True
    
    def test_deactivate_user_superuser_success(self, client, superuser_headers, test_user):
        """Test deactivating user by superuser."""
        response = client.post(f"/api/v1/users/{test_user.id}/deactivate", headers=superuser_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_active"] is False
    
    def test_deactivate_user_self_forbidden(self, client, superuser_headers, test_superuser):
        """Test deactivating own account (should be forbidden)."""
        response = client.post(f"/api/v1/users/{test_superuser.id}/deactivate", headers=superuser_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot deactivate your own account" in response.json()["detail"]
    
    def test_verify_user_superuser_success(self, client, superuser_headers, test_user):
        """Test verifying user by superuser."""
        response = client.post(f"/api/v1/users/{test_user.id}/verify", headers=superuser_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_verified"] is True
