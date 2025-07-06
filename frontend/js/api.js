// API 基礎配置
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// API 工具類
class API {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        // 如果有 access token，添加到 headers
        if (AuthManager.getAccessToken()) {
            defaultOptions.headers['Authorization'] = `Bearer ${AuthManager.getAccessToken()}`;
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

            // 如果 token 過期，嘗試刷新
            if (response.status === 401 && AuthManager.getAccessToken()) {
                try {
                    await this.refreshToken();
                    // 重新發送請求
                    config.headers['Authorization'] = `Bearer ${AuthManager.getAccessToken()}`;
                    const retryResponse = await fetch(url, config);
                    const retryData = await retryResponse.json();
                    
                    if (!retryResponse.ok) {
                        throw new Error(retryData.message || '請求失敗');
                    }
                    return retryData;
                } catch (refreshError) {
                    // 刷新失敗，清除 token 並跳轉到登入
                    AuthManager.logout();
                    throw new Error('登入已過期，請重新登入');
                }
            }

            if (!response.ok) {
                throw new Error(data.message || '請求失敗');
            }

            return data;
        } catch (error) {
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
        const response = await fetch(`${API_BASE_URL}/auth/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(credentials),
            credentials: 'include',
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || '登入失敗');
        }

        // 設置 access token
        AuthManager.setAccessToken(data.access_token);
        return data;
    }

    static async refreshToken() {
        const response = await fetch(`${API_BASE_URL}/auth/refresh-token/`, {
            method: 'GET',
            credentials: 'include', // 包含 cookies
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Token 刷新失敗');
        }

        // 更新 access token
        AuthManager.setAccessToken(data.access_token);
        return data;
    }

    // 貼文 API
    static async getPosts(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/posts/?${query}`);
    }

    static async createPost(postData) {
        // 如果是 FormData（包含檔案），直接發送
        if (postData instanceof FormData) {
            const url = `${API_BASE_URL}/posts/`;
            
            const config = {
                method: 'POST',
                body: postData,
                credentials: 'include',
            };

            // 如果有 access token，添加到 headers
            if (AuthManager.getAccessToken()) {
                config.headers = {
                    'Authorization': `Bearer ${AuthManager.getAccessToken()}`,
                };
            }

            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || '請求失敗');
            }

            return data;
        } else {
            // 如果是普通物件，使用 JSON
            return this.request('/posts/', {
                method: 'POST',
                body: JSON.stringify(postData),
                credentials: 'include',
            });
        }
    }

    static async getPost(id) {
        return this.request(`/posts/${id}/`);
    }

    static async updatePost(id, postData) {
        return this.request(`/posts/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(postData),
            credentials: 'include',
        });
    }

    static async deletePost(id) {
        return this.request(`/posts/${id}/`, {
            method: 'DELETE',
            credentials: 'include',
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
            credentials: 'include',
        });
    }

    static async getQuestion(id) {
        return this.request(`/questions/${id}/`);
    }

    static async updateQuestion(id, questionData) {
        return this.request(`/questions/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(questionData),
            credentials: 'include',
        });
    }

    static async deleteQuestion(id) {
        return this.request(`/questions/${id}/`, {
            method: 'DELETE',
            credentials: 'include',
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
            credentials: 'include',
        });
    }
}

// 認證管理
class AuthManager {
    static accessToken = null;
    
    static setAccessToken(token) {
        this.accessToken = token;
    }
    
    static getAccessToken() {
        return this.accessToken;
    }
    
    static clearAccessToken() {
        this.accessToken = null;
    }
    
    static isAuthenticated() {
        return !!this.accessToken;
    }

    // 檢查並恢復登入狀態
    static async checkAuthStatus() {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/refresh-token/`, {
                method: 'GET',
                credentials: 'include', // 包含 cookies
            });
            if (response.ok) {
                const data = await response.json();
                this.setAccessToken(data.access_token);
                return true;
            } else {
                const errorData = await response.json().catch(() => ({}));
                this.clearAccessToken();
                return false;
            }
        } catch (error) {
            this.clearAccessToken();
            return false;
        }
    }

    static async logout() {
        this.clearAccessToken();
        // 清除 refresh token cookie
        await fetch(`${API_BASE_URL}/auth/logout/`,{
            method: 'POST',
            credentials: 'include',
        })
        
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