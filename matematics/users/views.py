import time
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth
from .models import User
import json
from .forms import UserLoginForm, UserRegistrationForm, ProfileChangeForm
import secrets
from main.models import Task
from .tasks import send_email


def login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        form.is_valid()
        try:
            email = form.cleaned_data['email']
        except KeyError:
            return render(request, 'users/login.html')
        try:
            password = form.cleaned_data['password']
        except KeyError:
            return render(request, 'users/login.html')
        user = auth.authenticate(email=email, password=password)
        if user:
            auth.login(request, user)
            return redirect('main:topic_list')
        else:
            return render(request, 'users/login.html', {'form': form})
    else:
        if request.user.id:
            return redirect('main:topic_list')
        else:
            form = UserLoginForm()
            return render(request, 'users/login.html', {'form': form})

def verification(request, verification_token):
    if request.method == 'GET':
        user = get_object_or_404(User, verification_token=verification_token)
        user.email_proof = True
        user.save()
        return redirect('main:topic_list')
    else:
        return redirect('main:topic_list')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        form.is_valid()
        try:
            email = form.cleaned_data['email']
        except KeyError:
            return render(request, 'users/register.html',
                          {'form': form})
        try:
            password = form.cleaned_data['password']
        except KeyError:
            return render(request, 'users/register.html',
                          {'form': form})
        try:
            password_check = form.cleaned_data['password_check']
        except KeyError:
            return render(request, 'users/register.html',
                          {'form': form})    
        if password == password_check:
            verification_token = secrets.token_urlsafe(32)
            try:
                user = User.objects.create(email=email, password=password, verification_token=verification_token, teacher_flag=form.cleaned_data['teacher_flag'])
            except KeyError:
                user = User.objects.create(email=email, password=password, verification_token=verification_token)
            send_email.delay(user.email,
                             subject='Регистрация на Matematics',
                             message=f'Для подтверждения почты, пройдите по ссылке: 127.0.0.1:8000/users/verification/{verification_token}')
            auth.login(request, user)
            return redirect('main:topic_list')
        else:
            return render(request, 'users/register.html',
                          {'form': form})
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


def profile(request):
    if request.method == 'POST':
        form = ProfileChangeForm(request.POST, request.FILES)
        form.is_valid()
        user = get_object_or_404(User, id=request.user.id)
        try:
            user.first_name = form.cleaned_data['new_first_name']
        except KeyError:
            pass

        try:
            user.last_name = form.cleaned_data['new_last_name']
        except KeyError:
            pass

        try:
            user.avatar = request.FILES['avatar_photo']
        except KeyError:
            pass

        try:
            user.gender = form.cleaned_data['gender']
        except KeyError:
            pass

        try:
            if form.cleaned_data['new_password'] and form.cleaned_data['new_password_repeat']:
                if form.cleaned_data['new_password'] == form.cleaned_data['new_password_repeat']:
                    user.set_password(form.cleaned_data['new_password'])
                    auth.update_session_auth_hash(request, user)
                    send_email.delay(user.email, subject='Пароль на Matematics изменен!',
                                     message=f'{user.email}, Ваш пароль изменен!')
        except KeyError:
            pass
        user.save()
        return redirect('users:profile')
    return render(request, 'users/profile.html')


def statistics(request):
    if request.user.id:
        user = get_object_or_404(User, id=request.user.id)
        tests = user.users_solved_tests.order_by('-created')
        return render(request, 'users/statistics.html',
                      {'tests': tests})
    else:
        return redirect('users:login')


def logout(request):
    auth.logout(request)
    return redirect('main:topic_list')


def favorites(request):
    if request.method == 'POST':
        if request.user.id:
            user = get_object_or_404(User, id=request.user.id)
            task = get_object_or_404(Task, id=json.loads(request.body.decode())['task_id'])
            if task in user.favorites_tasks.all():
                user.favorites_tasks.remove(task)
            else:
                user.favorites_tasks.add(task)
            user.save()
            return JsonResponse({
                'data': 'success'
                })
        else:
            return JsonResponse({
                'data': 'failed'
                })
    if request.user.id:
        user = get_object_or_404(User, id=request.user.id)
        tasks = user.favorites_tasks.all()
        return render(request, 'users/favorites.html',
                    {'tasks': tasks})
    else:
        return redirect('users:login')
    

def forgot_password(request):
    if request.method == 'GET':
        return render(request, 'users/forgot-password.html')
    else:
        form = UserLoginForm(request.POST)
        form.is_valid()
        try:
            email = form.cleaned_data['email']
        except KeyError:
            return render(request, 'users/login.html')
        user = User.objects.filter(email=email).first()
        if user:
            user.verification_token = secrets.token_urlsafe(32)
            user.set_pass_link_created = time.time()
            user.save()
            send_email.delay(email=user.email, subject='Восстановление на Matematics',
                             message=f'Для восстановления пароля, пройдите по ссылке: 127.0.0.1:8000/users/set-new-pass/{user.verification_token}')
            return redirect('users:forgot_password')
        else:
            return render(request, 'users/forgot-password.html', {'form': form})
        

def set_new_pass(request, verification_token):
    if request.method == 'GET':
        if request.user.id:
            auth.logout(request)
        user = get_object_or_404(User, verification_token=verification_token)
        if (time.time() - float(user.set_pass_link_created)) < 120: 
            return render(request, 'users/set-new-pass.html')
        else:
            return redirect('users:login')
    else:
        user = get_object_or_404(User, verification_token=verification_token)
        if (time.time() - float(user.set_pass_link_created)) < 120: 
            form = UserRegistrationForm(request.POST)
            form.is_valid()
            try:
                if form.cleaned_data['password'] and form.cleaned_data['password_check']:
                    if form.cleaned_data['password'] == form.cleaned_data['password_check']:
                        user.set_password(form.cleaned_data['password'])
                        user.verification_token = secrets.token_urlsafe(32)
                        user.save()
                        auth.login(request, user)
                        send_email.delay(user.email, subject='Пароль на Matematics изменен!',
                                         message=f'{user.email}, Ваш пароль изменен!')
                        return redirect('main:topic_list')
            except KeyError:
                return redirect('main:topic_list')
        else:
            return redirect('users:login')
        

def get_proof_link(request):
    if request.method == 'GET' and request.user.id:
        user = get_object_or_404(User, id=request.user.id)
        user.verification_token = secrets.token_urlsafe(32)
        user.save()
        send_email.delay(user.email, subject='Восстановление на Matematics',
                         message=f'Для восстановления пароля, пройдите по ссылке: 127.0.0.1:8000/users/set-new-pass/{user.verification_token}')
        return redirect('users:profile')
    else:
        return redirect('main:topic_list')