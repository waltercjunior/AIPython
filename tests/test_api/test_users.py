"""
API tests for user endpoints.
"""
import pytest
from fastapi import status


class TestUserAPI:
    """Test cases for user API endpoints."""
    
    def test_create_user(self, client, sample_user_data):
        """Test creating a new user."""
        response = client.post("/api/v1/users/", json=sample_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["name"] == sample_user_data["name"]
        assert data["email"] == sample_user_data["email"]
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_user_duplicate_email(self, client, sample_user_data):
        """Test creating user with duplicate email."""
        # Create first user
        client.post("/api/v1/users/", json=sample_user_data)
        
        # Try to create second user with same email
        response = client.post("/api/v1/users/", json=sample_user_data)
        assert response.status_code == status.HTTP_409_CONFLICT
    
    def test_get_users(self, client, sample_user_data):
        """Test getting all users."""
        # Create a user first
        client.post("/api/v1/users/", json=sample_user_data)
        
        response = client.get("/api/v1/users/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        assert len(data["users"]) == 1
    
    def test_get_user_by_id(self, client, sample_user_data):
        """Test getting user by ID."""
        # Create a user first
        create_response = client.post("/api/v1/users/", json=sample_user_data)
        user_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == user_id
        assert data["name"] == sample_user_data["name"]
        assert data["email"] == sample_user_data["email"]
    
    def test_get_user_not_found(self, client):
        """Test getting non-existent user."""
        response = client.get("/api/v1/users/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_user(self, client, sample_user_data):
        """Test updating user."""
        # Create a user first
        create_response = client.post("/api/v1/users/", json=sample_user_data)
        user_id = create_response.json()["id"]
        
        # Update user
        update_data = {"name": "Updated Name"}
        response = client.put(f"/api/v1/users/{user_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == sample_user_data["email"]
    
    def test_delete_user(self, client, sample_user_data):
        """Test deleting user."""
        # Create a user first
        create_response = client.post("/api/v1/users/", json=sample_user_data)
        user_id = create_response.json()["id"]
        
        # Delete user
        response = client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify user is deleted
        get_response = client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_activate_user(self, client, sample_user_data):
        """Test activating user."""
        # Create a user first
        create_response = client.post("/api/v1/users/", json=sample_user_data)
        user_id = create_response.json()["id"]
        
        # Activate user
        response = client.patch(f"/api/v1/users/{user_id}/activate")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["is_active"] is True
    
    def test_deactivate_user(self, client, sample_user_data):
        """Test deactivating user."""
        # Create a user first
        create_response = client.post("/api/v1/users/", json=sample_user_data)
        user_id = create_response.json()["id"]
        
        # Deactivate user
        response = client.patch(f"/api/v1/users/{user_id}/deactivate")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["is_active"] is False
