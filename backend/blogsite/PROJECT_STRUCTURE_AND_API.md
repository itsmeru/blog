# 部落格與問答平台 - 技術架構與實作展示

## 📋 專案概述

這是一個採用 **Django REST Framework** 開發的現代化部落格與問答平台，具備完整的 JWT 認證、RESTful API 設計、自動化 API 文件，以及前後端分離架構。專案強調**安全性**、**可擴充性**與**易維護性**，適合正式環境部署與團隊協作。


---

## 🏗️ 技術架構

### 後端技術棧
- **Simple JWT 5.5.0** 認證（access token + refresh token）
- **drf-spectacular 0.28.0** 自動化 API 文件
- **SQLite** 資料庫（開發環境）
- **Argon2** 密碼雜湊

### 前端技術棧
- **原生 JavaScript** + **HTML5** + **CSS3**
- **Fetch API** 進行 HTTP 請求

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
│   ├── questions/         # 問題系統
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
- **Argon2 雜湊**：使用現代密碼雜湊演算法，安全性優於 bcrypt
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

### 1. 用戶管理 (accounts)
- **註冊/登入**：支援 email 或 username 登入
- **密碼重設**：email 驗證碼機制
- **個人資料**：用戶名修改、密碼更改
- **統計資訊**：用戶發文、提問、回覆數量

### 2. 部落格文章 (posts)
- **CRUD 操作**：建立、讀取、更新、刪除文章
- **圖片上傳**：base64 編碼存於資料庫
- **標籤系統**：支援多標籤篩選
- **搜尋功能**：標題與內容關鍵字搜尋
- **分頁顯示**：支援自訂每頁數量

### 3. 問答系統 (questions)
- **問題管理**：建立、瀏覽、更新、刪除問題
- **瀏覽統計**：自動記錄瀏覽次數
- **點讚功能**：用戶可對問題點讚
- **排序功能**：最新/熱門排序
- **標籤系統**：問題分類與篩選

### 4. 回答系統 (answers)
- **回答管理**：建立、瀏覽、更新、刪除回答
- **點讚功能**：用戶可對回答點讚
- **關聯顯示**：回答與問題關聯顯示

---

## 📖 API 文件與測試

### Swagger/OpenAPI 自動化
- **即時更新**：所有 API 變更自動反映在文件中
- **互動測試**：可直接在瀏覽器中測試 API
- **參數說明**：所有查詢參數、請求體、回應格式都有詳細說明
- **權限標註**：清楚標示每個端點的權限要求

### 文件特色
- **多語言支援**：API 文件使用英文，錯誤訊息使用中文
- **完整覆蓋**：包含所有自訂查詢參數與分頁邏輯
- **開發友善**：降低前後端溝通成本

**🎯 面試展示重點**：可現場展示 `/api/docs/` 頁面，展示完整的 API 文件與互動測試功能。

---

## 🎯 技術亮點

### 1. 現代化架構
- **模組化設計**：每個功能獨立成 app，職責分明
- **ViewSet + Router**：自動生成 RESTful 路由
- **序列化器**：統一資料驗證與轉換
- **自訂用戶模型**：擴展 Django 內建功能

### 2. 安全性
- **JWT 認證**：無狀態、安全、可擴展
- **HttpOnly Cookie**：防止 XSS 攻擊
- **Argon2 雜湊**：現代密碼安全標準
- **權限控制**：細緻的存取控制

### 3. 可維護性
- **DRF 最佳實踐**：遵循框架設計原則
- **自動化文件**：減少手動維護成本
- **統一錯誤處理**：一致的 API 回應格式
- **程式碼組織**：清晰的模組化結構

### 4. 用戶體驗
- **響應式設計**：支援多裝置瀏覽
- **即時互動**：點讚、搜尋、篩選功能
- **分頁優化**：大量資料分頁顯示
- **錯誤處理**：友善的錯誤訊息

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
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### 生產環境建議
- **資料庫**：PostgreSQL 或 MySQL
- **Web 伺服器**：Nginx + Gunicorn
- **靜態檔案**：CDN 或雲端儲存
- **監控**：Django Debug Toolbar（開發）、Sentry（生產）

---

## 📈 效能優化

### 資料庫優化
- **索引**：關鍵欄位建立適當索引
- **查詢優化**：使用 `select_related` 與 `prefetch_related`
- **分頁**：避免大量資料載入

### API 優化
- **快取**：適當使用 HTTP 快取標頭
- **壓縮**：啟用 Gzip 壓縮
- **CDN**：靜態資源使用 CDN

### 前端優化
- **懶載入**：分頁載入減少初始載入時間
- **本地快取**：減少重複 API 請求
- **錯誤處理**：優雅的錯誤提示

---

## 🎯 面試重點

### 架構設計能力
- **前後端分離**：清晰的 API 合約設計
- **模組化設計**：易於維護與擴展的程式碼組織
- **RESTful API**：符合標準設計原則的 API 設計

### 技術深度
- **JWT 認證**：理解 token 機制與安全性考量
- **DRF 最佳實踐**：ViewSet、序列化器、權限控制
- **自動化文件**：Swagger/OpenAPI 整合與維護

### 實作能力
- **完整功能**：從認證到內容管理的完整業務流程
- **錯誤處理**：統一的錯誤回應格式與用戶體驗
- **安全性**：權限控制、資料驗證、密碼安全

### 可展示功能
- **API 文件**：現場展示 `/api/docs/` 完整功能
- **前端互動**：展示完整的用戶操作流程
- **資料庫設計**：展示模型關係與查詢優化

---

## 🔮 未來擴展方向

### 技術升級
- **快取系統**：Redis 用於 session 與快取
- **搜尋引擎**：Elasticsearch 或 PostgreSQL 全文搜尋
- **檔案上傳**：AWS S3 或雲端儲存
- **非同步處理**：Celery + Redis 處理背景任務

### 功能擴展
- **通知系統**：即時通知與郵件通知
- **評論系統**：多層級評論功能
- **用戶權限**：角色基礎權限控制
- **內容審核**：自動化內容審核機制

---

*本專案展示了一個現代化、可擴展的 Django REST Framework 後端架構，具備完整的認證系統、RESTful API 設計、自動化文件，以及前後端分離的整合方案。專案強調實用性、安全性與可維護性，適合作為全端開發能力的展示作品。* 