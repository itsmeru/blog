class BlogApp {
    constructor() {
        this.currentPosts = [];
        this.currentQuestions = [];
        this._initialized = false;
        this._navigationEventsSetup = false;
        this._updatingAuthUI = false;
        this._loadingInitialData = false;
        this._loadingTags = false;
        this._filterTagsEventBound = false;
        this._currentTab = null;
    }

    async init() {
        if (this._initialized) {
            return;
        }
        this._initialized = true;
        
        // 先檢查並恢復登入狀態
        await AuthManager.checkAuthStatus();
        
        this.setupEventListeners();
        this.setupModalEvents();
        this.setupFormEvents();
        this.setupSearchEvents();
        this.setupImageUpload();
        this.setupTagSelection();
        this.setupNavigationEvents();
        
        // 在認證檢查完成後更新 UI
        this.updateAuthUI();
        
        await this.loadInitialData();
        
        // 添加頁面可見性變化監聽，當頁面重新獲得焦點時檢查認證狀態
        document.addEventListener('visibilitychange', async () => {
            if (!document.hidden && AuthManager.getAccessToken()) {
                // 頁面重新可見且有 token 時，檢查認證狀態
                await AuthManager.checkAuthStatus();
                this.updateAuthUI();
            }
        });
    }

    setupEventListeners() {
        // 登入註冊按鈕
        document.getElementById('loginBtn').addEventListener('click', () => this.showModal('loginModal'));
        document.getElementById('registerBtn').addEventListener('click', () => this.showModal('registerModal'));
        document.getElementById('logoutBtn').addEventListener('click', () => this.handleLogout());

        // 新貼文和問題按鈕
        document.getElementById('newPostBtn').addEventListener('click', () => this.showModal('newPostModal'));
        document.getElementById('newQuestionBtn').addEventListener('click', () => this.showModal('questionModal'));
        
        const homePage = document.getElementById('home-page');        
        if (homePage) {
            homePage.addEventListener('click', () => this.goToHomePage());
        }

        // 忘記密碼相關
        const forgotPasswordLink = document.getElementById('forgotPasswordLink');
        if (forgotPasswordLink) {
            forgotPasswordLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.hideModal('loginModal');
                this.showModal('forgotPasswordModal');
            });
        }
    }

    setupModalEvents() {
        // 關閉模態框
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                this.hideModal(modal.id);
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

    setupFormEvents() {
        // 登入表單
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        // 註冊表單
        document.getElementById('registerForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleRegister();
        });

        // 新貼文表單
        document.getElementById('newPostForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleCreatePost();
        });

        // 新問題表單
        document.getElementById('newQuestionForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleCreateQuestion();
        });

        // 更改密碼表單
        const changePasswordForm = document.getElementById('changePasswordForm');
        if (changePasswordForm) {
            changePasswordForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleChangePassword(e);
            });
        }

        // 更改用戶名表單
        const changeUsernameForm = document.getElementById('changeUsernameForm');
        if (changeUsernameForm) {
            changeUsernameForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleChangeUsername(e);
            });
        }

        // 忘記密碼表單
        const forgotPasswordForm = document.getElementById('forgotPasswordForm');
        if (forgotPasswordForm) {
            forgotPasswordForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleForgotPassword(e);
            });
        }

        // 驗證碼表單
        const verifyTokenForm = document.getElementById('verifyTokenForm');
        if (verifyTokenForm) {
            verifyTokenForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleVerifyToken(e);
            });
        }

        // 重設密碼表單
        const resetPasswordForm = document.getElementById('resetPasswordForm');
        if (resetPasswordForm) {
            resetPasswordForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleResetPassword(e);
            });
        }
    }

    setupNavigationEvents() {
        if (this._navigationEventsSetup) {
            return;
        }
        this._navigationEventsSetup = true;

        const showTab = (tab) => {
            // 防止重複切換
            if (this._currentTab === tab) {
                return;
            }
            this._currentTab = tab;
            
            // 隱藏所有頁面
            document.getElementById('posts-section').style.display = 'none';
            document.getElementById('qa-section').style.display = 'none';
            document.getElementById('qa-detail-section').style.display = 'none';
            document.getElementById('post-detail-section').style.display = 'none';
            document.getElementById('about-section').style.display = 'none';
            
            // 移除所有導航項的 active 狀態
            document.getElementById('nav-posts').classList.remove('active');
            document.getElementById('nav-qa').classList.remove('active');
            document.getElementById('nav-about').classList.remove('active');
            
            if (tab === 'posts') {
                document.getElementById('posts-section').style.display = '';
                document.getElementById('nav-posts').classList.add('active');
            } else if (tab === 'qa') {
                document.getElementById('qa-section').style.display = '';
                document.getElementById('nav-qa').classList.add('active');
            } else if (tab === 'about') {
                document.getElementById('about-section').style.display = '';
                document.getElementById('nav-about').classList.add('active');
                // 載入用戶統計信息
                this.loadProfileStats();
            }
            
            localStorage.setItem('blogTab', tab);
        };
    
        document.getElementById('nav-posts').onclick = (e) => {
            e.preventDefault();
            showTab('posts');
        };
        document.getElementById('nav-qa').onclick = (e) => {
            e.preventDefault();
            showTab('qa');
        };
        document.getElementById('nav-about').onclick = (e) => {
            e.preventDefault();
            if (!AuthManager.isLoggedIn()) {
                ErrorHandler.showError('請先登入才能查看個人資料');
                return;
            }
            showTab('about');
        };
    
        this.initializeDefaultTab(showTab); 
        this.setupQATabs();
        
        // 在認證檢查完成後，如果當前在關於頁面且已登入，載入統計資料
        if (this._currentTab === 'about' && AuthManager.isLoggedIn()) {
            setTimeout(() => {
                this.loadProfileStats();
            }, 100);
        }
    }

    // 設置Q&A標籤事件
    setupQATabs() {
        const latestTab = document.getElementById('qa-latest-tab');
        const hotTab = document.getElementById('qa-hot-tab');
        
        if (latestTab) {
            latestTab.addEventListener('click', () => {
                // 更新標籤狀態
                latestTab.classList.add('active');
                hotTab.classList.remove('active');
                // 載入最新問題（重置到第一頁）
                this.loadQuestions(1, 'desc');
            });
        }
        
        if (hotTab) {
            hotTab.addEventListener('click', () => {
                // 更新標籤狀態
                hotTab.classList.add('active');
                latestTab.classList.remove('active');
                // 載入熱門問題（重置到第一頁）
                this.loadQuestions(1, 'hot');
            });
        }
    }

    initializeDefaultTab(showTab) {
        const savedState = localStorage.getItem('blogPageState');
        if (savedState) {
            return;
        }
        
        const savedTab = localStorage.getItem('blogTab');
        const defaultTab = savedTab === 'qa' ? 'qa' : (savedTab === 'about' ? 'about' : 'posts');
        
        this._currentTab = defaultTab;
        if (defaultTab === 'qa') {
            document.getElementById('posts-section').style.display = 'none';
            document.getElementById('qa-section').style.display = '';
            document.getElementById('about-section').style.display = 'none';
            document.getElementById('nav-qa').classList.add('active');
            document.getElementById('nav-posts').classList.remove('active');
            document.getElementById('nav-about').classList.remove('active');
        } else if (defaultTab === 'about') {
            document.getElementById('posts-section').style.display = 'none';
            document.getElementById('qa-section').style.display = 'none';
            document.getElementById('about-section').style.display = '';
            document.getElementById('nav-about').classList.add('active');
            document.getElementById('nav-posts').classList.remove('active');
            document.getElementById('nav-qa').classList.remove('active');
            
            // 如果是關於頁面，載入統計資料
            if (AuthManager.isLoggedIn()) {
                this.loadProfileStats();
            }
        } else {
            document.getElementById('posts-section').style.display = '';
            document.getElementById('qa-section').style.display = 'none';
            document.getElementById('about-section').style.display = 'none';
            document.getElementById('nav-posts').classList.add('active');
            document.getElementById('nav-qa').classList.remove('active');
            document.getElementById('nav-about').classList.remove('active');
        }
    }

    setupSearchEvents() {
        const searchBtn = document.getElementById('searchBtn');
        const searchInput = document.getElementById('searchInput');
        const clearFilterBtn = document.getElementById('clearFilterBtn');

        searchBtn.addEventListener('click', () => {
            const keyword = searchInput.value.trim();
            const activeTags = Array.from(document.querySelectorAll('.filter-tag.active'))
                .map(tag => tag.dataset.tag);
            this.loadPosts(1, keyword, activeTags);
        });

        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const keyword = searchInput.value.trim();
                const activeTags = Array.from(document.querySelectorAll('.filter-tag.active'))
                    .map(tag => tag.dataset.tag);
                this.loadPosts(1, keyword, activeTags);
            }
        });

        clearFilterBtn.addEventListener('click', () => {
            this.clearFilter();
        });
    }

    showModal(modalId) {
        document.getElementById(modalId).style.display = 'block';
    }

    hideModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
        const form = document.getElementById(modalId).querySelector('form');
        if (form) form.reset();
    }

        updateAuthUI() {
        if (this._updatingAuthUI) {
            return;
        }
        this._updatingAuthUI = true;
        
        try {
            const isLoggedIn = AuthManager.isLoggedIn();
            const loginBtn = document.getElementById('loginBtn');
            const registerBtn = document.getElementById('registerBtn');
            const userMenu = document.getElementById('userMenu');
            const username = document.getElementById('username');
            const newPostBtn = document.getElementById('newPostBtn');
            const newQuestionBtn = document.getElementById('newQuestionBtn');

            if (isLoggedIn) {
                loginBtn.style.display = 'none';
                registerBtn.style.display = 'none';
                userMenu.style.display = 'flex';
                username.textContent = AuthManager.getUsername() || '用戶';
                
                if (newPostBtn) newPostBtn.style.display = 'inline-block';
                if (newQuestionBtn) newQuestionBtn.style.display = 'inline-block';
                
                // 如果當前在關於頁面，重新載入統計信息
                if (this._currentTab === 'about') {
                    this.loadProfileStats();
                }
            } else {
                loginBtn.style.display = 'inline-block';
                registerBtn.style.display = 'inline-block';
                userMenu.style.display = 'none';
                
                if (newPostBtn) newPostBtn.style.display = 'none';
                if (newQuestionBtn) newQuestionBtn.style.display = 'none';
                
                // 如果未登入且在關於頁面，重定向到貼文頁面並顯示提示
                if (this._currentTab === 'about') {
                    this.showTab('posts');
                    ErrorHandler.showError('請先登入才能查看個人資料');
                }
            }
            
            const qaDetailSection = document.getElementById('qa-detail-section');
            if (qaDetailSection && qaDetailSection.style.display !== 'none') {
                // 如果在問答詳情頁面，重新載入整個頁面以更新所有狀態
                const questionId = this.getCurrentQuestionId();
                if (questionId) {
                    // 延遲執行，避免與其他 UI 更新衝突
                    setTimeout(async () => {
                        await this.showQADetail(questionId, true);
                    }, 50);
                }
            }
        } finally {
            this._updatingAuthUI = false;
        }
    }



        async loadInitialData() {
        if (this._loadingInitialData) {
            return;
        }
        this._loadingInitialData = true;
        
        try {
            await this.loadPosts();
            await this.loadQuestions(1, 'desc');
            
            // 檢查當前頁面並載入相應資料
            if (this._currentTab === 'about' && AuthManager.isLoggedIn()) {
                await this.loadProfileStats();
            }
        } finally {
            this._loadingInitialData = false;
        }
    }

    // 載入貼文
    async loadPosts(page = 1, keyword = '', selectedTags = []) {
        const container = document.getElementById('postsContainer');
        LoadingManager.show(container);

        try {
            const params = { page };
            if (keyword) params.keyword = keyword;
            if (selectedTags && selectedTags.length > 0) {
                params.tags = selectedTags.join(',');
            }
            const result = await API.getPosts(params);
            this.currentPosts = result.posts; // 儲存貼文資料
            this.renderPosts(result.posts);
            this.renderPagination(result.current_page, result.num_pages, keyword, selectedTags);
            
            // 如果是第一頁，載入所有標籤
            if (page === 1) {
                await this.loadAllTags();
            }
        } catch (error) {
            console.error('loadPosts: 錯誤', error);
            container.innerHTML = '<p>載入貼文失敗</p>';
        } finally {
            LoadingManager.hide(container);
        }
    }

    // 載入所有標籤
    async loadAllTags() {
        if (this._loadingTags) {
            return;
        }
        this._loadingTags = true;
        
        try {
            const allTags = new Set();
            
            this.currentPosts.forEach(post => {
                if (post.tags) {
                    post.tags.split(',').forEach(tag => {
                        allTags.add(tag.trim());
                    });
                }
            });

            this.renderFilterTags(Array.from(allTags));
        } catch (error) {
            console.error('載入標籤失敗:', error);
        } finally {
            this._loadingTags = false;
        }
    }

    // 渲染篩選標籤
    renderFilterTags(tags) {
        const currentActiveTags = Array.from(document.querySelectorAll('.filter-tag.active'))
            .map(tag => tag.dataset.tag);
        
        const filterTagList = document.getElementById('filterTagList');
        const tagsHTML = tags.map(tag => {
            const isActive = currentActiveTags.includes(tag);
            return `<span class="filter-tag ${isActive ? 'active' : ''}" data-tag="${tag}">${tag}</span>`;
        }).join('');
        filterTagList.innerHTML = tagsHTML;

        if (this._filterTagsEventBound) {
            filterTagList.removeEventListener('click', this._filterTagsClickHandler);
        }
        
        this._filterTagsClickHandler = (e) => {
            if (e.target.classList.contains('filter-tag')) {
                e.target.classList.toggle('active');
                this.filterPostsByTags();
            }
        };
        filterTagList.addEventListener('click', this._filterTagsClickHandler);
        this._filterTagsEventBound = true;
    }

    // 根據標籤篩選貼文
    async filterPostsByTags() {
        const activeTags = Array.from(document.querySelectorAll('.filter-tag.active'))
            .map(tag => tag.dataset.tag);
        
        const clearFilterBtn = document.getElementById('clearFilterBtn');
        if (activeTags.length > 0) {
            clearFilterBtn.style.display = 'inline-block';
        } else {
            clearFilterBtn.style.display = 'none';
        }
        
        await this.loadPosts(1, '', activeTags);
    }

    clearFilter() {
        document.querySelectorAll('.filter-tag.active').forEach(tag => {
            tag.classList.remove('active');
        });
        
        // 隱藏清除篩選按鈕
        document.getElementById('clearFilterBtn').style.display = 'none';
        
        // 回到正常分頁模式
        this.loadPosts(1);
    }

    // 渲染貼文
    renderPosts(posts) {
        const container = document.getElementById('postsContainer');
        
        if (!posts || posts.length === 0) {
            container.innerHTML = '<p>目前沒有貼文</p>';
            return;
        }
        

        const postsHTML = posts.map(post => `
            <div class="post-card" data-post-id="${post.id}" style="cursor: pointer;">
                ${post.image ? `<div class="post-image"><img src="${post.image}" alt="${post.title}" class="post-img"></div>` : ''}
                <div class="post-header">
                    <h3 class="post-title">${post.title}</h3>
                    <div class="post-meta">
                        <span class="author"><i class="fas fa-user"></i> ${post.author || '匿名'}</span>
                        <span class="date"><i class="fas fa-calendar"></i> ${post.created_at}</span>
                    </div>
                </div>
                ${post.tags ? `<div class="post-tags">${post.tags.split(',').map(tag => `<span class="tag">${tag.trim()}</span>`).join('')}</div>` : ''}
                <div class="post-content">
                    <p>${post.content.substring(0, 150)}${post.content.length > 150 ? '...' : ''}</p>
                </div>
                <div class="post-actions">
                    <button class="btn btn-outline-primary read-more-btn">閱讀全文</button>
                </div>
            </div>
        `).join('');

        container.innerHTML = postsHTML;
        
        // 綁定點擊事件
        container.querySelectorAll('.post-card').forEach(card => {
            card.addEventListener('click', (e) => {
                // 如果點擊的是按鈕，不觸發卡片點擊
                if (e.target.classList.contains('read-more-btn')) {
                    return;
                }
                const postId = card.getAttribute('data-post-id');
                this.showPostDetail(postId);
            });
        });
        
        // 綁定按鈕點擊事件
        container.querySelectorAll('.read-more-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const postId = e.target.closest('.post-card').getAttribute('data-post-id');
                this.showPostDetail(postId);
            });
        });
        

    }

    // 分頁渲染
    renderPagination(currentPage, numPages, keyword = '', selectedTags = []) {
        const container = document.getElementById('pagination');
        container.innerHTML = '';

        if (numPages <= 1) {
            container.style.display = 'none';
            return;
        }
        container.style.display = 'block';

        // 上一頁
        const prevBtn = document.createElement('button');
        prevBtn.textContent = '上一頁';
        prevBtn.disabled = currentPage === 1;
        prevBtn.onclick = () => this.loadPosts(currentPage - 1, keyword, selectedTags);
        container.appendChild(prevBtn);

        // 頁碼
        for (let i = 1; i <= numPages; i++) {
            const btn = document.createElement('button');
            btn.textContent = i;
            btn.disabled = i === currentPage;
            btn.onclick = () => this.loadPosts(i, keyword, selectedTags);
            container.appendChild(btn);
        }

        // 下一頁
        const nextBtn = document.createElement('button');
        nextBtn.textContent = '下一頁';
        nextBtn.disabled = currentPage === numPages;
        nextBtn.onclick = () => this.loadPosts(currentPage + 1, keyword, selectedTags);
        container.appendChild(nextBtn);
    }

    // 載入問題
    async loadQuestions(page = 1, order = 'desc') {
        const container = document.getElementById('qa-list');
        LoadingManager.show(container);

        try {
            // 將前端的 order 參數轉換為後端期望的 sort 參數
            let sort = 'latest'; // 預設最新排序
            if (order === 'hot') {
                sort = 'hot';
            }
            
            const response = await API.getQuestions({ 
                page: page,
                size: 5, // 每頁顯示 5 個問題
                sort: sort 
            });
            
            const questions = response.questions || response; // 支援新舊格式
            this.currentQuestions = questions; // 保存問題資料
            this.renderQuestions(questions);
            
            // 渲染分頁
            if (response.total && response.num_pages > 1) {
                this.renderQuestionPagination(response.current_page, response.num_pages, sort);
            } else {
                document.getElementById('qa-pagination').style.display = 'none';
            }
        } catch (error) {
            container.innerHTML = '<p>載入問題失敗</p>';
        } finally {
            LoadingManager.hide(container);
        }
    }

    // 渲染問題
    renderQuestions(questions) {
        const container = document.getElementById('qa-list');
        if (!questions || questions.length === 0) {
            container.innerHTML = '<p>目前沒有問題</p>';
            return;
        }
        container.className = 'qa-list';
        const questionsHTML = questions.map(question => `
            <div class="qa-card" data-id="${question.id}">
                <div class="qa-stats">
                    <div class="qa-like">${question.likes} <span>Like</span></div>
                    <div class="qa-answers ${question.answer_count > 0 ? 'has-answer' : ''}">${question.answer_count} <span>回答</span></div>
                    <div class="qa-views">${question.views} <span>瀏覽</span></div>
                </div>
                <div class="qa-main">
                    <div class="qa-title">${question.title}</div>
                    <div class="qa-meta">
                        ${question.tags ? question.tags.split(',').map(tag => `<span class="qa-tag">${tag.trim()}</span>`).join('') : ''}
                        <span class="qa-author">${question.author || '匿名'}</span>
                        <span class="qa-date">${question.created_at ? question.created_at.split('T')[0] : ''}</span>
                    </div>
                </div>
            </div>
        `).join('');
        container.innerHTML = questionsHTML;
        // 改為留言板模式
        container.querySelectorAll('.qa-card').forEach(card => {
            card.addEventListener('click', () => {
                const qid = card.getAttribute('data-id');
                this.showQADetail(qid);
            });
        });
    }

    // 問題分頁渲染
    renderQuestionPagination(currentPage, numPages, sort) {
        const container = document.getElementById('qa-pagination');
        container.innerHTML = '';

        if (numPages <= 1) {
            container.style.display = 'none';
            return;
        }
        container.style.display = 'block';

        // 上一頁
        const prevBtn = document.createElement('button');
        prevBtn.textContent = '上一頁';
        prevBtn.disabled = currentPage === 1;
        prevBtn.onclick = () => this.loadQuestions(currentPage - 1, sort === 'hot' ? 'hot' : 'desc');
        container.appendChild(prevBtn);

        // 頁碼
        for (let i = 1; i <= numPages; i++) {
            const btn = document.createElement('button');
            btn.textContent = i;
            btn.disabled = i === currentPage;
            btn.onclick = () => this.loadQuestions(i, sort === 'hot' ? 'hot' : 'desc');
            container.appendChild(btn);
        }

        // 下一頁
        const nextBtn = document.createElement('button');
        nextBtn.textContent = '下一頁';
        nextBtn.disabled = currentPage === numPages;
        nextBtn.onclick = () => this.loadQuestions(currentPage + 1, sort === 'hot' ? 'hot' : 'desc');
        container.appendChild(nextBtn);
    }

    // 留言板模式：顯示主題與留言
    async showQADetail(questionId, fromRestore = false) {
        // 移除狀態保存邏輯，避免重新整理時的循環問題
        
        // 增加瀏覽次數
        try {
            await API.viewQuestion(questionId);
        } catch (error) {
            console.log('瀏覽次數更新失敗:', error);
        }
        
        // 載入主題（包含回答和瀏覽記錄）
        const response = await API.getQuestionDetail(questionId);
        const question = response.question;
        const answers = response.answers || [];
        
        // 獲取問題的點讚狀態（需要單獨調用）
        let questionLikeStatus = false;
        try {
            const questionDetail = await API.request(`/questions/${questionId}/`);
            questionLikeStatus = questionDetail.is_liked || false;
        } catch (error) {
            console.log('獲取問題點讚狀態失敗:', error);
        }
        
        const likeIcon = questionLikeStatus ? '❤️' : '👍';
        const likeText = questionLikeStatus ? '收回讚' : '讚';
        const isQuestionAuthor = AuthManager.isLoggedIn() && question.author === AuthManager.getUsername();
        document.getElementById('qa-detail-main').innerHTML = `
            <h2>${question.title}</h2>
            <div class="post-meta">
                <span>提問者: ${question.author || '匿名'}</span>
                <span>提問時間: ${question.created_at}</span>
            </div>
            <div class="question-content">
                <p>${question.content}</p>
            </div>
            <div class="question-actions">
                <button id="like-question-btn" class="btn ${questionLikeStatus ? 'btn-primary' : 'btn-outline-primary'}" data-question-id="${questionId}" data-is-liked="${questionLikeStatus}">
                    ${likeIcon} ${likeText} (${question.likes})
                </button>
                <span class="views-count">👁️ 瀏覽 ${question.views}</span>
                ${isQuestionAuthor ? `<button id="delete-question-btn" class="btn btn-danger" data-question-id="${questionId}">🗑️ 刪除問題</button>` : ''}
            </div>
            <button id="qa-detail-back" class="btn btn-outline-primary" style="margin-top:1rem;">返回列表</button>
        `;
        
        // 綁定問題按讚
        document.getElementById('like-question-btn').onclick = async () => {
            if (!AuthManager.isLoggedIn()) {
                ErrorHandler.showError('請先登入');
                this.showModal('loginModal');
                return;
            }
            try {
                const result = await API.likeQuestion(questionId);
                const btn = document.getElementById('like-question-btn');
                const likeIcon = result.is_liked ? '❤️' : '👍';
                const likeText = result.is_liked ? '收回讚' : '讚';
                
                btn.innerHTML = `${likeIcon} ${likeText}`;
                btn.setAttribute('data-is-liked', result.is_liked);
                btn.className = `btn ${result.is_liked ? 'btn-primary' : 'btn-outline-primary'}`;
                
            } catch (error) {
                if (error.message && (error.message.includes('登入') || error.message.includes('未授權') || error.message.includes('401'))) {
                    ErrorHandler.showError('請先登入');
                    this.showModal('loginModal');
                } else {
                    ErrorHandler.showError('按讚失敗');
                }
            }
        };
        
        // 綁定問題刪除
        const deleteQuestionBtn = document.getElementById('delete-question-btn');
        if (deleteQuestionBtn) {
            deleteQuestionBtn.onclick = async () => {
                if (!AuthManager.isLoggedIn()) {
                    ErrorHandler.showError('請先登入');
                    this.showModal('loginModal');
                    return;
                }
                
                if (!confirm('確定要刪除這個問題嗎？刪除後無法恢復。')) {
                    return;
                }
                
                try {
                    await API.deleteQuestion(questionId);
                    ErrorHandler.showSuccess('問題已刪除');
                    // 返回問題列表
                    document.getElementById('qa-detail-section').style.display = 'none';
                    document.getElementById('qa-section').style.display = '';
                    await this.loadQuestions(1, 'desc');
                } catch (error) {
                    if (error.message && (error.message.includes('登入') || error.message.includes('未授權') || error.message.includes('401'))) {
                        ErrorHandler.showError('請先登入');
                        this.showModal('loginModal');
                    } else {
                        ErrorHandler.showError('刪除失敗：' + (error.message || '未知錯誤'));
                    }
                }
            };
        }
        
        // 使用從API獲取的answers
        document.getElementById('qa-detail-answers-list').innerHTML = answers.map(a => {
            const likeIcon = a.is_liked ? '❤️' : '👍';
            const likeText = a.is_liked ? '收回讚' : '讚';
            const isAuthor = AuthManager.isLoggedIn() && a.author === AuthManager.getUsername();
            return `
                <div class="answer-item" data-answer-id="${a.id}">
                    <div class="post-meta">
                        <span>留言者: ${a.author || '匿名'}</span>
                        <span>留言時間: ${a.created_at}</span>
                    </div>
                    <p>${a.content}</p>
                    <div class="answer-actions">
                        <button class="btn ${a.is_liked ? 'btn-primary' : 'btn-outline-primary'} btn-sm like-answer-btn" data-answer-id="${a.id}" data-is-liked="${a.is_liked}">
                            ${likeIcon} ${likeText} (${a.likes || 0})
                        </button>
                        ${isAuthor ? `<button class="btn btn-danger btn-sm delete-answer-btn" data-answer-id="${a.id}">🗑️ 刪除</button>` : ''}
                    </div>
                </div>
            `;
        }).join('');
        
        // 綁定回答按讚事件
        document.querySelectorAll('.like-answer-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const answerId = btn.getAttribute('data-answer-id');
                
                if (!AuthManager.isLoggedIn()) {
                    ErrorHandler.showError('請先登入');
                    this.showModal('loginModal');
                    return;
                }
                
                try {
                    const result = await API.likeAnswer(answerId);
                    const likeIcon = result.is_liked ? '❤️' : '👍';
                    const likeText = result.is_liked ? '收回讚' : '讚';
                    
                    btn.innerHTML = `${likeIcon} ${likeText}`;
                    btn.setAttribute('data-is-liked', result.is_liked);
                    btn.className = `btn ${result.is_liked ? 'btn-primary' : 'btn-outline-primary'} btn-sm like-answer-btn`;
                    
                } catch (error) {
                    if (error.message && (error.message.includes('登入') || error.message.includes('未授權') || error.message.includes('401'))) {
                        ErrorHandler.showError('請先登入');
                        this.showModal('loginModal');
                    } else {
                        ErrorHandler.showError('按讚失敗');
                    }
                }
            });
        });
        
        document.querySelectorAll('.delete-answer-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const answerId = btn.getAttribute('data-answer-id');
                
                if (!AuthManager.isLoggedIn()) {
                    ErrorHandler.showError('請先登入');
                    this.showModal('loginModal');
                    return;
                }
                
                if (!confirm('確定要刪除這則留言嗎？')) {
                    return;
                }
                
                try {
                    await API.deleteAnswer(answerId);
                    // 從 DOM 中移除該回答
                    const answerItem = btn.closest('.answer-item');
                    answerItem.remove();
                    ErrorHandler.showSuccess('留言已刪除');
                } catch (error) {
                    if (error.message && (error.message.includes('登入') || error.message.includes('未授權') || error.message.includes('401'))) {
                        ErrorHandler.showError('請先登入');
                        this.showModal('loginModal');
                    } else {
                        ErrorHandler.showError('刪除失敗：' + (error.message || '未知錯誤'));
                    }
                }
            });
        });
        
        document.getElementById('qa-section').style.display = 'none';
        document.getElementById('qa-detail-section').style.display = '';
        
        // 根據登入狀態更新留言表單顯示
        const answerFormContainer = document.querySelector('.qa-detail-answer-form');
        if (answerFormContainer) {
            if (AuthManager.isLoggedIn()) {
                // 已登入：顯示留言表單
                answerFormContainer.innerHTML = `
                    <h3>發表留言</h3>
                    <form id="qa-detail-answer-form">
                        <textarea id="qa-detail-answer-content" rows="4" required placeholder="輸入你的留言內容..."></textarea>
                        <button type="submit">送出留言</button>
                    </form>
                `;
                
                // 綁定送出留言（只有已登入時才綁定）
                document.getElementById('qa-detail-answer-form').onsubmit = async (e) => {
                    e.preventDefault();
                    // 檢查是否已登入
                    if (!AuthManager.isLoggedIn()) {
                        ErrorHandler.showError('請先登入後再發表留言');
                        this.showModal('loginModal');
                        return;
                    }
                    const content = document.getElementById('qa-detail-answer-content').value;
                    if (!content.trim()) {
                        ErrorHandler.showError('請輸入留言內容');
                        return;
                    }
                    try {
                        const newAnswer = await API.createAnswer(questionId, { content });
                        // 直接添加新留言到列表
                        const answersContainer = document.getElementById('qa-detail-answers-list');
                        const newAnswerHtml = `
                            <div class="answer-item" data-answer-id="${newAnswer.id}">
                                <div class="post-meta">
                                    <span>留言者: ${newAnswer.author || '匿名'}</span>
                                    <span>留言時間: ${newAnswer.created_at}</span>
                                </div>
                                <p>${newAnswer.content}</p>
                                <div class="answer-actions">
                                    <button class="btn btn-outline-primary btn-sm like-answer-btn" data-answer-id="${newAnswer.id}" data-is-liked="${newAnswer.is_liked || false}">
                                        👍 讚 (${newAnswer.likes || 0})
                                    </button>
                                    <button class="btn btn-danger btn-sm delete-answer-btn" data-answer-id="${newAnswer.id}">🗑️ 刪除</button>
                                </div>
                            </div>
                        `;
                        answersContainer.insertAdjacentHTML('beforeend', newAnswerHtml);
                        
                        // 為新添加的回答綁定按讚事件
                        const newAnswerBtn = answersContainer.querySelector(`[data-answer-id="${newAnswer.id}"] .like-answer-btn`);
                        newAnswerBtn.addEventListener('click', async (e) => {
                            e.stopPropagation();
                            const answerId = newAnswerBtn.getAttribute('data-answer-id');
                            
                            if (!AuthManager.isLoggedIn()) {
                                ErrorHandler.showError('請先登入');
                                this.showModal('loginModal');
                                return;
                            }
                            
                            try {
                                const result = await API.likeAnswer(answerId);
                                const likeIcon = result.is_liked ? '❤️' : '👍';
                                const likeText = result.is_liked ? '收回讚' : '讚';
                                
                                newAnswerBtn.innerHTML = `${likeIcon} ${likeText}`;
                                newAnswerBtn.setAttribute('data-is-liked', result.is_liked);
                                newAnswerBtn.className = `btn ${result.is_liked ? 'btn-primary' : 'btn-outline-primary'} btn-sm like-answer-btn`;
                                
                            } catch (error) {
                                if (error.message && (error.message.includes('登入') || error.message.includes('未授權') || error.message.includes('401'))) {
                                    ErrorHandler.showError('請先登入');
                                    this.showModal('loginModal');
                                } else {
                                    ErrorHandler.showError('按讚失敗');
                                }
                            }
                        });
                        
                        // 為新添加的回答綁定刪除事件
                        const newDeleteBtn = answersContainer.querySelector(`[data-answer-id="${newAnswer.id}"] .delete-answer-btn`);
                        newDeleteBtn.addEventListener('click', async (e) => {
                            e.stopPropagation();
                            const answerId = newDeleteBtn.getAttribute('data-answer-id');
                            
                            if (!AuthManager.isLoggedIn()) {
                                ErrorHandler.showError('請先登入');
                                this.showModal('loginModal');
                                return;
                            }
                            
                            if (!confirm('確定要刪除這則留言嗎？')) {
                                return;
                            }
                            
                            try {
                                await API.deleteAnswer(answerId);
                                // 從 DOM 中移除該回答
                                const answerItem = newDeleteBtn.closest('.answer-item');
                                answerItem.remove();
                                ErrorHandler.showSuccess('留言已刪除');
                            } catch (error) {
                                if (error.message && (error.message.includes('登入') || error.message.includes('未授權') || error.message.includes('401'))) {
                                    ErrorHandler.showError('請先登入');
                                    this.showModal('loginModal');
                                } else {
                                    ErrorHandler.showError('刪除失敗：' + (error.message || '未知錯誤'));
                                }
                            }
                        });
                        document.getElementById('qa-detail-answer-content').value = '';
                    } catch (error) {
                        ErrorHandler.showError(error.message || '留言發布失敗');
                    }
                };
            } else {
                // 未登入：顯示登入提示
                answerFormContainer.innerHTML = `
                    <div class="login-prompt">
                        <h3>發表留言</h3>
                        <p>請先登入後再發表留言</p>
                        <button class="btn btn-primary" onclick="app.showModal('loginModal')">登入</button>
                    </div>
                `;
            }
        }
        
        // 綁定返回按鈕（確保未登入用戶也可以返回）
        document.getElementById('qa-detail-back').onclick = async () => {
            document.getElementById('qa-detail-section').style.display = 'none';
            document.getElementById('qa-section').style.display = '';
            
            // 重新載入問題列表以反映最新狀態
            await this.loadQuestions(1, 'desc');
        };
    }
    
    // 獲取當前問題ID
    getCurrentQuestionId() {
        // 從URL參數或頁面狀態中獲取問題ID
        const urlParams = new URLSearchParams(window.location.search);
        const questionId = urlParams.get('question');
        
        if (questionId) {
            return questionId;
        }
        
        // 如果URL中沒有，嘗試從頁面狀態獲取
        const savedState = localStorage.getItem('blogPageState');
        if (savedState) {
            try {
                const state = JSON.parse(savedState);
                if (state.page === 'qa-detail' && state.data && state.data.questionId) {
                    return state.data.questionId;
                }
            } catch (e) {
                console.error('解析頁面狀態失敗:', e);
            }
        }
        
        return null;
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
            
            this.hideModal('loginModal');
            ErrorHandler.showSuccess('登入成功！');
            
            location.reload();
            
        } catch (error) {
            ErrorHandler.showError(error.message || '登入失敗');
        }
    }

    // 重新整理當前頁面
    async refreshCurrentPage() {
        console.log('重新整理當前頁面...');
        
        // 檢查各個頁面的顯示狀態
        const qaDetailSection = document.getElementById('qa-detail-section');
        const postDetailSection = document.getElementById('post-detail-section');
        const qaSection = document.getElementById('qa-section');
        const postsSection = document.getElementById('posts-section');
        const aboutSection = document.getElementById('about-section');
        
        console.log('頁面狀態:', {
            qaDetail: qaDetailSection?.style.display !== 'none',
            postDetail: postDetailSection?.style.display !== 'none',
            qaList: qaSection?.style.display !== 'none',
            postsList: postsSection?.style.display !== 'none',
            about: aboutSection?.style.display !== 'none'
        });
        
        // 如果在問答詳情頁面，重新載入以更新留言表單
        if (qaDetailSection && qaDetailSection.style.display !== 'none') {
            console.log('重新整理問答詳情頁面');
            const questionId = this.getCurrentQuestionId();
            if (questionId) {
                await this.showQADetail(questionId, true);
            }
        }
        
        // 如果在貼文詳情頁面，重新載入以更新按讚狀態
        if (postDetailSection && postDetailSection.style.display !== 'none') {
            console.log('重新整理貼文詳情頁面');
            const postId = this.getCurrentPostId();
            if (postId) {
                await this.showPostDetail(postId);
            }
        }
        
        // 如果在問答列表頁面，重新載入以更新按讚狀態
        if (qaSection && qaSection.style.display !== 'none') {
            console.log('重新整理問答列表頁面');
            await this.loadQuestions(1, 'desc');
        }
        
        // 如果在貼文列表頁面，重新載入以更新按讚狀態
        if (postsSection && postsSection.style.display !== 'none') {
            console.log('重新整理貼文列表頁面');
            await this.loadPosts(1);
        }
        
        // 如果在關於頁面，重新載入統計資料
        if (aboutSection && aboutSection.style.display !== 'none') {
            console.log('重新整理關於頁面');
            await this.loadProfileStats();
        }
        
        console.log('重新整理完成');
    }

    // 獲取當前貼文ID
    getCurrentPostId() {
        const urlParams = new URLSearchParams(window.location.search);
        const postId = urlParams.get('post');
        
        if (postId) {
            return postId;
        }
        
        // 如果URL中沒有，嘗試從頁面狀態獲取
        const savedState = localStorage.getItem('blogPageState');
        if (savedState) {
            try {
                const state = JSON.parse(savedState);
                if (state.page === 'post-detail' && state.data && state.data.postId) {
                    return state.data.postId;
                }
            } catch (e) {
                console.error('解析頁面狀態失敗:', e);
            }
        }
        
        return null;
    }

    // 處理註冊
    async handleRegister() {
        const form = document.getElementById('registerForm');
        const formData = new FormData(form);
        
        const password = formData.get('password');
        const confirmPassword = formData.get('confirmPassword');
        
        if (password !== confirmPassword) {
            ErrorHandler.showError('密碼確認不匹配');
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
            ErrorHandler.showSuccess('註冊成功！請登入');
        } catch (error) {
            ErrorHandler.showError(error.message || '註冊失敗');
        }
    }

    // 處理創建貼文
    async handleCreatePost() {
        const form = document.getElementById('newPostForm');
        const formData = new FormData(form);
        
        // 收集選中的標籤
        const selectedTags = [];
        const checkboxes = form.querySelectorAll('input[name="tags"]:checked');
        checkboxes.forEach(checkbox => {
            selectedTags.push(checkbox.value);
        });
        
        // 收集自訂標籤
        const customTags = formData.get('customTag');
        
        if (customTags) {
            const customTagArray = customTags.split(',').map(tag => tag.trim()).filter(tag => tag);
            selectedTags.push(...customTagArray);
        }
        
        // 建立 FormData 物件
        const postFormData = new FormData();
        postFormData.append('title', formData.get('title'));
        postFormData.append('content', formData.get('content'));
        postFormData.append('tags', selectedTags.join(','));
        
        // 添加圖片（如果有的話）
        const imageFile = formData.get('image');
        if (imageFile && imageFile.size > 0) {
            postFormData.append('image', imageFile);
        }

        try {
            let res = await API.createPost(postFormData);            
            this.hideModal('newPostModal');
            
            // 重新載入貼文
            this.loadPosts();
        } catch (error) {
            ErrorHandler.showError(error.message || '發布失敗');
        }
    }

    // 處理創建問題
    async handleCreateQuestion() {
        const form = document.getElementById('newQuestionForm');
        const formData = new FormData(form);
        
        const title = formData.get('title').trim();
        const content = formData.get('content').trim();
        const tags = formData.get('tags').trim();
        
        // 前端驗證
        if (title.length < 5) {
            ErrorHandler.showError('標題至少需要5個字符');
            return;
        }
        
        if (content.length < 10) {
            ErrorHandler.showError('內容至少需要10個字符');
            return;
        }
        
        const questionData = {
            title: title,
            content: content,
            tags: tags
        };

        try {
            await API.createQuestion(questionData);
            
            this.hideModal('questionModal');
            
            // 清空表單
            form.reset();
            
            // 重新載入問題
            this.loadQuestions();
            
            ErrorHandler.showSuccess('問題發布成功！');
        } catch (error) {
            ErrorHandler.showError(error.message || '發布失敗');
        }
    }

    // 圖片上傳預覽功能
    setupImageUpload() {
        const imageInput = document.getElementById('postImage');
        const imagePreview = document.getElementById('imagePreview');
        const previewImg = document.getElementById('previewImg');
        const removeImageBtn = document.getElementById('removeImage');

        imageInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    previewImg.src = e.target.result;
                    imagePreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });

        removeImageBtn.addEventListener('click', () => {
            imageInput.value = '';
            imagePreview.style.display = 'none';
            previewImg.src = '';
        });
    }

    // 標籤選擇效果
    setupTagSelection() {
        const tagOptions = document.querySelectorAll('.tag-option');
        
        tagOptions.forEach(option => {
            const checkbox = option.querySelector('input[type="checkbox"]');
            const label = option.querySelector('.tag-label');
            
            checkbox.addEventListener('change', () => {
                if (checkbox.checked) {
                    option.style.background = '#667eea';
                    option.style.borderColor = '#667eea';
                    label.style.color = 'white';
                    label.style.fontWeight = '600';
                } else {
                    option.style.background = 'white';
                    option.style.borderColor = '#e1e5e9';
                    label.style.color = '#666';
                    label.style.fontWeight = 'normal';
                }
            });
        });
    }

    // 顯示貼文詳情
    async showPostDetail(postId) {
        document.getElementById('posts-section').style.display = 'none';
        document.getElementById('qa-section').style.display = 'none';
        document.getElementById('qa-detail-section').style.display = 'none';
        document.getElementById('post-detail-section').style.display = 'block';
        
        document.getElementById('nav-posts').classList.remove('active');
        document.getElementById('nav-qa').classList.remove('active');
        
        try {
            const post = this.currentPosts.find(p => p.id === parseInt(postId));
            if (!post) {
                throw new Error('貼文不存在');
            }
            
            const isPostAuthor = AuthManager.isLoggedIn() && post.author === AuthManager.getUsername();
            
            document.getElementById('post-detail-main').innerHTML = `
                <h1>${post.title}</h1>
                <div class="post-meta">
                    <span><i class="fas fa-user"></i> ${post.author || '匿名'}</span>
                    <span><i class="fas fa-calendar"></i> ${post.created_at}</span>
                </div>
                ${post.tags ? `<div class="post-tags">${post.tags.split(',').map(tag => `<span class="tag">${tag.trim()}</span>`).join('')}</div>` : ''}
                ${post.image ? `<div class="post-image"><img src="${post.image}" alt="${post.title}" style="width: 100%; height: auto; max-height: 600px; object-fit: cover; border-radius: 12px; box-shadow: 0 6px 20px rgba(0,0,0,0.15); transition: transform 0.3s ease;"></div>` : ''}
                <div class="post-content">
                    <p>${post.content}</p>
                </div>
                ${isPostAuthor ? `<button id="delete-post-detail-btn" class="btn btn-danger" data-post-id="${postId}">🗑️ 刪除貼文</button>` : ''}
            `;
            
            document.getElementById('post-detail-back').onclick = () => {
                this.hidePostDetail();
            };
            
            const deletePostDetailBtn = document.getElementById('delete-post-detail-btn');
            if (deletePostDetailBtn) {
                deletePostDetailBtn.onclick = async () => {
                    if (!AuthManager.isLoggedIn()) {
                        ErrorHandler.showError('請先登入');
                        this.showModal('loginModal');
                        return;
                    }
                    
                    if (!confirm('確定要刪除這篇貼文嗎？刪除後無法恢復。')) {
                        return;
                    }
                    
                    try {
                        await API.deletePost(postId);
                        ErrorHandler.showSuccess('貼文已刪除');
                        this.hidePostDetail();
                        await this.loadPosts();
                    } catch (error) {
                        if (error.message && (error.message.includes('登入') || error.message.includes('未授權') || error.message.includes('401'))) {
                            ErrorHandler.showError('請先登入');
                            this.showModal('loginModal');
                        } else {
                            ErrorHandler.showError('刪除失敗：' + (error.message || '未知錯誤'));
                        }
                    }
                };
            }
            
            const detailImage = document.querySelector('.post-detail-main .post-image img');
            if (detailImage) {
                const isMobile = window.innerWidth <= 768;
                if (isMobile) {
                    detailImage.style.maxHeight = '400px';
                }
                
                detailImage.addEventListener('mouseenter', () => {
                    detailImage.style.transform = 'scale(1.02)';
                });
                detailImage.addEventListener('mouseleave', () => {
                    detailImage.style.transform = 'scale(1)';
                });
            }
            
        } catch (error) {
            document.getElementById('post-detail-main').innerHTML = `
                <h1>載入失敗</h1>
                <p>無法載入貼文內容：${error.message}</p>
            `;
        }
    }
    
    hidePostDetail() {
        document.getElementById('post-detail-section').style.display = 'none';
        document.getElementById('posts-section').style.display = 'block';
        document.getElementById('nav-posts').classList.add('active');
        this._currentTab = 'posts';
        
        localStorage.removeItem('blogPageState');
    }

    async handleLogout() {
        await AuthManager.logout();
        ErrorHandler.showSuccess('已登出');
        
        const qaDetailSection = document.getElementById('qa-detail-section');
        if (qaDetailSection && qaDetailSection.style.display !== 'none') {
            const questionId = this.getCurrentQuestionId();
            if (questionId) {
                await this.showQADetail(questionId, true);
            }
        }
    }
    
    // 回到貼文頁面
    async goToHomePage() {
        
        document.getElementById('posts-section').style.display = '';
        document.getElementById('qa-section').style.display = 'none';
        document.getElementById('qa-detail-section').style.display = 'none';
        
        document.getElementById('nav-posts').classList.add('active');
        document.getElementById('nav-qa').classList.remove('active');
        this._currentTab = 'posts';
        
        await this.loadPosts(1);
        
    }

    // 載入用戶統計信息
    async loadProfileStats() {
        if (!AuthManager.isLoggedIn()) {
            // 如果未登入，重定向到貼文頁面
            this.showTab('posts');
            return;
        }
        
        try {
            const stats = await API.getProfileStats();
            
            // 更新統計數字
            document.getElementById('posts-count').textContent = stats.posts_count;
            document.getElementById('questions-count').textContent = stats.questions_count;
            document.getElementById('answers-count').textContent = stats.answers_count;
        } catch (error) {
            console.error('載入用戶統計失敗:', error);
            if (error.message.includes('未授權') || error.message.includes('無效')) {
                // 如果認證失敗，清除登入狀態並重定向
                AuthManager.clearAccessToken();
                this.updateAuthUI();
                this.showTab('posts');
                ErrorHandler.showError('登入已過期，請重新登入');
            } else {
                ErrorHandler.showError('載入統計信息失敗');
            }
        }
    }

    // 處理更改密碼
    async handleChangePassword(e) {
        e.preventDefault();
        
        const oldPassword = document.getElementById('oldPassword').value;
        const newPassword = document.getElementById('changeNewPassword').value;
        const confirmNewPassword = document.getElementById('changeConfirmNewPassword').value;
        
        if (!oldPassword || !newPassword || !confirmNewPassword) {
            ErrorHandler.showError('請填寫所有欄位');
            return;
        }
        
        if (newPassword !== confirmNewPassword) {
            ErrorHandler.showError('新密碼與確認密碼不符');
            return;
        }
        
        if (newPassword.length < 6) {
            ErrorHandler.showError('新密碼至少需要6個字符');
            return;
        }
        
        try {
            const response = await API.changePassword(oldPassword, newPassword);
            ErrorHandler.showSuccess(response.message || '密碼更改成功！');
            
            // 清空表單
            document.getElementById('changePasswordForm').reset();
            
            // 如果後端要求重新登入
            if (response.require_relogin) {
                // 清除登入狀態
                AuthManager.clearAccessToken();
                this.updateAuthUI();
                
                // 重定向到貼文頁面
                this.showTab('posts');
                
                // 顯示重新登入提示
                setTimeout(() => {
                    ErrorHandler.showError('密碼已更改，請重新登入');
                }, 1000);
            }
        } catch (error) {
            if (error.message.includes('未授權') || error.message.includes('無效')) {
                // 如果認證失敗，清除登入狀態並重定向
                AuthManager.clearAccessToken();
                this.updateAuthUI();
                this.showTab('posts');
                ErrorHandler.showError('登入已過期，請重新登入');
            } else {
                ErrorHandler.showError(error.message || '密碼更改失敗');
            }
        }
    }

    // 處理更改用戶名
    async handleChangeUsername(e) {
        e.preventDefault();
        
        const newUsername = document.getElementById('newUsername').value.trim();
        
        if (!newUsername) {
            ErrorHandler.showError('請輸入新用戶名');
            return;
        }
        
        if (newUsername.length < 2) {
            ErrorHandler.showError('用戶名至少需要2個字符');
            return;
        }
        
        try {
            const response = await API.changeUsername(newUsername);
            ErrorHandler.showSuccess(response.message || '用戶名更改成功！');
            
            // 更新 AuthManager 中的用戶名
            AuthManager.setAccessToken(AuthManager.getAccessToken(), newUsername);
            
            // 更新 UI 顯示的用戶名
            this.updateAuthUI();
            
            // 重新載入統計信息以更新頁面
            if (this._currentTab === 'about') {
                this.loadProfileStats();
            }
            
            // 清空表單
            document.getElementById('changeUsernameForm').reset();
        } catch (error) {
            if (error.message.includes('未授權') || error.message.includes('無效')) {
                // 如果認證失敗，清除登入狀態並重定向
                AuthManager.clearAccessToken();
                this.updateAuthUI();
                this.showTab('posts');
                ErrorHandler.showError('登入已過期，請重新登入');
            } else {
                ErrorHandler.showError(error.message || '用戶名更改失敗');
            }
        }
    }

    // 顯示指定頁面
    showTab(tab) {
        this._currentTab = tab;
        
        // 隱藏所有頁面
        document.getElementById('posts-section').style.display = 'none';
        document.getElementById('qa-section').style.display = 'none';
        document.getElementById('qa-detail-section').style.display = 'none';
        document.getElementById('post-detail-section').style.display = 'none';
        document.getElementById('about-section').style.display = 'none';
        
        // 移除所有導航項的 active 狀態
        document.getElementById('nav-posts').classList.remove('active');
        document.getElementById('nav-qa').classList.remove('active');
        document.getElementById('nav-about').classList.remove('active');
        
        if (tab === 'posts') {
            document.getElementById('posts-section').style.display = '';
            document.getElementById('nav-posts').classList.add('active');
        } else if (tab === 'qa') {
            document.getElementById('qa-section').style.display = '';
            document.getElementById('nav-qa').classList.add('active');
        } else if (tab === 'about') {
            document.getElementById('about-section').style.display = '';
            document.getElementById('nav-about').classList.add('active');
            
            // 根據登入狀態顯示不同內容
            if (AuthManager.isLoggedIn()) {
                // 已登入：顯示統計信息和帳號管理
                document.getElementById('login-required-message').style.display = 'none';
                document.getElementById('stats-container').style.display = '';
                document.querySelector('.account-management').style.display = '';
                this.loadProfileStats();
            } else {
                // 未登入：顯示登入提示
                document.getElementById('login-required-message').style.display = '';
                document.getElementById('stats-container').style.display = 'none';
                document.querySelector('.account-management').style.display = 'none';
            }
        }
        
        localStorage.setItem('blogTab', tab);
    }

    // 忘記密碼相關方法
    async handleForgotPassword(e) {
        e.preventDefault();
        
        const email = document.getElementById('forgotEmail').value.trim();
        
        if (!email) {
            ErrorHandler.showError('請輸入電子郵件地址');
            return;
        }
        
        try {
            await API.forgotPassword(email);
            ErrorHandler.showSuccess('驗證碼已發送，請檢查您的郵箱');
            
            // 切換到步驟2
            this.showForgotPasswordStep(2);
            
        } catch (error) {
            ErrorHandler.showError(error.message || '發送驗證碼失敗');
        }
    }

    async handleVerifyToken(e) {
        e.preventDefault();
        
        const token = document.getElementById('resetToken').value.trim();
        const email = document.getElementById('forgotEmail').value.trim();
        
        if (!token) {
            ErrorHandler.showError('請輸入驗證碼');
            return;
        }
        
        try {
            await API.verifyResetToken(email, token);
            ErrorHandler.showSuccess('驗證碼正確');
            
            // 切換到步驟3
            this.showForgotPasswordStep(3);
            
        } catch (error) {
            ErrorHandler.showError(error.message || '驗證碼錯誤');
        }
    }

    async handleResetPassword(e) {
        e.preventDefault();
        
        const newPassword = document.getElementById('newPassword').value;
        const confirmNewPassword = document.getElementById('confirmNewPassword').value;
        const token = document.getElementById('resetToken').value.trim();
        const email = document.getElementById('forgotEmail').value.trim();
        
        if (!newPassword || !confirmNewPassword) {
            ErrorHandler.showError('請填寫所有欄位');
            return;
        }
        
        if (newPassword !== confirmNewPassword) {
            ErrorHandler.showError('新密碼與確認密碼不符');
            return;
        }
        
        if (newPassword.length < 6) {
            ErrorHandler.showError('新密碼至少需要6個字符');
            return;
        }
        
        try {
            await API.resetPassword(email, token, newPassword);
            ErrorHandler.showSuccess('密碼重設成功！請使用新密碼登入');
            
            // 關閉忘記密碼模態框
            this.hideModal('forgotPasswordModal');
            
            // 清空表單
            this.resetForgotPasswordForm();
            
        } catch (error) {
            ErrorHandler.showError(error.message || '密碼重設失敗');
        }
    }

    showForgotPasswordStep(step) {
        // 隱藏所有步驟
        document.getElementById('step1').style.display = 'none';
        document.getElementById('step2').style.display = 'none';
        document.getElementById('step3').style.display = 'none';
        
        // 顯示指定步驟
        document.getElementById(`step${step}`).style.display = 'block';
    }

    resetForgotPasswordForm() {
        // 重置到步驟1
        this.showForgotPasswordStep(1);
        
        // 清空所有表單
        document.getElementById('forgotPasswordForm').reset();
        document.getElementById('verifyTokenForm').reset();
        document.getElementById('resetPasswordForm').reset();
    }
    
    savePageState(page, data = {}) {
        const state = {
            page: page,
            data: data,
            timestamp: Date.now()
        };
        localStorage.setItem('blogPageState', JSON.stringify(state));
    }
    
    async restorePageState() {
        const savedState = localStorage.getItem('blogPageState');
        if (!savedState) return false;
        
        try {
            const state = JSON.parse(savedState);
            const now = Date.now();
            const oneHour = 60 * 60 * 1000;
            
            if (now - state.timestamp > oneHour) {
                localStorage.removeItem('blogPageState');
            }
        } catch (error) {
            console.error('清除舊狀態失敗:', error);
            localStorage.removeItem('blogPageState');
        }
        return false;
    }
}

const app = new BlogApp();
window.app = app;

document.addEventListener('DOMContentLoaded', () => {
        app.init();
});