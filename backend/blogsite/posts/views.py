import json
import base64

from accounts.utils import login_check
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from posts.models import Post


@csrf_exempt
def posts_handler(request):
    if request.method == "POST":
        return create_post(request)
    elif request.method == "GET":
        return get_posts(request)
    else:
        return JsonResponse({"message": "Method not allowed"}, status=405)


@csrf_exempt
@login_check
@require_http_methods(["POST"])
def create_post(request):
    try:
        # 處理表單資料
        title = request.POST.get("title")
        content = request.POST.get("content")
        tags = request.POST.get("tags", "")
        image_file = request.FILES.get("image")
        author = request.account
        
        # 處理圖片
        image_data = None
        image_type = None
        if image_file:
            image_data = image_file.read()
            image_type = image_file.content_type
            print("圖片類型:", image_type)
            print("圖片大小:", len(image_data), "bytes")
        
        # 創建貼文
        post = Post.objects.create(
            title=title,
            content=content,
            tags=tags,
            image=image_data,
            image_type=image_type,
            author=author
        )
        
        return JsonResponse({
            "message": "Post created successfully",
            "post_id": post.id
        })
    except Exception as e:
        return JsonResponse({"message": f"Error creating post: {str(e)}"}, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def get_posts(request):
    page = request.GET.get("page", 1)
    size = request.GET.get("size", 3)
    keyword = request.GET.get("keyword", "")
    order_by = request.GET.get("order", "desc")
    order_by = "-created_at" if order_by == "desc" else "created_at"

    posts_page = Post.get_posts(page, size, keyword, order_by)

    posts_data = []
    for post in posts_page:
        image_data = None
        if post.image and isinstance(post.image, bytes):
            try:
                image_data = f"data:{post.image_type};base64,{base64.b64encode(post.image).decode('utf-8')}"
            except Exception as e:
                print(f"圖片編碼錯誤: {e}")
                image_data = None
        
        posts_data.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "tags": post.tags,
            "image": image_data,
            "author": post.author.username,
            "created_at": (
                post.created_at.strftime("%Y-%m-%d %H:%M") if post.created_at else None
            ),
        })
    
    # 從 posts_page 取得分頁資訊
    return JsonResponse(
        {
            "posts": posts_data,
            "total": posts_page.paginator.count,
            "num_pages": posts_page.paginator.num_pages,
            "current_page": posts_page.number,
        }
    )


@csrf_exempt
@require_http_methods(["GET"])
def get_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        image_data = None
        if post.image and isinstance(post.image, bytes):
            try:
                image_data = f"data:{post.image_type};base64,{base64.b64encode(post.image).decode('utf-8')}"
            except Exception as e:
                print(f"圖片編碼錯誤: {e}")
                image_data = None
        
        post_data = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "tags": post.tags,
            "image": image_data,
            "author": post.author.username,
            "created_at": (
                post.created_at.strftime("%Y-%m-%d %H:%M") if post.created_at else None
            ),
        }
        return JsonResponse(post_data)
    except Post.DoesNotExist:
        return JsonResponse({"message": "Post not found"}, status=404)
