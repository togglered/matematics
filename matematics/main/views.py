from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Topic, Category, Task, Test, SolvedTest, PhotoFile, SolvedTask
from .forms import GetMainPageData, GetUsersAnswers
from users.models import User
import random


def category_tasks(request, id: int):
    in_progress_tests = []
    if request.user.id:
        user = get_object_or_404(User, id=request.user.id)
        in_progress_tests = user.users_created_tests.filter(status='in_progress')
    sorted = request.GET.get('sorted')
    if not sorted:
        sorted = '-created'
    category = get_object_or_404(Category, id=id)
    tasks = Task.objects.filter(category=category).order_by(sorted)
    showed_tasks = int(request.GET.get('showed', 10))
    current_page = int(request.GET.get('page', 1))
    try:
        current_page_tasks = tasks[(showed_tasks) * (current_page - 1):(showed_tasks) * current_page]
    except IndexError:
        current_page_tasks = tasks[(showed_tasks) * (current_page - 1):len(tasks) + 1]
    if len(tasks) / showed_tasks % 1 == 0:
        pages = range(1, len(tasks) // showed_tasks + 1)
    else:
        pages = range(1, len(tasks) // showed_tasks + 2)
    counter_start = (showed_tasks) * (current_page - 1)
    return render(request,
                  'main/category-tasks/category-tasks.html',
                  {'tasks': current_page_tasks,
                   'counter_start': counter_start,
                   'current_page': current_page,
                   'pages': pages,
                   'category': category,
                   'in_progress_tests': in_progress_tests})


def topic_tasks(request, number: int):
    in_progress_tests = []
    if request.user.id:
        user = get_object_or_404(User, id=request.user.id)
        in_progress_tests = user.users_created_tests.filter(status='in_progress')
    sorted = request.GET.get('sorted')
    if not sorted:
        sorted = '-created'
    topic = get_object_or_404(Topic, number=number)
    tasks = Task.objects.filter(topic=topic).order_by(sorted)
    showed_tasks = int(request.GET.get('showed', 10))
    current_page = int(request.GET.get('page', 1))
    try:
        current_page_tasks = tasks[(showed_tasks) * (current_page - 1):(showed_tasks) * current_page]
    except IndexError:
        current_page_tasks = tasks[(showed_tasks) * (current_page - 1):len(tasks) + 1]
    if len(tasks) / showed_tasks % 1 == 0:
        pages = range(1, len(tasks) // showed_tasks + 1)
    else:
        pages = range(1, len(tasks) // showed_tasks + 2)
    counter_start = showed_tasks * (current_page - 1)
    return render(request,
                  'main/topic-tasks/topic-tasks.html',
                  {'tasks': current_page_tasks,
                   'counter_start': counter_start,
                   'current_page': current_page,
                   'pages': pages,
                   'topic': topic,
                   'in_progress_tests': in_progress_tests})


def test_result(request, solved_test_id: int):
    if request.method == 'POST':
        solved_test = get_object_or_404(SolvedTest, id=solved_test_id)
        solved_tasks = solved_test.users_answers.all().order_by('main_task_obj__topic__number')
        dynamic_fields = {}
        for solved_task in solved_tasks:
            task = solved_task.main_task_obj
            dynamic_fields[str(task.id)] = 'option'
        users_test = GetUsersAnswers(request.POST, dynamic_fields=dynamic_fields).get_cleaned_data()
        for solved_task in solved_tasks:
            try:
                solved_task.score = int(users_test[str(solved_task.main_task_obj.id)])
                solved_task.save()
                solved_task.main_task_obj.solved(solved_task=solved_task)
            except KeyError:
                pass
        solved_test.checked = True
        solved_test.users_answers.set(solved_tasks)
        solved_test.count()
        return redirect('main:test_result', solved_test.id)
    else:
        solved_test = get_object_or_404(SolvedTest, id=solved_test_id)
        solved_tasks = solved_test.users_answers.all()
        if solved_test.checked:
            return render(request,
                    'main/test-result/test-result.html',
                    {'solved_tasks': solved_tasks,
                    'solved_test': solved_test,})
        else:
            test_creator = solved_test.main_test.created_by
            if test_creator and request.user.id:
                user = get_object_or_404(User, id=request.user.id)
                if test_creator == user:
                    return render(request,
                            'main/test-result/test-check.html',
                            {'solved_tasks': solved_tasks,
                            })
                else:
                    return redirect('main:topic_list')
            elif test_creator and not request.user.id:
                return redirect('main:topic_list')
            else:
                return render(request,
                            'main/test-result/test-check.html',
                            {'solved_tasks': solved_tasks,
                            })


def open_test(request, test_id: int):
    if request.method == 'POST':
        test_obj = get_object_or_404(Test, id=test_id)
        checked = True
        users_answers = {}
        dynamic_fields = {}
        for task in Task.objects.all():
            dynamic_fields[str(task.id)] = 'text'
        users_test = GetUsersAnswers(request.POST, dynamic_fields=dynamic_fields).get_cleaned_data()
        for task in test_obj.tasks.all():
            try:
                solved_task = SolvedTask.objects.create(main_task_obj=task,
                                                        gived_answer=users_test[str(task.id)])
                task.solved(solved_task=solved_task)
                users_answers[task.id] = solved_task
            except KeyError:
                if task.topic.number > 19:
                    solved_task = SolvedTask.objects.create(main_task_obj=task, gived_answer=None)
                    users_answers[task.id] = solved_task
                    checked = False
                else:
                    solved_task = SolvedTask.objects.create(main_task_obj=task, gived_answer='Нет ответа',
                                                            score=0)
                    task.solved(solved_task=solved_task)
                    users_answers[task.id] = solved_task
        files = dict(request.FILES)
        for task, photos in files.items():
            task = get_object_or_404(Task, id=task)
            images_temp = []
            for photo in photos:
                new_photo_obj = PhotoFile.objects.create(file=photo)
                images_temp.append(new_photo_obj)
            if images_temp:
                users_answers[task.id].images.set(images_temp)
                checked = False

        if request.user.id:
            user = get_object_or_404(User, id=request.user.id)
            db_new_test = SolvedTest.objects.create(main_test=test_obj, checked=checked, solved_by=user)
        else:
            db_new_test = SolvedTest.objects.create(main_test=test_obj, checked=checked)
        db_new_test.users_answers.set(users_answers.values())
        db_new_test.count()
        db_new_test.save()
        return redirect('main:test_result', db_new_test.id)
    else:
        test = get_object_or_404(Test, id=test_id)
        return render(request,
                    'main/test/test.html',
                    {'test': test})

def topic_list(request):
    if request.method == 'POST':
        dynamic_fields = {}
        for topic in Topic.objects.all():
            dynamic_fields[str(topic.number)] = 'tel'
        activated_topics = GetMainPageData(request.POST, dynamic_fields=dynamic_fields).get_topics()
        dynamic_fields = {}
        for category in Category.objects.all():
            dynamic_fields[str(category.slug)] = 'checkbox'
        
        categories_slugs = GetMainPageData(request.POST, dynamic_fields=dynamic_fields).get_categories()
        categories_ids = list(Category.objects.filter(slug__in=categories_slugs).values_list('id', flat=True))
        random_tasks = []
        for topic, task_count in activated_topics.items():
            all_tasks_objects = list(Task.objects.filter(category__in=categories_ids))
            topic = get_object_or_404(Topic, number=topic)
            if bool(set(categories_ids) & set(topic.categories.all().values_list('id', flat=True))):
                if task_count < len(all_tasks_objects):
                    random_tasks += random.sample(all_tasks_objects, task_count)
                else:
                    random_tasks += all_tasks_objects
            else:
                all_tasks_objects = list(Task.objects.filter(topic=topic).values_list('id', flat=True))
                if task_count < len(all_tasks_objects):
                    random_tasks += random.sample(all_tasks_objects, task_count)
                else:
                    random_tasks += all_tasks_objects
        if random_tasks:
            if request.user.id :
                user = get_object_or_404(User, id=request.user.id)
                created_test = Test.objects.create(created_by=user, status='published')
            else:
                created_test = Test.objects.create(status='published')
            created_test.tasks.set(random_tasks)
            return redirect('main:open_test', created_test.id)
        else:
            return redirect('main:topic_list')
    else:
        topics = Topic.objects.all()
        return render(request,
                    'main/index/index.html',
                    {'topics': topics})


def get_task(request, id: int):
    task = get_object_or_404(Task,
                             id=id)
    return render(request,
                  'main/task-detail/task-detail.html',
                  {'task': task})


def search(request):
    search_req = request.GET.get('req')
    tasks = Task.objects.filter(
        Q(first_text__icontains=search_req) | Q(second_text__icontains=search_req) |
        Q(solution__icontains=search_req) | Q(answer__icontains=search_req) |
        Q(id__icontains=search_req)
    )
    return render(request,
                  'main/search/search.html',
                  {'tasks': tasks,
                   'search_req': search_req})
