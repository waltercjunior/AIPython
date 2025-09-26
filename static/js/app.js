/**
 * AIPython User Management System - Frontend JavaScript
 * Modern ES6+ JavaScript with async/await and fetch API
 */

class UserManagementApp {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api/v1';
        this.currentPage = 1;
        this.usersPerPage = 25;
        this.users = [];
        this.filteredUsers = [];
        this.searchTerm = '';
        this.statusFilter = '';
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadDashboardData();
        await this.loadUsers();
        this.updateStats();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchSection(link.dataset.section);
            });
        });

        // Search functionality
        const searchInput = document.getElementById('user-search');
        searchInput.addEventListener('input', (e) => {
            this.searchTerm = e.target.value.toLowerCase();
            this.filterUsers();
        });

        // Status filter
        const statusFilter = document.getElementById('status-filter');
        statusFilter.addEventListener('change', (e) => {
            this.statusFilter = e.target.value;
            this.filterUsers();
        });

        // Users per page
        const usersPerPageSelect = document.getElementById('users-per-page');
        usersPerPageSelect.addEventListener('change', (e) => {
            this.usersPerPage = parseInt(e.target.value);
            this.currentPage = 1;
            this.renderUsers();
        });

        // Form submissions
        document.getElementById('create-user-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createUser();
        });

        document.getElementById('edit-user-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.updateUser();
        });

        // Modal close events
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    switchSection(sectionName) {
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

        // Update content sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(sectionName).classList.add('active');

        // Load section-specific data
        if (sectionName === 'users') {
            this.loadUsers();
        } else if (sectionName === 'dashboard') {
            this.loadDashboardData();
        }
    }

    async loadDashboardData() {
        try {
            this.showLoading();
            const response = await fetch(`${this.apiBaseUrl}/users/`);
            const data = await response.json();
            
            if (response.ok) {
                this.updateDashboardStats(data.users);
            } else {
                this.showToast('Error loading dashboard data', 'error');
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showToast('Error loading dashboard data', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async loadUsers() {
        try {
            this.showTableLoading();
            const response = await fetch(`${this.apiBaseUrl}/users/?skip=0&limit=1000`);
            const data = await response.json();
            
            if (response.ok) {
                this.users = data.users;
                this.filteredUsers = [...this.users];
                this.renderUsers();
                this.updateStats();
            } else {
                this.showToast('Error loading users', 'error');
            }
        } catch (error) {
            console.error('Error loading users:', error);
            this.showToast('Error loading users', 'error');
        } finally {
            this.hideTableLoading();
        }
    }

    filterUsers() {
        this.filteredUsers = this.users.filter(user => {
            const matchesSearch = !this.searchTerm || 
                user.name.toLowerCase().includes(this.searchTerm) ||
                user.email.toLowerCase().includes(this.searchTerm);
            
            const matchesStatus = !this.statusFilter || 
                (this.statusFilter === 'active' && user.is_active) ||
                (this.statusFilter === 'inactive' && !user.is_active);
            
            return matchesSearch && matchesStatus;
        });
        
        this.currentPage = 1;
        this.renderUsers();
    }

    renderUsers() {
        const tbody = document.getElementById('users-tbody');
        const startIndex = (this.currentPage - 1) * this.usersPerPage;
        const endIndex = startIndex + this.usersPerPage;
        const pageUsers = this.filteredUsers.slice(startIndex, endIndex);

        tbody.innerHTML = '';

        if (pageUsers.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 2rem; color: var(--gray-500);">
                        <i class="fas fa-users" style="font-size: 2rem; margin-bottom: 1rem; display: block;"></i>
                        No users found
                    </td>
                </tr>
            `;
        } else {
            pageUsers.forEach(user => {
                const row = this.createUserRow(user);
                tbody.appendChild(row);
            });
        }

        this.renderPagination();
    }

    createUserRow(user) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.id}</td>
            <td>${user.name}</td>
            <td>${user.email}</td>
            <td>
                <span class="status-badge ${user.is_active ? 'active' : 'inactive'}">
                    <i class="fas fa-circle"></i>
                    ${user.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>${this.formatDate(user.created_at)}</td>
            <td>
                <div class="action-buttons-small">
                    <button class="btn btn-small btn-primary" onclick="app.editUser(${user.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-small ${user.is_active ? 'btn-warning' : 'btn-success'}" 
                            onclick="app.toggleUserStatus(${user.id}, ${user.is_active})">
                        <i class="fas fa-${user.is_active ? 'pause' : 'play'}"></i>
                    </button>
                    <button class="btn btn-small btn-error" onclick="app.deleteUser(${user.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        return row;
    }

    renderPagination() {
        const pagination = document.getElementById('pagination');
        const totalPages = Math.ceil(this.filteredUsers.length / this.usersPerPage);
        
        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }

        let paginationHTML = '';
        
        // Previous button
        paginationHTML += `
            <button ${this.currentPage === 1 ? 'disabled' : ''} 
                    onclick="app.goToPage(${this.currentPage - 1})">
                <i class="fas fa-chevron-left"></i>
            </button>
        `;

        // Page numbers
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(totalPages, this.currentPage + 2);

        if (startPage > 1) {
            paginationHTML += `<button onclick="app.goToPage(1)">1</button>`;
            if (startPage > 2) {
                paginationHTML += `<span>...</span>`;
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <button class="${i === this.currentPage ? 'active' : ''}" 
                        onclick="app.goToPage(${i})">${i}</button>
            `;
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHTML += `<span>...</span>`;
            }
            paginationHTML += `<button onclick="app.goToPage(${totalPages})">${totalPages}</button>`;
        }

        // Next button
        paginationHTML += `
            <button ${this.currentPage === totalPages ? 'disabled' : ''} 
                    onclick="app.goToPage(${this.currentPage + 1})">
                <i class="fas fa-chevron-right"></i>
            </button>
        `;

        pagination.innerHTML = paginationHTML;
    }

    goToPage(page) {
        this.currentPage = page;
        this.renderUsers();
    }

    async createUser() {
        const form = document.getElementById('create-user-form');
        const formData = new FormData(form);
        const userData = {
            name: formData.get('name'),
            email: formData.get('email')
        };

        // Validate form
        if (!this.validateUserForm(userData)) {
            return;
        }

        try {
            this.showLoading();
            const response = await fetch(`${this.apiBaseUrl}/users/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();

            if (response.ok) {
                this.showToast('User created successfully!', 'success');
                this.hideCreateUserModal();
                form.reset();
                await this.loadUsers();
                await this.loadDashboardData();
            } else {
                this.showToast(data.detail || 'Error creating user', 'error');
            }
        } catch (error) {
            console.error('Error creating user:', error);
            this.showToast('Error creating user', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async editUser(userId) {
        try {
            this.showLoading();
            const response = await fetch(`${this.apiBaseUrl}/users/${userId}`);
            const user = await response.json();

            if (response.ok) {
                document.getElementById('edit-user-id').value = user.id;
                document.getElementById('edit-user-name').value = user.name;
                document.getElementById('edit-user-email').value = user.email;
                this.showEditUserModal();
            } else {
                this.showToast('Error loading user data', 'error');
            }
        } catch (error) {
            console.error('Error loading user:', error);
            this.showToast('Error loading user data', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async updateUser() {
        const form = document.getElementById('edit-user-form');
        const formData = new FormData(form);
        const userId = formData.get('edit-user-id');
        const userData = {
            name: formData.get('name'),
            email: formData.get('email')
        };

        // Validate form
        if (!this.validateUserForm(userData)) {
            return;
        }

        try {
            this.showLoading();
            const response = await fetch(`${this.apiBaseUrl}/users/${userId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();

            if (response.ok) {
                this.showToast('User updated successfully!', 'success');
                this.hideEditUserModal();
                await this.loadUsers();
                await this.loadDashboardData();
            } else {
                this.showToast(data.detail || 'Error updating user', 'error');
            }
        } catch (error) {
            console.error('Error updating user:', error);
            this.showToast('Error updating user', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async deleteUser(userId) {
        if (!confirm('Are you sure you want to delete this user?')) {
            return;
        }

        try {
            this.showLoading();
            const response = await fetch(`${this.apiBaseUrl}/users/${userId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showToast('User deleted successfully!', 'success');
                await this.loadUsers();
                await this.loadDashboardData();
            } else {
                const data = await response.json();
                this.showToast(data.detail || 'Error deleting user', 'error');
            }
        } catch (error) {
            console.error('Error deleting user:', error);
            this.showToast('Error deleting user', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async toggleUserStatus(userId, currentStatus) {
        const action = currentStatus ? 'deactivate' : 'activate';
        const actionText = currentStatus ? 'deactivate' : 'activate';

        if (!confirm(`Are you sure you want to ${actionText} this user?`)) {
            return;
        }

        try {
            this.showLoading();
            const response = await fetch(`${this.apiBaseUrl}/users/${userId}/${action}`, {
                method: 'PATCH'
            });

            if (response.ok) {
                this.showToast(`User ${actionText}d successfully!`, 'success');
                await this.loadUsers();
                await this.loadDashboardData();
            } else {
                const data = await response.json();
                this.showToast(data.detail || `Error ${actionText}ing user`, 'error');
            }
        } catch (error) {
            console.error(`Error ${actionText}ing user:`, error);
            this.showToast(`Error ${actionText}ing user`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    validateUserForm(userData) {
        let isValid = true;

        // Clear previous errors
        document.querySelectorAll('.error-message').forEach(error => {
            error.classList.remove('show');
        });

        // Validate name
        if (!userData.name || userData.name.trim().length < 2) {
            document.getElementById('name-error').textContent = 'Name must be at least 2 characters long';
            document.getElementById('name-error').classList.add('show');
            isValid = false;
        }

        // Validate email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!userData.email || !emailRegex.test(userData.email)) {
            document.getElementById('email-error').textContent = 'Please enter a valid email address';
            document.getElementById('email-error').classList.add('show');
            isValid = false;
        }

        return isValid;
    }

    updateDashboardStats(users) {
        const totalUsers = users.length;
        const activeUsers = users.filter(user => user.is_active).length;
        const inactiveUsers = totalUsers - activeUsers;

        document.getElementById('total-users').textContent = totalUsers;
        document.getElementById('active-users').textContent = activeUsers;
        document.getElementById('inactive-users').textContent = inactiveUsers;
        document.getElementById('api-calls').textContent = Math.floor(Math.random() * 100) + 50; // Mock data
    }

    updateStats() {
        const totalUsers = this.users.length;
        const activeUsers = this.users.filter(user => user.is_active).length;
        const inactiveUsers = totalUsers - activeUsers;

        document.getElementById('total-users').textContent = totalUsers;
        document.getElementById('active-users').textContent = activeUsers;
        document.getElementById('inactive-users').textContent = inactiveUsers;
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    // Modal functions
    showCreateUserModal() {
        document.getElementById('create-user-modal').classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    hideCreateUserModal() {
        document.getElementById('create-user-modal').classList.remove('active');
        document.body.style.overflow = 'auto';
        document.getElementById('create-user-form').reset();
        document.querySelectorAll('#create-user-form .error-message').forEach(error => {
            error.classList.remove('show');
        });
    }

    showEditUserModal() {
        document.getElementById('edit-user-modal').classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    hideEditUserModal() {
        document.getElementById('edit-user-modal').classList.remove('active');
        document.body.style.overflow = 'auto';
        document.querySelectorAll('#edit-user-form .error-message').forEach(error => {
            error.classList.remove('show');
        });
    }

    closeModal(modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }

    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
        });
        document.body.style.overflow = 'auto';
    }

    // Loading states
    showLoading() {
        document.getElementById('loading-overlay').classList.add('active');
    }

    hideLoading() {
        document.getElementById('loading-overlay').classList.remove('active');
    }

    showTableLoading() {
        document.getElementById('users-loading').style.display = 'flex';
        document.getElementById('users-table').style.display = 'none';
    }

    hideTableLoading() {
        document.getElementById('users-loading').style.display = 'none';
        document.getElementById('users-table').style.display = 'table';
    }

    // Toast notifications
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-${this.getToastIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;

        document.getElementById('toast-container').appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Utility functions
    async refreshUsers() {
        await this.loadUsers();
        this.showToast('Users refreshed successfully!', 'success');
    }

    exportUsers() {
        const csvContent = this.generateCSV(this.filteredUsers);
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `users_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
        this.showToast('Users exported successfully!', 'success');
    }

    generateCSV(users) {
        const headers = ['ID', 'Name', 'Email', 'Status', 'Created At'];
        const rows = users.map(user => [
            user.id,
            user.name,
            user.email,
            user.is_active ? 'Active' : 'Inactive',
            user.created_at
        ]);

        return [headers, ...rows].map(row => 
            row.map(field => `"${field}"`).join(',')
        ).join('\n');
    }
}

// Global functions for HTML onclick handlers
function showCreateUserModal() {
    app.showCreateUserModal();
}

function hideCreateUserModal() {
    app.hideCreateUserModal();
}

function hideEditUserModal() {
    app.hideEditUserModal();
}

function refreshUsers() {
    app.refreshUsers();
}

function exportUsers() {
    app.exportUsers();
}

// Initialize the application when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new UserManagementApp();
});
