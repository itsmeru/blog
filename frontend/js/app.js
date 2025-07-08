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
        // 防止重複初始化
        if (this._initialized) {
            return;
        }
        this._initialized = true;
        
        // 先檢查並恢復登入狀態
        await AuthManager.checkAuthStatus();
        
        // 設置事件監聽器
        this.setupEventListeners();
        this.setupModalEvents();
        this.setupFormEvents();
        this.setupSearchEvents();
        this.setupImageUpload();
        this.setupTagSelection();
        this.updateAuthUI();
        this.setupNavigationEvents();
        
        // 嘗試恢復頁面狀態
        const restored = await this.restorePageState();
        
        // 載入初始資料
        await this.loadInitialData();
    }

    setupEventListeners() {
        // 登入註冊按鈕
        document.getElementById('loginBtn').addEventListener('click', () => this.showModal('loginModal'));
        document.getElementById('registerBtn').addEventListener('click', () => this.showModal('registerModal'));
        document.getElementById('logoutBtn').addEventListener('click', () => this.handleLogout());

        // 新貼文和問題按鈕
        document.getElementById('newPostBtn').addEventListener('click', () => this.showModal('newPostModal'));
        document.getElementById('newQuestionBtn').addEventListener('click', () => this.showModal('questionModal'));
        
        // 部落格標題回到貼文頁面
        const homePage = document.getElementById('home-page');
        if (homePage) {
            homePage.addEventListener('click', () => this.goToHomePage());
            console.log('home-page 事件監聽器已綁定');
        } else {
            console.log('找不到 home-page 元素');
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
    }

    setupNavigationEvents() {
        // 防止重複綁定事件
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
            
            if (tab === 'posts') {
                document.getElementById('posts-section').style.display = '';
                document.getElementById('qa-section').style.display = 'none';
                document.getElementById('qa-detail-section').style.display = 'none';
                document.getElementById('post-detail-section').style.display = 'none';
                document.getElementById('nav-posts').classList.add('active');
                document.getElementById('nav-qa').classList.remove('active');
            } else {
                document.getElementById('posts-section').style.display = 'none';
                document.getElementById('qa-section').style.display = '';
                document.getElementById('qa-detail-section').style.display = 'none';
                document.getElementById('post-detail-section').style.display = 'none';
                document.getElementById('nav-qa').classList.add('active');
                document.getElementById('nav-posts').classList.remove('active');
            }
            // 記錄目前分頁
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
    
        // 初始化時設置預設分頁，但不觸發載入
        this.initializeDefaultTab(showTab);
    }

    // 新增：初始化預設分頁但不觸發資料載入
    initializeDefaultTab(showTab) {
        const savedState = localStorage.getItem('blogPageState');
        if (savedState) {
            // 如果有保存的頁面狀態，不要自動切換分頁
            return;
        }
        
            const savedTab = localStorage.getItem('blogTab');
        const defaultTab = savedTab === 'qa' ? 'qa' : 'posts';
        
        // 設置 UI 狀態但不觸發資料載入
        this._currentTab = defaultTab;
        if (defaultTab === 'qa') {
            document.getElementById('posts-section').style.display = 'none';
            document.getElementById('qa-section').style.display = '';
            document.getElementById('nav-qa').classList.add('active');
            document.getElementById('nav-posts').classList.remove('active');
            } else {
            document.getElementById('posts-section').style.display = '';
            document.getElementById('qa-section').style.display = 'none';
            document.getElementById('nav-posts').classList.add('active');
            document.getElementById('nav-qa').classList.remove('active');
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
        // 清空表單
        const form = document.getElementById(modalId).querySelector('form');
        if (form) form.reset();
    }

        updateAuthUI() {
        // 防止重複更新
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
                
                // 顯示發布按鈕
                if (newPostBtn) newPostBtn.style.display = 'inline-block';
                if (newQuestionBtn) newQuestionBtn.style.display = 'inline-block';
            } else {
                loginBtn.style.display = 'inline-block';
                registerBtn.style.display = 'inline-block';
                userMenu.style.display = 'none';
                
                // 隱藏發布按鈕
                if (newPostBtn) newPostBtn.style.display = 'none';
                if (newQuestionBtn) newQuestionBtn.style.display = 'none';
            }
        } finally {
            this._updatingAuthUI = false;
        }
    }



        async loadInitialData() {
        // 避免重複載入
        if (this._loadingInitialData) {
            return;
        }
        this._loadingInitialData = true;
        
        try {
            await this.loadPosts();
            await this.loadQuestions();
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
    async loadQuestions() {
        const container = document.getElementById('qa-list');
        LoadingManager.show(container);

        try {
            const questions = await API.getQuestions();
            this.currentQuestions = questions; // 保存問題資料
            this.renderQuestions(questions);
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

    // 留言板模式：顯示主題與留言
    async showQADetail(questionId, fromRestore = false) {
        // 只有不是 restore 狀態時才存
        if (!fromRestore) {
        this.savePageState('qa-detail', { questionId });
        }
        
                // 載入主題（包含回答和瀏覽記錄）
        const question = await API.getQuestion(questionId);
        const likeIcon = question.is_liked ? '❤️' : '👍';
        const likeText = question.is_liked ? '收回讚' : '讚';
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
                <button id="like-question-btn" class="btn ${question.is_liked ? 'btn-primary' : 'btn-outline-primary'}" data-question-id="${questionId}" data-is-liked="${question.is_liked}">
                    ${likeIcon} ${likeText} (${question.likes})
                </button>
                <span class="views-count">👁️ 瀏覽 ${question.views}</span>
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
                
                btn.innerHTML = `${likeIcon} ${likeText} (${result.likes})`;
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
        
        // 使用 question.answers 而不是單獨呼叫 API
        const answers = question.answers || [];
        document.getElementById('qa-detail-answers-list').innerHTML = answers.map(a => {
            const likeIcon = a.is_liked ? '❤️' : '👍';
            const likeText = a.is_liked ? '收回讚' : '讚';
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
                    
                    btn.innerHTML = `${likeIcon} ${likeText} (${result.likes})`;
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
        
        // 顯示留言板區塊
        document.getElementById('qa-section').style.display = 'none';
        document.getElementById('qa-detail-section').style.display = '';
        
        // 綁定送出留言
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
                            <button class="btn btn-outline-primary btn-sm like-answer-btn" data-answer-id="${newAnswer.id}" data-is-liked="false">
                                👍 讚 (${newAnswer.likes || 0})
                            </button>
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
                        
                        newAnswerBtn.innerHTML = `${likeIcon} ${likeText} (${result.likes})`;
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
                document.getElementById('qa-detail-answer-content').value = '';
            } catch (error) {
                ErrorHandler.showError(error.message || '留言發布失敗');
            }
        };
        
        // 綁定返回按鈕
        document.getElementById('qa-detail-back').onclick = async () => {
            this.savePageState('qa-list');
            document.getElementById('qa-detail-section').style.display = 'none';
            document.getElementById('qa-section').style.display = '';
            
            // 重新載入問題列表以反映最新狀態
            await this.loadQuestions();
        };
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
            ErrorHandler.showSuccess('登入成功！');
            
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
            console.log(error.message || '註冊失敗');
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
            
            this.hideModal('questionModal');
            
            // 重新載入問題
            this.loadQuestions();
        } catch (error) {
            console.log(error.message || '發布失敗');
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
        // 保存頁面狀態
        this.savePageState('post-detail', { postId });
        
        // 隱藏其他區塊
        document.getElementById('posts-section').style.display = 'none';
        document.getElementById('qa-section').style.display = 'none';
        document.getElementById('qa-detail-section').style.display = 'none';
        document.getElementById('post-detail-section').style.display = 'block';
        
        // 更新導航狀態
        document.getElementById('nav-posts').classList.remove('active');
        document.getElementById('nav-qa').classList.remove('active');
        
        try {
            // 從當前貼文列表中找到貼文
            const post = this.currentPosts.find(p => p.id === parseInt(postId));
            if (!post) {
                throw new Error('貼文不存在');
            }
            
            // 渲染貼文詳情
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
            `;
            
            // 綁定返回按鈕
            document.getElementById('post-detail-back').onclick = () => {
                this.hidePostDetail();
            };
            
            // 為圖片添加懸停效果和響應式樣式
            const detailImage = document.querySelector('.post-detail-main .post-image img');
            if (detailImage) {
                // 檢查是否為手機版
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
    
    // 隱藏貼文詳情
    hidePostDetail() {
        document.getElementById('post-detail-section').style.display = 'none';
        document.getElementById('posts-section').style.display = 'block';
        document.getElementById('nav-posts').classList.add('active');
        this._currentTab = 'posts';
        
        // 清除保存的狀態
        localStorage.removeItem('blogPageState');
    }

    // 處理登出
    async handleLogout() {
        await AuthManager.logout();
        ErrorHandler.showSuccess('已登出');
    }
    
    // 回到貼文頁面
    async goToHomePage() {
        console.log('goToHomePage 被呼叫');
        
        // 切換到貼文頁面
        document.getElementById('posts-section').style.display = '';
        document.getElementById('qa-section').style.display = 'none';
        document.getElementById('qa-detail-section').style.display = 'none';
        
        // 更新導航狀態
        document.getElementById('nav-posts').classList.add('active');
        document.getElementById('nav-qa').classList.remove('active');
        this._currentTab = 'posts';
        
        // 重新載入貼文
        await this.loadPosts(1);
        
        console.log('goToHomePage 完成');
    }
    
    // 保存頁面狀態
    savePageState(page, data = {}) {
        const state = {
            page: page,
            data: data,
            timestamp: Date.now()
        };
        localStorage.setItem('blogPageState', JSON.stringify(state));
    }
    
    // 恢復頁面狀態
    async restorePageState() {
        const savedState = localStorage.getItem('blogPageState');
        if (!savedState) return false;
        
        try {
            const state = JSON.parse(savedState);
            const now = Date.now();
            const oneHour = 60 * 60 * 1000; // 1小時
            
            // 如果狀態太舊，清除它
            if (now - state.timestamp > oneHour) {
                localStorage.removeItem('blogPageState');
                return false;
            }
            
            localStorage.removeItem('blogPageState');
            return false;
        } catch (error) {
            console.error('恢復頁面狀態失敗:', error);
            localStorage.removeItem('blogPageState');
        }
        return false;
    }
}

// 初始化應用
const app = new BlogApp();
window.app = app; // 設置全局引用

// 防止重複初始化
let initCalled = false;
document.addEventListener('DOMContentLoaded', () => {
    if (!initCalled) {
        initCalled = true;
        app.init();
    }
});