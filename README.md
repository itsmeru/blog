# 部落格與問答平台 - 技術架構與實作展示

## 📋 專案概述

這是一個採用 **Django REST Framework** 開發的現代化部落格與問答平台，具備完整的 JWT 認證、RESTful API 設計、自動化 API 文件，以及前後端分離架構。

---

## 🏗️ 技術架構

### 後端技術棧
- **Django 5.2.4** + **Django REST Framework 3.16.0**
- **Simple JWT 5.5.0**
- **drf-spectacular 0.28.0** 自動化 API 文件
- **SQLite** 資料庫（開發環境）

### 前端技術棧
- **原生 JavaScript** + **HTML5** + **CSS3**
- **Fetch API** 進行 HTTP 請求
- **單頁應用 (SPA)** 架構

---

## 📁 專案結構

```
backend/
├── blogsite/
│   ├── accounts/          # 用戶認證與管理
│   │   ├── models.py      
│   │   ├── serializers.py 
│   │   ├── views.py       # 登入/註冊/密碼重設
│   │   └── urls.py        
│   ├── posts/             # 部落格文章管理
│   │   ├── models.py      
│   │   ├── serializers.py 
│   │   ├── views.py       # 文章 CRUD
│   │   └── urls.py        
│   ├── questions/         # 問答系統
│   │   ├── models.py      
│   │   ├── serializers.py 
│   │   ├── views.py       # 問題 CRUD
│   │   └── urls.py        
│   ├── answers/           # 回答系統
│   │   ├── models.py      
│   │   ├── serializers.py 
│   │   ├── views.py       # 回答 CRUD
│   │   └── urls.py        
│   └── blogsite/          # 專案核心設定
│       ├── settings.py    # 專案設定
│       ├── urls.py        # 主路由
│       └── wsgi.py        
└── requirements.txt        # 依賴套件

```

---

## 🔐 安全與認證

### JWT 認證機制
- **Access Token**：短期有效（30分鐘），用於 API 請求
- **Refresh Token**：長期有效（7天），存於 HttpOnly cookie，防止 XSS 攻擊
- **自訂登入**：支援 email 或 username 登入
- **安全登出**：清除 refresh token cookie
- **Token 黑名單**：支援登出後 token 失效

### 密碼安全
- **Argon2 雜湊**：使用現代密碼雜湊演算法
- **密碼重設**：採用驗證碼機制，email 驗證，15分鐘有效，單次使用

### 權限控制
- **細緻權限**：只有作者能刪除/修改自己的內容
- **公開存取**：未登入者僅能瀏覽公開資料
- **動態權限**：使用 `get_permissions()` 針對不同 action 分配權限

---

## 🌐 API 設計

### RESTful 設計原則
- **標準 HTTP 方法**：GET、POST、PUT、DELETE
- **統一資源命名**：`/api/posts/`、`/api/questions/`、`/api/answers/`


### 分頁與查詢
- **標準分頁**：使用 DRF `PageNumberPagination`
- **查詢參數**：
  - `page`：頁碼
  - `size`：每頁數量
  - `keyword`：關鍵字搜尋（標題/內容模糊搜尋）
  - `tags`：標籤篩選（貼文，逗號分隔）
  - `sort`：排序（hot/latest，問答）

---

## 📚 核心功能模組

### 1. 用戶認證系統 (accounts)
- **雙重登入支援**：用戶可以用 email 或 username 登入，提供靈活性
- **JWT 雙 token 機制**：access token 存於記憶體，refresh token 存於 HttpOnly cookie，防止 XSS 攻擊
- **密碼安全**：使用 Argon2 雜湊演算法
- **密碼重設流程**：email 驗證碼機制，15分鐘有效，單次使用
- **個人資料管理**：用戶可以修改用戶名、密碼，查看個人統計
- **自動 token 刷新**：無縫的用戶體驗，無感知的認證維護

### 2. 部落格文章系統 (posts)
- **完整 CRUD 操作**：建立、讀取、更新、刪除文章，權限控制
- **圖片上傳功能**：支援 base64 編碼，存於資料庫
- **標籤系統**：支援多標籤篩選，用逗號分隔
- **智能搜尋**：標題和內容的模糊搜尋，支援關鍵字匹配
- **分頁優化**：支援自訂每頁數量，提升大量資料的載入效能
- **權限控制**：只有作者能刪除/修改自己的文章，確保資料安全

### 3. 問答系統 (questions)
- **問題管理**：完整的問題 CRUD 功能，支援標籤分類
- **瀏覽統計**：自動記錄瀏覽次數，支援熱門排序演算法
- **點讚功能**：用戶可以對問題點讚，增加社群互動性
- **智能排序**：支援最新/熱門排序，提升用戶體驗
- **權限管理**：作者專屬的內容管理權限

### 4. 回答系統 (answers)
- **回答管理**：建立、瀏覽、更新、刪除回答，完整的內容管理
- **點讚功能**：用戶可以對回答點讚，促進社群互動
- **權限控制**：只有作者能管理自己的回答
- **即時更新**：點讚狀態即時反映，提升用戶體驗

---

## 🚀 部署與開發

### 開發環境
```bash
# 安裝依賴
pip install -r requirements.txt

# 資料庫遷移
python manage.py migrate

# 啟動開發伺服器
python manage.py runserver

# 訪問 API 文件
http://localhost:8000/api/docs/
```

### 環境變數設定
```bash
# .env 檔案
SECRET_KEY=your-secret-key
EMAIL_HOST_USER=your-email@gmail.com
```
