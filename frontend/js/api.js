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
                
                if (response.status === 400) {
                    let errorMessage = '';
                    
                 if (data.message) {
                        errorMessage = data.message;
                    } else {
                        const errorMessages = [];
                        for (const field in data) {
                            errorMessages.push(...data[field]);
                        }
                        errorMessage = errorMessages.join(', ');
                    }
                    
                    throw new Error(errorMessage);
                }
                throw new Error(data.message|| '請求失敗');
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
        const response = await this.request('/token/', {
            method: 'POST',
            body: JSON.stringify({
                username: credentials.email,
                password: credentials.password
            }),
        });

        if (response.access) {
            AuthManager.setAccessToken(response.access, credentials.email);
        }
        
        return response;
    }

    static async refreshToken() {
        const response = await this.request('/token/refresh/', {
            method: 'GET',
        });

        if (response.access) {
            AuthManager.setAccessToken(response.access, response.username || AuthManager.getUsername());
        }
        
        return response;
    }

    // 貼文 API
    static async getPosts(params = {}) {
        const query = new URLSearchParams(params).toString();
        const response = await this.request(`/posts/?${query}`);
        return {
            results: response.results,
            count: response.count,
            next: response.next,
            previous: response.previous,
        };
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
        const response = await this.request(`/questions/?${query}`);
        return {
            results: response.results,
            count: response.count,
            next: response.next,
            previous: response.previous,
        };
    }

    static async createQuestion(questionData) {
        return this.request('/questions/', {
            method: 'POST',
            body: JSON.stringify(questionData),
        });
    }

    static async getQuestionDetail(questionId) {
        return this.request(`/answers/?question_id=${questionId}`);
    }

    static async deleteQuestion(questionId) {
        return this.request(`/questions/${questionId}/`, {
            method: 'DELETE',
        });
    }

    static async deleteAnswer(answerId) {
        return this.request(`/answers/${answerId}/`, {
            method: 'DELETE',
        });
    }

    static async createAnswer(questionId, data) {
        return this.request('/answers/', {
            method: 'POST',
            body: JSON.stringify({
                ...data,
                question_id: questionId
            }),
        });
    }

    static async likeQuestion(questionId) {
        return this.request(`/questions/${questionId}/like_question/`, {
            method: 'POST',
        });
    }

    static async likeAnswer(answerId) {
        return this.request(`/answers/${answerId}/like_answer/`, {
            method: 'POST',
        });
    }

    static async viewQuestion(questionId) {
        return this.request(`/questions/${questionId}/view_question/`, {
            method: 'POST',
        });
    }

    // 用戶相關 API
    static async changePassword(oldPassword, newPassword) {
        return this.request('/accounts/change_password/', {
            method: 'POST',
            body: JSON.stringify({
                old_password: oldPassword,
                new_password: newPassword
            }),
        });
    }

    static async changeUsername(newUsername) {
        return this.request('/accounts/change_username/', {
            method: 'POST',
            body: JSON.stringify({
                new_username: newUsername
            }),
        });
    }

    static async getProfileStats() {
        return this.request('/accounts/profile_stats/', {
            method: 'GET',
        });
    }

    // 忘記密碼相關 API
    static async forgotPassword(email) {
        return this.request('/accounts/forgot_password/', {
            method: 'POST',
            body: JSON.stringify({
                email: email
            }),
        });
    }

    static async verifyResetToken(email, token) {
        return this.request('/accounts/verify_reset_token/', {
            method: 'POST',
            body: JSON.stringify({
                email: email,
                token: token
            }),
        });
    }

    static async resetPassword(email, token, newPassword) {
        return this.request('/accounts/reset_password/', {
            method: 'POST',
            body: JSON.stringify({
                email: email,
                token: token,
                new_password: newPassword
            }),
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