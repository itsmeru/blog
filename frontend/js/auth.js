class AuthManager {
    static accessToken = null;
    static username = null;
    
    static setAccessToken(token, username) {
        this.accessToken = token;
        this.username = username;
    }
    
    static getAccessToken() {
        return this.accessToken;
    }
    
    static clearAccessToken() {
        this.accessToken = null;
        this.username = null;
    }
    

    static isLoggedIn() {
        return !!this.accessToken;
    }

    static getUsername() {        
        return this.username || '用戶';
    }

    static async checkAuthStatus() {
        if (this._checkingAuth) {
            return this.isLoggedIn();
        }
        
        this._checkingAuth = true;
        
        try {
            const response = await fetch(`${API_BASE_URL}/accounts/refresh_token/`, {
                method: 'GET',
                credentials: 'include',
            });
            if (response.ok) {
                const data = await response.json();
                this.setAccessToken(data.access_token, data.username);
                return true;
            } else {
                this.clearAccessToken();
                return false;
            }
        } catch (error) {
            this.clearAccessToken();
            return false;
        } finally {
            this._checkingAuth = false;
        }
    }

    static async logout() {
        if (this._loggingOut) {
            return;
        }
        this._loggingOut = true;
        
        this.clearAccessToken();
        
        try {
        await fetch(`${API_BASE_URL}/accounts/logout/`,{
            method: 'POST',
            credentials: 'include',
            });
        } catch (error) {
            console.log('登出請求失敗:', error);
        }
        
        if (window.app) {
            window.app.updateAuthUI();
        }
        
        this._loggingOut = false;
    }
}