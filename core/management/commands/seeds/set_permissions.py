from dataclasses import dataclass


@dataclass
class PermissionField:
    code: str
    name: str
    function_zh: str
    is_active: bool
    action: str
    resource: str
    category: str
    api_url: str
    method: str


def set_permissions():
    return [
        # RBAC
        PermissionField(
            code="list-permissions",
            name="List Permissions",
            function_zh="取得權限列表",
            is_active=True,
            action="list",
            resource="permissions",
            category="rbac",
            api_url=r"/api/v1/rbac/permissions/",
            method="GET",
        ),
        PermissionField(
            code="create-permission",
            name="Create Permission",
            function_zh="建立權限",
            is_active=True,
            action="create",
            resource="permissions",
            category="rbac",
            api_url=r"/api/v1/rbac/permissions/",
            method="POST",
        ),
        PermissionField(
            code="get-permission",
            name="Get Permission Detail",
            function_zh="取得權限詳細資訊",
            is_active=True,
            action="get",
            resource="permissions",
            category="rbac",
            api_url=r"/api/v1/rbac/permissions/\\d+/",
            method="GET",
        ),
        PermissionField(
            code="update-permission",
            name="Update Permission",
            function_zh="更新權限",
            is_active=True,
            action="update",
            resource="permissions",
            category="rbac",
            api_url=r"/api/v1/rbac/permissions/\\d+/",
            method="PATCH",
        ),
        PermissionField(
            code="delete-permission",
            name="Delete Permission",
            function_zh="刪除權限",
            is_active=True,
            action="delete",
            resource="permissions",
            category="rbac",
            api_url=r"/api/v1/rbac/permissions/\\d+/",
            method="DELETE",
        ),
        PermissionField(
            code="batch-update-permissions",
            name="Batch Update Permissions",
            function_zh="批次更新權限",
            is_active=True,
            action="batch-update",
            resource="permissions",
            category="rbac",
            api_url=r"/api/v1/rbac/permissions/batch-update/",
            method="PATCH",
        ),
        PermissionField(
            code="list-roles",
            name="List Roles",
            function_zh="取得角色列表",
            is_active=True,
            action="list",
            resource="roles",
            category="rbac",
            api_url=r"/api/v1/rbac/roles/",
            method="GET",
        ),
        PermissionField(
            code="create-role",
            name="Create Role",
            function_zh="建立角色",
            is_active=True,
            action="create",
            resource="roles",
            category="rbac",
            api_url=r"/api/v1/rbac/roles/",
            method="POST",
        ),
        PermissionField(
            code="get-role",
            name="Get Role Detail",
            function_zh="取得角色詳細資訊",
            is_active=True,
            action="get",
            resource="roles",
            category="rbac",
            api_url=r"/api/v1/rbac/roles/\\d+/",
            method="GET",
        ),
        PermissionField(
            code="update-role",
            name="Update Role",
            function_zh="更新角色",
            is_active=True,
            action="update",
            resource="roles",
            category="rbac",
            api_url=r"/api/v1/rbac/roles/\\d+/",
            method="PUT",
        ),
        PermissionField(
            code="delete-role",
            name="Delete Role",
            function_zh="刪除角色",
            is_active=True,
            action="delete",
            resource="roles",
            category="rbac",
            api_url=r"/api/v1/rbac/roles/\\d+/",
            method="DELETE",
        ),
        PermissionField(
            code="list-role-users",
            name="List Role Users",
            function_zh="取得角色使用者列表",
            is_active=True,
            action="id-list",
            resource="role-users",
            category="rbac",
            api_url=r"/api/v1/rbac/roles/\\d+/users/",
            method="GET",
        ),
        PermissionField(
            code="update-role-user",
            name="Update Role User",
            function_zh="更新角色使用者",
            is_active=True,
            action="update",
            resource="role-users",
            category="rbac",
            api_url=r"/api/v1/rbac/roles/\\d+/users/",
            method="PUT",
        ),
        PermissionField(
            code="list-all-role-users",
            name="List All Role Users",
            function_zh="取得所有角色使用者列表",
            is_active=True,
            action="list",
            resource="role-users",
            category="rbac",
            api_url=r"/api/v1/rbac/roles/users/",
            method="GET",
        ),
        # Posts
        PermissionField(
            code="post.create",
            name="Create Post",
            function_zh="建立貼文",
            is_active=True,
            action="create",
            resource="posts",
            category="posts",
            api_url=r"/api/v1/posts/",
            method="POST",
        ),
        PermissionField(
            code="post.list",
            name="List Posts",
            function_zh="取得貼文列表",
            is_active=True,
            action="list",
            resource="posts",
            category="posts",
            api_url=r"/api/v1/posts/",
            method="GET",
        ),
        PermissionField(
            code="post.get",
            name="Get Post",
            function_zh="取得貼文",
            is_active=True,
            action="get",
            resource="posts",
            category="posts",
            api_url=r"/api/v1/posts/\\d+/",
            method="GET",
        ),
        PermissionField(
            code="post.update",
            name="Update Post",
            function_zh="編輯貼文",
            is_active=True,
            action="update",
            resource="posts",
            category="posts",
            api_url=r"/api/v1/posts/\\d+/",
            method="PUT",
        ),
        PermissionField(
            code="post.patch",
            name="Patch Post",
            function_zh="部分更新貼文",
            is_active=True,
            action="update",
            resource="posts",
            category="posts",
            api_url=r"/api/v1/posts/\\d+/",
            method="PATCH",
        ),
        PermissionField(
            code="post.delete",
            name="Delete Post",
            function_zh="刪除貼文",
            is_active=True,
            action="delete",
            resource="posts",
            category="posts",
            api_url=r"/api/v1/posts/\\d+/",
            method="DELETE",
        ),
        # Questions
        PermissionField(
            code="question.create",
            name="Create Question",
            function_zh="建立問題",
            is_active=True,
            action="create",
            resource="questions",
            category="questions",
            api_url=r"/api/v1/questions/",
            method="POST",
        ),
        PermissionField(
            code="question.list",
            name="List Questions",
            function_zh="取得問題列表",
            is_active=True,
            action="list",
            resource="questions",
            category="questions",
            api_url=r"/api/v1/questions/",
            method="GET",
        ),
        PermissionField(
            code="question.get",
            name="Get Question",
            function_zh="取得問題",
            is_active=True,
            action="get",
            resource="questions",
            category="questions",
            api_url=r"/api/v1/questions/\\d+/",
            method="GET",
        ),
        PermissionField(
            code="question.update",
            name="Update Question",
            function_zh="編輯問題",
            is_active=True,
            action="update",
            resource="questions",
            category="questions",
            api_url=r"/api/v1/questions/\\d+/",
            method="PUT",
        ),
        PermissionField(
            code="question.patch",
            name="Patch Question",
            function_zh="部分更新問題",
            is_active=True,
            action="update",
            resource="questions",
            category="questions",
            api_url=r"/api/v1/questions/\\d+/",
            method="PATCH",
        ),
        PermissionField(
            code="question.delete",
            name="Delete Question",
            function_zh="刪除問題",
            is_active=True,
            action="delete",
            resource="questions",
            category="questions",
            api_url=r"/api/v1/questions/\\d+/",
            method="DELETE",
        ),
        PermissionField(
            code="question.like",
            name="Like Question",
            function_zh="按讚/取消按讚問題",
            is_active=True,
            action="like",
            resource="questions",
            category="questions",
            api_url=r"/api/v1/questions/\\d+/like/",
            method="POST",
        ),
        PermissionField(
            code="question.view",
            name="View Question",
            function_zh="更新問題瀏覽次數",
            is_active=True,
            action="view",
            resource="questions",
            category="questions",
            api_url=r"/api/v1/questions/\\d+/view/",
            method="POST",
        ),
        # Answers
        PermissionField(
            code="answer.create",
            name="Create Answer",
            function_zh="建立回答",
            is_active=True,
            action="create",
            resource="answers",
            category="answers",
            api_url=r"/api/v1/answers/",
            method="POST",
        ),
        PermissionField(
            code="answer.get",
            name="Get Answer",
            function_zh="取得回答",
            is_active=True,
            action="get",
            resource="answers",
            category="answers",
            api_url=r"/api/v1/answers/\\d+/",
            method="GET",
        ),
        PermissionField(
            code="answer.update",
            name="Update Answer",
            function_zh="編輯回答",
            is_active=True,
            action="update",
            resource="answers",
            category="answers",
            api_url=r"/api/v1/answers/\\d+/",
            method="PUT",
        ),
        PermissionField(
            code="answer.patch",
            name="Patch Answer",
            function_zh="部分更新回答",
            is_active=True,
            action="update",
            resource="answers",
            category="answers",
            api_url=r"/api/v1/answers/\\d+/",
            method="PATCH",
        ),
        PermissionField(
            code="answer.delete",
            name="Delete Answer",
            function_zh="刪除回答",
            is_active=True,
            action="delete",
            resource="answers",
            category="answers",
            api_url=r"/api/v1/answers/\\d+/",
            method="DELETE",
        ),
        PermissionField(
            code="answer.like",
            name="Like Answer",
            function_zh="按讚/取消按讚回答",
            is_active=True,
            action="like",
            resource="answers",
            category="answers",
            api_url=r"/api/v1/answers/\\d+/like/",
            method="POST",
        ),
        # Users
        PermissionField(
            code="user.register",
            name="Register User",
            function_zh="註冊新用戶",
            is_active=True,
            action="create",
            resource="users",
            category="users",
            api_url=r"/api/v1/users/register/",
            method="POST",
        ),
        PermissionField(
            code="user.login",
            name="User Login",
            function_zh="使用者登入",
            is_active=True,
            action="create",
            resource="users",
            category="users",
            api_url=r"/api/v1/users/login/",
            method="POST",
        ),
        PermissionField(
            code="user.logout",
            name="User Logout",
            function_zh="使用者登出",
            is_active=True,
            action="delete",
            resource="users",
            category="users",
            api_url=r"/api/v1/users/logout/",
            method="POST",
        ),
        PermissionField(
            code="user.change_password",
            name="Change Password",
            function_zh="變更密碼",
            is_active=True,
            action="update",
            resource="users",
            category="users",
            api_url=r"/api/v1/users/change-password/",
            method="POST",
        ),
        PermissionField(
            code="user.forgot_password",
            name="Forgot Password",
            function_zh="忘記密碼發送驗證碼",
            is_active=True,
            action="create",
            resource="users",
            category="users",
            api_url=r"/api/v1/users/forgot-password/",
            method="POST",
        ),
        PermissionField(
            code="user.reset_password",
            name="Reset Password",
            function_zh="重置密碼",
            is_active=True,
            action="update",
            resource="users",
            category="users",
            api_url=r"/api/v1/users/reset-password/",
            method="POST",
        ),
        PermissionField(
            code="user.refresh_token",
            name="Refresh Token",
            function_zh="刷新Token",
            is_active=True,
            action="create",
            resource="users",
            category="users",
            api_url=r"/api/v1/users/refresh/",
            method="POST",
        ),
    ]
