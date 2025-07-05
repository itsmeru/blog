class BlogApp {
    constructor() {
        this.init().catch(error => {
            console.error('應用初始化失敗:', error);
        });
    }

    async init() {
        // 先檢查登入狀態
        await AuthManager.checkAuthStatus();
        
        this.setupEventListeners();
        this.updateAuthUI();
        this.loadInitialData();
    }

    // 設置事件監聽器
    setupEventListeners() {
        // 模態框事件
        this.setupModalEvents();
        
        // 表單事件
        this.setupFormEvents();
        
        // 導航事件
        this.setupNavigationEvents();
    }

    // 模態框管理
    setupModalEvents() {
        // 登入按鈕
        document.getElementById('loginBtn').addEventListener('click', () => {
            this.showModal('loginModal');
        });

        // 註冊按鈕
        document.getElementById('registerBtn').addEventListener('click', () => {
            this.showModal('registerModal');
        });

        // 新貼文按鈕
        document.getElementById('newPostBtn').addEventListener('click', () => {
            if (!AuthManager.isAuthenticated()) {
                console.log('請先登入');
                return;
            }
            this.showModal('newPostModal');
        });

        // 新問題按鈕
        document.getElementById('newQuestionBtn').addEventListener('click', () => {
            if (!AuthManager.isAuthenticated()) {
                console.log('請先登入');
                return;
            }
            this.showModal('newQuestionModal');
        });

        // 登出按鈕
        document.getElementById('logoutBtn').addEventListener('click', () => {
            AuthManager.logout();
        });

        // 關閉模態框
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => {
                this.hideModal(e.target.closest('.modal').id);
            });
        });

        // 點擊模態框外部關閉
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modal.id);
                }
            });
        });
    }

    // 表單事件處理
    setupFormEvents() {
        // 登入表單
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleLogin();
        });

        // 註冊表單
        document.getElementById('registerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleRegister();
        });

        // 新貼文表單
        document.getElementById('newPostForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleCreatePost();
        });

        // 新問題表單
        document.getElementById('newQuestionForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleCreateQuestion();
        });
    }

    // 導航事件
    setupNavigationEvents() {
        // 平滑滾動到錨點
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // 顯示模態框
    showModal(modalId) {
        document.getElementById(modalId).style.display = 'block';
        document.body.style.overflow = 'hidden';
    }

    // 隱藏模態框
    hideModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
        document.body.style.overflow = 'auto';
        
        // 清空表單
        const form = document.querySelector(`#${modalId} form`);
        if (form) {
            form.reset();
        }
    }

    // 更新認證 UI
    updateAuthUI() {
        const loginBtn = document.getElementById('loginBtn');
        const registerBtn = document.getElementById('registerBtn');
        const userMenu = document.getElementById('userMenu');
        const usernameSpan = document.getElementById('username');

        if (AuthManager.isAuthenticated()) {
            loginBtn.style.display = 'none';
            registerBtn.style.display = 'none';
            userMenu.style.display = 'flex';
            
        } else {
            loginBtn.style.display = 'inline-block';
            registerBtn.style.display = 'inline-block';
            userMenu.style.display = 'none';
        }
    }

    // 載入初始數據
    async loadInitialData() {
        try {
            await Promise.all([
                this.loadPosts(),
                this.loadQuestions()
            ]);
        } catch (error) {
            console.error('載入初始數據失敗:', error);
        }
    }

    // 載入貼文
    async loadPosts() {
        const container = document.getElementById('postsContainer');
        LoadingManager.show(container);

        try {
            const posts = await API.getPosts();
            this.renderPosts(posts);
        } catch (error) {
            container.innerHTML = '<p>載入貼文失敗</p>';
            console.log('載入貼文失敗');
        } finally {
            LoadingManager.hide(container);
        }
    }

    // 渲染貼文
    renderPosts(posts) {
        const container = document.getElementById('postsContainer');
        
        if (!posts || posts.length === 0) {
            container.innerHTML = '<p>目前沒有貼文</p>';
            return;
        }

        const postsHTML = posts.map(post => `
            <div class="post-card">
                <h3>${post.title}</h3>
                <div class="post-meta">
                    <span>作者: ${post.author || '匿名'}</span>
                    <span>發布時間: ${new Date(post.created_at).toLocaleDateString()}</span>
                </div>
                <p>${post.content.substring(0, 150)}${post.content.length > 150 ? '...' : ''}</p>
                <button class="btn btn-primary" onclick="app.viewPost(${post.id})">閱讀更多</button>
            </div>
        `).join('');

        container.innerHTML = postsHTML;
    }

    // 載入問題
    async loadQuestions() {
        const container = document.getElementById('qaContainer');
        LoadingManager.show(container);

        try {
            const questions = await API.getQuestions();
            this.renderQuestions(questions);
        } catch (error) {
            container.innerHTML = '<p>載入問題失敗</p>';
            console.log('載入問題失敗');
        } finally {
            LoadingManager.hide(container);
        }
    }

    // 渲染問題
    renderQuestions(questions) {
        const container = document.getElementById('qaContainer');
        
        if (!questions || questions.length === 0) {
            container.innerHTML = '<p>目前沒有問題</p>';
            return;
        }

        const questionsHTML = questions.map(question => `
            <div class="qa-card">
                <h3>${question.title}</h3>
                <div class="post-meta">
                    <span>提問者: ${question.author || '匿名'}</span>
                    <span>提問時間: ${new Date(question.created_at).toLocaleDateString()}</span>
                </div>
                <p>${question.content.substring(0, 150)}${question.content.length > 150 ? '...' : ''}</p>
                <button class="btn btn-primary" onclick="app.viewQuestion(${question.id})">查看回答</button>
            </div>
        `).join('');

        container.innerHTML = questionsHTML;
    }

    // 處理登入
    async handleLogin() {
        const form = document.getElementById('loginForm');
        const formData = new FormData(form);
        
        const credentials = {
            email: formData.get('email'),
            password: formData.get('password')
        };

        try {
            const response = await API.login(credentials);
            AuthManager.setAccessToken(response.access_token);
            
            this.updateAuthUI();
            this.hideModal('loginModal');
            alert('登入成功！');
            
        } catch (error) {
            console.log(error.message || '登入失敗');
        }
    }

    // 處理註冊
    async handleRegister() {
        const form = document.getElementById('registerForm');
        const formData = new FormData(form);
        
        const password = formData.get('password');
        const confirmPassword = formData.get('confirmPassword');
        
        if (password !== confirmPassword) {
            console.log('密碼確認不匹配');
            return;
        }

        const userData = {
            username: formData.get('username'),
            email: formData.get('email'),
            password: password
        };

        try {
            const response = await API.register(userData);
            
            this.hideModal('registerModal');
            alert('註冊成功！請登入');
        } catch (error) {
            console.log(error.message || '註冊失敗');
        }
    }

    // 處理創建貼文
    async handleCreatePost() {
        const form = document.getElementById('newPostForm');
        const formData = new FormData(form);
        
        const postData = {
            title: formData.get('title'),
            content: formData.get('content')
        };

        try {
            await API.createPost(postData);
            
            this.hideModal('newPostModal');
            alert('貼文發布成功！');
            
            // 重新載入貼文
            this.loadPosts();
        } catch (error) {
            console.log(error.message || '發布失敗');
        }
    }

    // 處理創建問題
    async handleCreateQuestion() {
        const form = document.getElementById('newQuestionForm');
        const formData = new FormData(form);
        
        const questionData = {
            title: formData.get('title'),
            content: formData.get('content')
        };

        try {
            await API.createQuestion(questionData);
            
            this.hideModal('newQuestionModal');
            alert('問題發布成功！');
            
            // 重新載入問題
            this.loadQuestions();
        } catch (error) {
            console.log(error.message || '發布失敗');
        }
    }

    // 查看貼文詳情
    viewPost(postId) {
        // 這裡可以實現查看貼文詳情的功能
        console.log('查看貼文:', postId);
    }

    // 查看問題詳情
    viewQuestion(questionId) {
        // 這裡可以實現查看問題詳情的功能
        console.log('查看問題:', questionId);
    }
}

// 初始化應用程式
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new BlogApp();
}); 