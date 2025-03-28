from django.urls import path
from . import views


app_name = 'tests'


urlpatterns = [
    path('my-tests/', views.my_tests, name='my_tests'),
    path('test-info/<int:test_id>', views.test_info, name='test_info'),
    path('delete-task-from-test/<int:test_id>', views.delete_task_from_test, name='delete_task_from_test'),
    path('publish-test/<int:test_id>', views.publish_test, name='publish_test'),
    path('delete-test/<int:test_id>', views.delete_test, name='delete_test'),
    path('add-random-task/<int:test_id>/<str:type>/<int:id>/', views.add_random_task, name='add_random_task'),
    path('create-test/', views.create_test, name='create_test'),
]
