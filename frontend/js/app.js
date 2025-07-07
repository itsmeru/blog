class BlogApp {
    constructor() {
        this.currentPosts = [];
        this.currentQuestions = [];
    }

    async init() {
        // 先檢查並恢復登入狀態
        await AuthManager.checkAuthStatus();
        
        this.setupEventListeners();
        this.setupModalEvents();
        this.setupFormEvents();
        this.setupSearchEvents();
        this.setupImageUpload();
        this.setupTagSelection();
        this.updateAuthUI();
        await this.loadInitialData();
        
        // 先恢復頁面狀態，再設定導航事件
        await this.restorePageState();
        this.setupNavigationEvents();
    }

    setupEventListeners() {
        // 登入註冊按鈕
        document.getElementById('loginBtn').addEventListener('click', () => this.showModal('loginModal'));
        document.getElementById('registerBtn').addEventListener('click', () => this.showModal('registerModal'));
        document.getElementById('logoutBtn').addEventListener('click', () => this.handleLogout());

        // 新貼文和問題按鈕
        document.getElementById('newPostBtn').addEventListener('click', () => this.showModal('newPostModal'));
        document.getElementById('newQuestionBtn').addEventListener('click', () => this.showModal('questionModal'));
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

        // 新問題表單（修正 id）
        document.getElementById('newQuestionForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleCreateQuestion();
        });
    }

    setupNavigationEvents() {
        const showTab = (tab) => {
            if (tab === 'posts') {
                document.getElementById('posts-section').style.display = '';
                document.getElementById('qa-section').style.display = 'none';
                document.getElementById('qa-detail-section').style.display = 'none';
                document.getElementById('nav-posts').classList.add('active');
                document.getElementById('nav-qa').classList.remove('active');
            } else {
                document.getElementById('posts-section').style.display = 'none';
                document.getElementById('qa-section').style.display = '';
                document.getElementById('qa-detail-section').style.display = 'none';
                document.getElementById('nav-qa').classList.add('active');
                document.getElementById('nav-posts').classList.remove('active');
            }
            // 記錄目前分頁
            localStorage.setItem('blogTab', tab);
            this.savePageState(tab);
        };
    
        document.getElementById('nav-posts').onclick = (e) => {
            e.preventDefault();
            showTab('posts');
        };
        document.getElementById('nav-qa').onclick = (e) => {
            e.preventDefault();
            showTab('qa');
        };
    
        // 只有在沒有頁面狀態時才自動切換
        const savedState = localStorage.getItem('blogPageState');
        if (!savedState) {
            const savedTab = localStorage.getItem('blogTab');
            if (savedTab === 'qa') {
                showTab('qa');
            } else {
                showTab('posts');
            }
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
    }

    async loadInitialData() {
        await this.loadPosts();
        await this.loadQuestions();
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
            container.innerHTML = '<p>載入貼文失敗</p>';
        } finally {
            LoadingManager.hide(container);
        }
    }

    // 載入所有標籤
    async loadAllTags() {
        try {
            // 載入所有貼文來收集標籤（不分頁）
            const result = await API.getPosts({ page: 1, size: 1000 }); // 載入大量貼文
            const allTags = new Set();
            
            result.posts.forEach(post => {
                if (post.tags) {
                    post.tags.split(',').forEach(tag => {
                        allTags.add(tag.trim());
                    });
                }
            });

            this.renderFilterTags(Array.from(allTags));
        } catch (error) {
            console.error('載入標籤失敗:', error);
        }
    }

    // 渲染篩選標籤
    renderFilterTags(tags) {
        // 保存當前選中的標籤
        const currentActiveTags = Array.from(document.querySelectorAll('.filter-tag.active'))
            .map(tag => tag.dataset.tag);
        
        const filterTagList = document.getElementById('filterTagList');
        const tagsHTML = tags.map(tag => {
            const isActive = currentActiveTags.includes(tag);
            return `<span class="filter-tag ${isActive ? 'active' : ''}" data-tag="${tag}">${tag}</span>`;
        }).join('');
        filterTagList.innerHTML = tagsHTML;

        // 添加點擊事件
        filterTagList.querySelectorAll('.filter-tag').forEach(tag => {
            tag.addEventListener('click', () => {
                console.log('標籤點擊:', tag.dataset.tag);
                tag.classList.toggle('active');
                console.log('標籤狀態:', tag.classList.contains('active'));
                this.filterPostsByTags();
            });
        });
    }

    // 根據標籤篩選貼文
    async filterPostsByTags() {
        const activeTags = Array.from(document.querySelectorAll('.filter-tag.active'))
            .map(tag => tag.dataset.tag);
        
        // 顯示或隱藏清除篩選按鈕
        const clearFilterBtn = document.getElementById('clearFilterBtn');
        if (activeTags.length > 0) {
            clearFilterBtn.style.display = 'inline-block';
        } else {
            clearFilterBtn.style.display = 'none';
        }
        
        // 重新載入貼文，包含標籤篩選
        await this.loadPosts(1, '', activeTags);
    }

    // 清除篩選
    clearFilter() {
        // 清除所有選中的標籤
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
        console.log(posts);
        

        const postsHTML = posts.map(post => `
            <div class="post-card">
                ${post.image ? `<div class="post-image"><img src="${post.image}" alt="${post.title}" class="post-img"></div>` : ''}
                <div class="post-header">
                    <h3 class="post-title">${post.title}</h3>
                    <div class="post-meta">
                        <span class="author"><i class="fas fa-user"></i> ${post.author || '匿名'}</span>
                        <span class="date"><i class="fas fa-calendar"></i> ${post.created_at}</span>
                    </div>
                </div>
                ${post.tags ? `<div class="post-tags">${post.tags.split(',').map(tag => `<span class="tag">${tag.trim()}</span>`).join('')}</div>` : ''}
                <div class="post-content" id="post-content-${post.id}">
                    <p>${post.content.substring(0, 100)}${post.content.length > 100 ? '...' : ''}</p>
                </div>
                ${post.content.length > 100 ? `<button class="btn btn-outline-primary" onclick="app.togglePostContent(${post.id})" id="toggle-btn-${post.id}">閱讀更多</button>` : ''}
            </div>
        `).join('');

        container.innerHTML = postsHTML;
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
    async showQADetail(questionId) {
        // 保存當前狀態
        this.savePageState('qa-detail', { questionId });
        
        // 載入主題
        const question = await API.getQuestion(questionId);
        document.getElementById('qa-detail-main').innerHTML = `
            <h2>${question.title}</h2>
            <div class="post-meta">
                <span>提問者: ${question.author || '匿名'}</span>
                <span>提問時間: ${question.created_at}</span>
            </div>
            <div class="question-content">
                <p>${question.content}</p>
            </div>
            <button id="qa-detail-back" class="btn btn-outline-primary" style="margin-top:1rem;">返回列表</button>
        `;
        // 載入留言
        const answers = await API.getAnswers(questionId);
        document.getElementById('qa-detail-answers-list').innerHTML = answers.map(a => `
            <div class="answer-item">
                <div class="post-meta">
                    <span>留言者: ${a.author || '匿名'}</span>
                    <span>留言時間: ${a.created_at}</span>
                </div>
                <p>${a.content}</p>
            </div>
        `).join('');
        // 顯示留言板區塊
        document.getElementById('qa-section').style.display = 'none';
        document.getElementById('qa-detail-section').style.display = '';
        // 綁定送出留言
        document.getElementById('qa-detail-answer-form').onsubmit = async (e) => {
            e.preventDefault();
            // 檢查是否已登入
            if (!AuthManager.isAuthenticated()) {
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
                    <div class="answer-item">
                        <div class="post-meta">
                            <span>留言者: ${newAnswer.author || '匿名'}</span>
                            <span>留言時間: ${newAnswer.created_at}</span>
                        </div>
                        <p>${newAnswer.content}</p>
                    </div>
                `;
                answersContainer.insertAdjacentHTML('beforeend', newAnswerHtml);
                document.getElementById('qa-detail-answer-content').value = '';
                ErrorHandler.showSuccess('留言發布成功！');
            } catch (error) {
                ErrorHandler.showError(error.message || '留言發布失敗');
            }
        };
        // 綁定返回按鈕
        document.getElementById('qa-detail-back').onclick = () => {
            this.savePageState('qa-list');
            document.getElementById('qa-detail-section').style.display = 'none';
            document.getElementById('qa-section').style.display = '';
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
            alert('登入成功！');
            
            // 重新載入資料而不是重新整理頁面
            this.loadInitialData();
            
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
            alert('密碼確認不匹配');
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
            
            this.hideModal('questionModal');
            alert('問題發布成功！');
            
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

    // 切換貼文內容顯示
    togglePostContent(postId) {
        const post = this.currentPosts.find(p => p.id === parseInt(postId));
        if (!post) return;

        const contentDiv = document.getElementById(`post-content-${postId}`);
        const toggleBtn = document.getElementById(`toggle-btn-${postId}`);
        
        if (contentDiv.innerHTML.includes('...')) {
            // 顯示完整內容
            contentDiv.innerHTML = `<p>${post.content}</p>`;
            toggleBtn.textContent = '收起';
        } else {
            // 顯示截斷內容
            contentDiv.innerHTML = `<p>${post.content.substring(0, 100)}${post.content.length > 100 ? '...' : ''}</p>`;
            toggleBtn.textContent = '閱讀更多';
        }
    }

    // 處理登出
    handleLogout() {
        AuthManager.logout();
        this.updateAuthUI();
        alert('已登出');
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
        if (!savedState) return;
        
        try {
            const state = JSON.parse(savedState);
            const now = Date.now();
            const oneHour = 60 * 60 * 1000; // 1小時
            
            // 如果狀態太舊，清除它
            if (now - state.timestamp > oneHour) {
                localStorage.removeItem('blogPageState');
                return;
            }
            
            if (state.page === 'qa-detail' && state.data.questionId) {
                // 恢復到 Q&A 詳細頁面
                document.getElementById('posts-section').style.display = 'none';
                document.getElementById('qa-section').style.display = 'none';
                document.getElementById('qa-detail-section').style.display = '';
                document.getElementById('nav-qa').classList.add('active');
                document.getElementById('nav-posts').classList.remove('active');
                await this.showQADetail(state.data.questionId);
            } else if (state.page === 'qa-list') {
                // 恢復到 Q&A 列表
                document.getElementById('posts-section').style.display = 'none';
                document.getElementById('qa-section').style.display = '';
                document.getElementById('qa-detail-section').style.display = 'none';
                document.getElementById('nav-qa').classList.add('active');
                document.getElementById('nav-posts').classList.remove('active');
            }
        } catch (error) {
            console.error('恢復頁面狀態失敗:', error);
            localStorage.removeItem('blogPageState');
        }
    }
}

// 初始化應用
const app = new BlogApp();
document.addEventListener('DOMContentLoaded', () => app.init()); 