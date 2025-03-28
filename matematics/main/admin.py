from django.contrib import admin
from .models import Topic, Category, Task, Test, SolvedTest, PhotoFile, SolvedTask


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['id', 'max_score', 'number', 'name', 'slug']
    list_editable = ['number', 'max_score', 'name', 'slug']
    prepopulated_fields = {'slug': ('number', 'name')}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'topic', 'name', 'slug']
    prepopulated_fields = {'slug': ['name']}


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'id', 'category', 'first_text',
                    'second_text', 'image', 'solution_image',
                    'solution', 'answer', 'right_solved', 'solved_count']
    list_filter = ['created', 'updated']
    list_editable = ['category', 'first_text',
                    'second_text', 'image', 'solution_image',
                    'solution', 'answer']
    

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created_by']
    list_editable = []


@admin.register(SolvedTest)
class TestAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'main_test', 'checked', 'first_part_exist', 'first_part_score']
    list_editable = ['main_test', 'checked', 'first_part_exist', 'first_part_score']


@admin.register(PhotoFile)
class TestAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'file']
    list_editable = ['file']


@admin.register(SolvedTask)
class TestAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'main_task_obj', 'gived_answer', 'score']
    list_editable = ['main_task_obj', 'gived_answer', 'score']

