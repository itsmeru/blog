import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q

from accounts.utils import login_check
from posts.models import Post


@csrf_exempt
@login_check
@require_http_methods(["POST"])
def create_post(request):
    data = json.loads(request.body)
    title = data.get('title')
    content = data.get('content')
    author = request.account
    Post.objects.create(
        title=title,
        content=content,
        author=author
    )
    return JsonResponse({'message': 'Post created successfully'})


@csrf_exempt
@require_http_methods(["GET"])
def get_posts(request):
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 1)
    keyword = request.GET.get('keyword', '')
    order_by = request.GET.get('order', 'desc')
    order_by = '-created_at' if order_by == 'desc' else 'created_at'
    posts = Post.objects.all()

    if keyword:
        posts = posts.filter(Q(title__icontains=keyword) | Q(content__icontains=keyword))

    posts = posts.order_by(order_by)
    paginator = Paginator(posts, page_size)

    posts_page = paginator.get_page(page)

    posts_data = [{
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'author': post.author.username,
            'created_at': post.created_at.strftime('%Y-%m-%d %H:%M') if post.created_at else None
        } for post in posts_page]
    return JsonResponse({
        'posts': posts_data,
        'total': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': posts_page.number,
    })