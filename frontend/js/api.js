// API 基礎配置
const API_BASE_URL = 'http://localhost:8000/api';

// API 工具類
class API {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        // 如果有 token，添加到 headers
        const token = localStorage.getItem('token');
        if (token) {
            defaultOptions.headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || '請求失敗');
            }

            return data;
        } catch (error) {
            console.error('API 請求錯誤:', error);
            throw error;
        }
    }

    // 用戶認證 API
    static async register(userData) {
        return this.request('/auth/register/', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    }

    static async login(credentials) {
        return this.request('/auth/login/', {
            method: 'POST',
            body: JSON.stringify(credentials),
        });
    }

    static async getProfile() {
        return this.request('/auth/profile/');
    }

    // 貼文 API
    static async getPosts() {
        return this.request('/posts/');
    }

    static async createPost(postData) {
        return this.request('/posts/', {
            method: 'POST',
            body: JSON.stringify(postData),
        });
    }

    static async getPost(id) {
        return this.request(`/posts/${id}/`);
    }

    static async updatePost(id, postData) {
        return this.request(`/posts/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(postData),
        });
    }

    static async deletePost(id) {
        return this.request(`/posts/${id}/`, {
            method: 'DELETE',
        });
    }

    // 問答 API
    static async getQuestions() {
        return this.request('/questions/');
    }

    static async createQuestion(questionData) {
        return this.request('/questions/', {
            method: 'POST',
            body: JSON.stringify(questionData),
        });
    }

    static async getQuestion(id) {
        return this.request(`/questions/${id}/`);
    }

    static async updateQuestion(id, questionData) {
        return this.request(`/questions/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(questionData),
        });
    }

    static async deleteQuestion(id) {
        return this.request(`/questions/${id}/`, {
            method: 'DELETE',
        });
    }

    // 回答 API
    static async getAnswers(questionId) {
        return this.request(`/questions/${questionId}/answers/`);
    }

    static async createAnswer(questionId, answerData) {
        return this.request(`/questions/${questionId}/answers/`, {
            method: 'POST',
            body: JSON.stringify(answerData),
        });
    }
}

// 認證管理
class AuthManager {
    static isAuthenticated() {
        return !!localStorage.getItem('token');
    }

    static getToken() {
        return localStorage.getItem('token');
    }

    static setToken(token) {
        localStorage.setItem('token', token);
    }

    static removeToken() {
        localStorage.removeItem('token');
    }

    static getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }

    static setUser(user) {
        localStorage.setItem('user', JSON.stringify(user));
    }

    static removeUser() {
        localStorage.removeItem('user');
    }

    static logout() {
        this.removeToken();
        this.removeUser();
        window.location.reload();
    }
}

// 錯誤處理
class ErrorHandler {
    static showError(message) {
        // 創建錯誤訊息元素
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message error';
        errorDiv.textContent = message;
        errorDiv.style.position = 'fixed';
        errorDiv.style.top = '100px';
        errorDiv.style.left = '50%';
        errorDiv.style.transform = 'translateX(-50%)';
        errorDiv.style.zIndex = '9999';
        errorDiv.style.minWidth = '300px';
        errorDiv.style.textAlign = 'center';
        
        // 插入到頁面頂部
        document.body.appendChild(errorDiv);
        
        // 3秒後自動移除
        setTimeout(() => {
            errorDiv.remove();
        }, 3000);
    }

    static showSuccess(message) {
        // 創建成功訊息元素
        const successDiv = document.createElement('div');
        successDiv.className = 'message success';
        successDiv.textContent = message;
        successDiv.style.position = 'fixed';
        successDiv.style.top = '100px';
        successDiv.style.left = '50%';
        successDiv.style.transform = 'translateX(-50%)';
        successDiv.style.zIndex = '9999';
        successDiv.style.minWidth = '300px';
        successDiv.style.textAlign = 'center';
        
        // 插入到頁面頂部
        document.body.appendChild(successDiv);
        
        // 3秒後自動移除
        setTimeout(() => {
            successDiv.remove();
        }, 3000);
    }
}

// 載入動畫
class LoadingManager {
    static show(container) {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading';
        loadingDiv.textContent = '載入中...';
        container.appendChild(loadingDiv);
    }

    static hide(container) {
        const loadingDiv = container.querySelector('.loading');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }
} 