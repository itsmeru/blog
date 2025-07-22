# Blog & Q&A Platform

一個基於 Django REST Framework 的部落格與問答平台，採用明確分層的 MVC 架構設計。

## 專案架構

本專案採用**明確分層的 MVC 架構**，並設有 `core` 共用層，方便大型專案維護、擴充與團隊協作。

### 目錄結構

```
django_proto/
├── core/                        # 專案主程式（主設定、主路由、主進入點、管理指令等）
│   ├── app/                     # 業務邏輯、API、基礎服務、middleware
│   │   ├── api/                 # API 相關（exception, response, 測試等）
│   │   ├── base/                # 共用 repository/service/view 基底類別與測試
│   │   ├── config/              # 設定管理（如 config loader、環境變數、常數等）
│   │   └── middleware/          # middleware 與相關測試
│   ├── asgi.py                  # ASGI 進入點
│   ├── management/              # 自訂 Django 管理指令
│   ├── settings.py              # Django 設定
│   ├── urls.py                  # 主 URL 路由
│   └── wsgi.py                  # WSGI 進入點
├── users/                       # 使用者相關（models、API、service、測試）
├── rbac/                        # 權限/角色管理 (Role-Based Access Control)
├── health/                      # 健康檢查 API
├── docs/                        # 專案說明、API 標準、測試規範等文件
├── manage.py                    # Django 管理指令入口
├── requirements.txt             # Python 套件需求
├── .env.example                 # 環境變數範例
├── README.md                    # 專案說明文件
├── TASKS.md                     # 開發任務追蹤
├── LICENSE                      # 授權條款
├── pyproject.toml               # Python 專案設定
├── uv.lock                      # uv 套件鎖定檔

```
---

## 架構圖與流程說明

```
1. 前端/用戶端 (Client)
   ↓
2. blogsite/urls.py (Django 主路由)
   ↓
3. api/<app>/urls.py (各 app 路由)
   ↓
4. api/<app>/views.py (View/Controller)
   ↓
5. api/<app>/services.py (Service/業務邏輯)
   ↓
6. api/<app>/models.py, serializers.py (Model/資料層, Serializer/驗證)
   ↓
7. 資料庫 (DB)

# 請求/回應流程中，會經過 core 層的：
- core/lifecycle.py：
    - middleware（全域請求/回應鉤子，處理 log、驗證、權限、exception 統一格式化等）
    - decorator（單一 view 的請求/回應鉤子）
    - signal（如 post_save, post_delete）
    - exception handler（全域錯誤攔截與格式化）
- core/exceptions.py：
    - 自訂 exception class
    - 全域 exception handler（如 DRF 的 EXCEPTION_HANDLER 設定）
- core/permissions.py, response.py, validators.py, logging.py：
    - 於 view/service/middleware 中隨時可 import 使用
```

---

## 各層職責說明

### core/（共用邏輯層）

- **permissions.py**：自訂權限 class，所有 app 可共用（如 RBAC、IsOwnerOrReadOnly 等）
- **response.py**：統一 API 回應格式（如 success_response, error_response）
- **validators.py**：共用資料驗證工具（如 email、密碼、欄位格式等）
- **logging.py**：日誌記錄（log_info, log_error 等，支援寫檔、第三方監控）
- **lifecycle.py**：API 生命週期鉤子（如 decorator、middleware、signal，統一處理請求前後流程，並可整合全域 exception handler）
- **exceptions.py**：自訂 exception class 與全域 exception handler，確保所有錯誤都能被攔截並以統一格式回應

### api/（功能 app 層）

每個 app（如 posts、questions、answers、accounts）都包含：

- **models.py**：資料結構、ORM
- **serializers.py**：資料驗證與格式轉換
- **services.py**：業務邏輯（如建立、查詢、刪除、複雜流程）
- **views.py**：HTTP 請求/回應處理（Controller，調用 service）
- **urls.py**：路由分發

### blogsite/（Django 專案設定層）

- **settings.py**：全域設定（app 註冊、middleware、資料庫、JWT、CORS 等）
- **urls.py**：主路由，include 各 app 的 urls

## 生命週期與共用邏輯

- **middleware**：可在 core/lifecycle.py 統一管理（如全域權限、日誌、請求驗證、API 請求前後處理、exception 統一格式化）
- **lifecycle decorator**：可用於 view method，統一處理請求前後的自動化流程（如審計、格式化、通知）
- **exception handler**：可在 core/lifecycle.py 或 core/exceptions.py 統一管理，確保所有錯誤都能被攔截並以統一格式回應
- **log**：所有 app/service/view 可直接 import core/logging.py 使用
- **permission**：所有 app 可直接 import core/permissions.py 使用
- **response formatter**：所有 view 可直接 import core/response.py 使用

## 範例：如何在 app 中使用 core 層

```python
# api/posts/views.py
from core.response import success_response, error_response
from core.permissions import IsOwnerOrReadOnly
from core.logging import log_info
from .services import PostService

class PostCreateView(GenericAPIView):
    def post(self, request):
        # ...驗證資料...
        post = PostService.create_post(...)
        log_info(f'User {request.user} created post {post.id}')
        return success_response({'post_id': post.id}, message='貼文建立成功', status=201)
```

## 技術棧

### 後端技術棧
- **Django 5.2.4** - Web 框架
- **Django REST Framework 3.15.0** - API 框架
- **Simple JWT 5.5.0** - 認證
- **PostgreSQL** - 資料庫
- **Argon2** - 密碼雜湊
- **DRF-Spectacular** - API 文件

### 前端技術棧
- **HTML/CSS/JavaScript** - 前端技術
- **Live Server** - 開發伺服器

## 功能特色

### 帳號系統 (accounts)
- 用戶註冊/登入
- JWT 認證
- 密碼重設
- 個人資料管理
- RBAC 權限控制

### 貼文系統 (posts)
- 建立/編輯/刪除貼文
- 圖片上傳
- 標籤系統
- 搜尋功能

### 問答系統 (questions)
- 建立/編輯/刪除問題
- 問題分類
- 瀏覽次數統計
- 按讚功能

### 回答系統 (answers)
- 回答問題
- 回答按讚
- 回答排序

## 適用情境

- **中大型專案**：可維護性、可測試性、可擴充性高
- **多人協作**：分層明確，易於分工
- **需要共用邏輯**：如權限、日誌、驗證、API 格式統一

## 延伸設計

- 可在 core 增加 `exceptions.py`（自訂例外）、`tasks.py`（共用 Celery 任務）、`utils/`（共用小工具）
- 可在 api 各 app 增加 `repositories.py`（資料存取層，進一步分離 ORM 操作）

## 開發指南

### 環境設定
1. 建立虛擬環境
2. 安裝依賴：`pip install -r requirements.txt`
3. 執行遷移：`python manage.py migrate`
4. 啟動開發伺服器：`python manage.py runserver`

### API 文件
- Swagger UI：`http://localhost:8000/api/schema/swagger-ui/`
- ReDoc：`http://localhost:8000/api/schema/redoc/`

### 測試
```bash
python manage.py test
```

## 貢獻指南

1. Fork 專案
2. 建立功能分支
3. 提交變更
4. 發起 Pull Request

## 授權

MIT License
