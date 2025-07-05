from django.shortcuts import render
from django.contrib import messages

from .models import User


# Create your views here.
def register(request):
    if request.method == 'POST':
        account = request.POST['account']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        birth_date = request.POST['birth_date']

        if not all([account, username, email, password, birth_date]):
            messages.error(request, '請填寫完整資料')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '帳號已存在')
            return render(request, 'accounts/register.html')
        
    return render(request, 'accounts/register.html')

def login(request):
    return render(request, 'accounts/login.html')