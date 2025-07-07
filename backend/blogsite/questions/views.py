import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from accounts.utils import login_check
from questions.models import Question, Answer

@csrf_exempt
def questions_handler(request):
    if request.method == "GET":
        return get_questions(request)
    elif request.method == "POST":
        return create_question(request)
    else:
        return JsonResponse({"message": "Method not allowed"}, status=405)

@csrf_exempt
def answers_handler(request, question_id):
    if request.method == "GET":
        return get_answers(request, question_id)
    elif request.method == "POST":
        return create_answer(request, question_id)
    else:
        return JsonResponse({"message": "Method not allowed"}, status=405)
    

@csrf_exempt
@require_http_methods(["GET"])
def get_questions(request):
    questions = Question.objects.all().order_by('-created_at')
    data = []
    for q in questions:
        data.append({
            "id": q.id,
            "title": q.title,
            "content": q.content,
            "created_at": q.created_at.strftime("%Y-%m-%d %H:%M"),
            "author": q.author.username if q.author else "匿名",
            "views": q.views,
            "likes": q.likes,
            "answer_count": q.answer_count,
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
@login_check
@require_http_methods(["POST"])
def create_question(request):
    data = json.loads(request.body)
    title = data.get("title")
    content = data.get("content")
    q = Question.objects.create(
        title=title,
        content=content,
        author=request.account
    )
    return JsonResponse({
        "id": q.id,
        "title": q.title,
        "content": q.content,
        "created_at": q.created_at.strftime("%Y-%m-%d %H:%M"),
        "author": q.author.username,
        "views": q.views,
        "likes": q.likes,
        "answer_count": q.answer_count,
    })

@csrf_exempt
@require_http_methods(["GET"])
def get_question_detail(request, question_id):
    try:
        q = Question.objects.get(id=question_id)
        # 自動增加瀏覽數
        q.views += 1
        q.save()
    except Question.DoesNotExist:
        return JsonResponse({"message": "Question not found"}, status=404)
    answers = Answer.objects.filter(question=q).order_by('created_at')
    answers_data = [
        {
            "id": a.id,
            "content": a.content,
            "created_at": a.created_at.strftime("%Y-%m-%d %H:%M"),
            "author": a.author.username if a.author else "匿名",
            "likes": a.likes,
        }
        for a in answers
    ]
    data = {
        "id": q.id,
        "title": q.title,
        "content": q.content,
        "created_at": q.created_at.strftime("%Y-%m-%d %H:%M"),
        "author": q.author.username if q.author else "匿名",
        "views": q.views,
        "likes": q.likes,
        "answer_count": q.answer_count,
        "answers": answers_data,
    }
    return JsonResponse(data)

@csrf_exempt
@require_http_methods(["GET"])
def get_answers(request, question_id):
    try:
        q = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return JsonResponse({"message": "Question not found"}, status=404)
    answers = Answer.objects.filter(question=q).order_by('created_at')
    answers_data = [
        {
            "id": a.id,
            "content": a.content,
            "created_at": a.created_at.strftime("%Y-%m-%d %H:%M"),
            "author": a.author.username if a.author else "匿名",
            "likes": a.likes,
        }
        for a in answers
    ]
    return JsonResponse(answers_data, safe=False)

@csrf_exempt
@login_check
@require_http_methods(["POST"])
def create_answer(request, question_id):
    try:
        q = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return JsonResponse({"message": "Question not found"}, status=404)
    
    try:
        data = json.loads(request.body)
        content = data.get("content")
    
        a = Answer.objects.create(
            content=content,
            author=request.account,
            question=q
        )
        print(f"回答創建成功: {a.id}")
        
        # 更新回答數
        q.answer_count = Answer.objects.filter(question=q).count()
        q.save()
        
        response_data = {
            "id": a.id,
            "content": a.content,
            "created_at": a.created_at.strftime("%Y-%m-%d %H:%M"),
            "author": a.author.username,
            "likes": a.likes,
        }
        return JsonResponse(response_data)
    except json.JSONDecodeError as e:
        print(f"JSON 解析錯誤: {e}")
        return JsonResponse({"message": "Invalid JSON"}, status=400)
    except Exception as e:
        print(f"創建回答時發生錯誤: {e}")
        return JsonResponse({"message": f"創建回答失敗: {str(e)}"}, status=500)

@csrf_exempt
@login_check
@require_http_methods(["POST"])
def like_question(request, question_id):
    try:
        q = Question.objects.get(id=question_id)
        q.likes += 1
        q.save()
        return JsonResponse({
            "likes": q.likes,
            "message": "按讚成功"
        })
    except Question.DoesNotExist:
        return JsonResponse({"message": "Question not found"}, status=404)
    except Exception as e:
        return JsonResponse({"message": f"按讚失敗: {str(e)}"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def view_question(request, question_id):
    try:
        q = Question.objects.get(id=question_id)
        q.views += 1
        q.save()
        return JsonResponse({
            "views": q.views,
            "message": "瀏覽記錄成功"
        })
    except Question.DoesNotExist:
        return JsonResponse({"message": "Question not found"}, status=404)
    except Exception as e:
        return JsonResponse({"message": f"瀏覽記錄失敗: {str(e)}"}, status=500)

@csrf_exempt
@login_check
@require_http_methods(["POST"])
def like_answer(request, answer_id):
    try:
        a = Answer.objects.get(id=answer_id)
        a.likes += 1
        a.save()
        return JsonResponse({
            "likes": a.likes,
            "message": "按讚成功"
        })
    except Answer.DoesNotExist:
        return JsonResponse({"message": "Answer not found"}, status=404)
    except Exception as e:
        return JsonResponse({"message": f"按讚失敗: {str(e)}"}, status=500)
