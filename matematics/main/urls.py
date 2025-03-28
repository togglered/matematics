from django.urls import path 
from . import views


app_name = 'main'

urlpatterns = [
    path('', views.topic_list, name='topic_list'),
    path('test/<int:test_id>/', views.open_test, name='open_test'),
    path('task-detail/<int:id>/', views.get_task, name='get_task'),
    path('search/', views.search, name='search'),
    path('test-result/<int:solved_test_id>/', views.test_result, name='test_result'),
    path('topic-tasks/<int:number>', views.topic_tasks, name='topic_tasks'),
    path('category-tasks/<int:id>/', views.category_tasks, name='category_tasks'),
]