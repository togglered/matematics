from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from users.models import User
import json
from .forms import NewTestName
from main.models import Task, Test, Topic


def my_tests(request):
    if request.method == 'GET':
        if request.user.id:
            user = get_object_or_404(User, id=request.user.id)
            tests = user.users_created_tests.all().order_by('-created')
            return render(request, 'tests/my-tests.html',
                        {'tests': tests})
        else:
            return redirect('users:login')
    

def test_info(request, test_id):
    if request.method == 'POST' and request.user.id:
        user = get_object_or_404(User, id=request.user.id)
        test = get_object_or_404(Test, id=test_id)
        referer = request.META.get('HTTP_REFERER')
        if user == test.created_by:
            form = NewTestName(request.POST)
            form.is_valid()
            try:
                new_name = form.cleaned_data['new_name']
                test.name = new_name
            except KeyError:
                pass
            test.save()
        return redirect(referer)
    elif request.user.id:
        topics = Topic.objects.all()
        user = get_object_or_404(User, id=request.user.id)
        test = get_object_or_404(Test, id=test_id)
        creator = test.created_by
        if user == creator:
            tasks = test.tasks.all().order_by('topic')
            return render(request, 'tests/test-info.html',
                        {'test': test,
                        'tasks': tasks,
                        'topics': topics})
        else:
            return redirect('main:topic_list')
    else:
        return redirect('users:login')
        

def create_test(request):
    if request.method == 'POST':
        '''
            Добавление задачи в тест вручную из каталога
        '''
        chosen_tests = json.loads(request.body.decode())
        task_id = chosen_tests['task_id']
        task = get_object_or_404(Task, id=task_id)
        del chosen_tests['task_id']
        for test, value in chosen_tests.items():
            if int(value):
                test = get_object_or_404(Test, id=test)
                test.tasks.add(task)
                test.save()
        return JsonResponse({'data': "success"})
    else:
        '''
            Создание теста
        '''
        if request.user.id:
            user = get_object_or_404(User, id=request.user.id)
            new_test = Test.objects.create(created_by=user)
            new_test.save()
            return redirect('tests:my_tests')
        else:
            return redirect('users:login')


def delete_task_from_test(request, test_id):
    if request.method == 'POST' and request.user.id:
        user = get_object_or_404(User, id=request.user.id)
        test = get_object_or_404(Test, id=test_id)
        if test in user.users_created_tests.all():
            task = get_object_or_404(Task, id=json.loads(request.body.decode())['task_id'])
            test.tasks.remove(task)
            test.save()
            return JsonResponse({'data': 'success'})
        else:
            return JsonResponse({'data': 'failed'})
    else:
        return redirect('users:login')
    

def delete_test(request, test_id):
    if request.method == 'POST' and request.user.id:
        user = get_object_or_404(User, id=request.user.id)
        test = get_object_or_404(Test, id=test_id)
        if test in user.users_created_tests.all():
            test.delete()
        return redirect('tests:my_tests')
    else:
        return redirect('users:login')
    

def publish_test(request, test_id):
    if request.user.id:
        user = get_object_or_404(User, id=request.user.id)
        referer = request.META.get('HTTP_REFERER')
        test = get_object_or_404(Test, id=test_id)
        if test in user.users_created_tests.all():
            test.status = 'published'
            test.save()
            return redirect(referer)
    else:
        return redirect('main:topic_list')


def add_random_task(request, test_id, type, id):
    if request.method == 'GET':
        referer = request.META.get('HTTP_REFERER')
        test = get_object_or_404(Test, id=test_id)
        user = get_object_or_404(User, id=request.user.id)
        if user == test.created_by:
            if type == 'topic':
                added_tasks = test.tasks.all()
                all_tasks = Task.objects.filter(topic__id=id)
                tasks_range = all_tasks.exclude(id__in=added_tasks.values_list('id', flat=True))
                if tasks_range:
                    task = tasks_range.order_by('?').first()
                    test.tasks.add(task)
                    test.save()
                return redirect(referer)
            elif type == 'category':
                added_tasks = test.tasks.all()
                all_tasks = Task.objects.filter(category__id=id)
                tasks_range = all_tasks.exclude(id__in=added_tasks.values_list('id', flat=True))
                if tasks_range:
                    task = tasks_range.order_by('?').first()
                    test.tasks.add(task)
                    test.save()
                return redirect(referer)
            else:
                return redirect('main:topic_list')
        else:
            return redirect('users:login')
