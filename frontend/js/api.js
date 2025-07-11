const API_BASE_URL = 'http://localhost:8000/api';

class API {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', 
        };

        const token = AuthManager.getAccessToken();
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

        // 如果是 FormData，不設置 Content-Type
        if (options.body instanceof FormData) {
            delete config.headers['Content-Type'];
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (response.status === 401 && AuthManager.getAccessToken() && !this._refreshingToken) {
                this._refreshingToken = true;
                try {
                    await this.refreshToken();
                    config.headers['Authorization'] = `Bearer ${AuthManager.getAccessToken()}`;
                    const retryResponse = await fetch(url, config);
                    const retryData = await retryResponse.json();
                    
                    if (!retryResponse.ok) {
                        throw new Error(retryData.message || '請求失敗');
                    }
                    return retryData;
                } catch (refreshError) {
                    AuthManager.clearAccessToken();
                    throw new Error('登入已過期，請重新登入');
                } finally {
                    this._refreshingToken = false;
                }
            }

            if (!response.ok) {
                console.error('API 請求失敗:', { status: response.status, data });
                if (response.status === 401) {
                    AuthManager.clearAccessToken();
                }
                
                if (response.status === 400 && data.errors) {
                    const errorMessages = [];
                    for (const field in data.errors) {
                        if (Array.isArray(data.errors[field])) {
                            errorMessages.push(...data.errors[field]);
                        } else {
                            errorMessages.push(data.errors[field]);
                        }
                    }
                    throw new Error(errorMessages.join(', '));
                }
                
                throw new Error(data.message || data.error || '請求失敗');
            }

            return data;
        } catch (error) {
            throw error;
        }
    }

    static async register(userData) {
        return this.request('/accounts/register/', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    }

    static async login(credentials) {
        const response = await this.request('/accounts/login/', {
            method: 'POST',
            body: JSON.stringify(credentials),
        });

        // 設置 token 和 username
        if (response.access_token) {
            AuthManager.setAccessToken(response.access_token, response.username);
        }
        
        return response;
    }

    static async refreshToken() {
        const response = await this.request('/accounts/refresh_token/', {
            method: 'GET',
        });

        if (response.access_token) {
            AuthManager.setAccessToken(response.access_token, response.username);
        }
        
        return response;
    }

    // 貼文 API
    static async getPosts(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/posts/?${query}`);
    }

    static async createPost(postData) {
        if (postData instanceof FormData) {
            return this.request('/posts/', {
                method: 'POST',
                body: postData,
            });
        } else {
            return this.request('/posts/', {
                method: 'POST',
                body: JSON.stringify(postData),
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
        });
    }

    static async deletePost(id) {
        return this.request(`/posts/${id}/`, {
            method: 'DELETE',
        });
    }

    // 問答 API
    static async getQuestions(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/questions/?${query}`);
    }

    static async createQuestion(questionData) {
        return this.request('/questions/', {
            method: 'POST',
            body: JSON.stringify(questionData),
        });
    }

    static async getQuestionDetail(questionId) {
        return this.request(`/questions/${questionId}/answers/`);
    }

    static async deleteQuestion(questionId) {
        return this.request(`/questions/${questionId}/`, {
            method: 'DELETE',
        });
    }

    static async deleteAnswer(answerId) {
        return this.request('/questions/delete_answer/', {
            method: 'POST',
            body: JSON.stringify({ answer_id: answerId }),
        });
    }

    static async createAnswer(questionId, data) {
        return this.request(`/questions/${questionId}/answers/`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    static async likeQuestion(questionId) {
        return this.request(`/questions/${questionId}/like/`, {
            method: 'POST',
        });
    }

    static async likeAnswer(answerId) {
        return this.request('/questions/like_answer/', {
            method: 'POST',
            body: JSON.stringify({ answer_id: answerId }),
        });
    }

    static async viewQuestion(questionId) {
        return this.request(`/questions/${questionId}/view/`, {
            method: 'POST',
        });
    }
}


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