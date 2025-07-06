import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from django.http import JsonResponse

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
@login_check
@require_http_methods(["GET"])
def get_posts(request):
    posts = Post.objects.all()
    posts_data = [{
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'author': post.author.username,
            'created_at': post.created_at.strftime('%Y-%m-%d %H:%M') if post.created_at else None
        } for post in posts]
    return JsonResponse({'posts': posts_data})