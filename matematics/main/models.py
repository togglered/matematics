from django.apps import apps
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Topic(models.Model):
    number = models.IntegerField(unique=True)
    max_score = models.IntegerField()
    name = models.TextField(max_length=100, unique=True)
    slug = models.SlugField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['number']
        indexes = [
            models.Index(fields=['number']),
            models.Index(fields=['created']),
        ]
        verbose_name = 'Номер задачи'
        verbose_name_plural = 'Номера задач'

    
    def __str__(self):
        return str(self.number)
    

class Category(models.Model):
    topic = models.ForeignKey(Topic,
                              related_name='categories',
                              on_delete=models.CASCADE)
    name = models.TextField(max_length=100,
                            unique=True)
    slug = models.SlugField(max_length=40,
                            unique=True)
    

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    
    def __str__(self):
        return str(self.name)


class Task(models.Model):
    topic = models.ForeignKey(Topic,
                              related_name='tasks',
                              on_delete=models.CASCADE)
    category = models.ForeignKey(Category,
                                  related_name='tasks',
                                  on_delete=models.CASCADE,
                                  blank=True)
    first_text = models.TextField(max_length=2000)
    second_text = models.TextField(max_length=2000, blank=True)
    image = models.ImageField(upload_to='images/%Y/%m/%d',
                              blank=True)
    solution_image = models.ImageField(upload_to='images/%Y/%m/%d',
                              blank=True)
    solution = models.TextField(max_length=1000)
    answer = models.TextField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    right_solved = models.IntegerField(default=0)
    solved_count = models.IntegerField(default=0)
    solved_percent = models.IntegerField(default=100)


    class Meta:
        ordering = ['category']
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['category']),
            models.Index(fields=['created']),
        ]
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    
    def solved(self, *args, **kwargs):
        solved_task = kwargs.pop('solved_task')
        self.solved_count += 1
        if solved_task.score == self.topic.max_score:
            self.right_solved += 1
        self.solved_percent = self.right_solved * 100 // self.solved_count
        super().save(*args, **kwargs)


    def __str__(self):
        return str(self.id)
    

    def get_absolute_url(self):
        return reverse('main:task_detail',
                       args=[self.id])
    

class SolvedTask(models.Model):
    main_task_obj = models.ForeignKey(Task, related_name='solved_tasks', on_delete=models.CASCADE)
    gived_answer = models.CharField(max_length=20, null=True)
    images = models.ManyToManyField('PhotoFile')
    score = models.IntegerField(default=0)
    created = models.DateTimeField(default=timezone.now)


    def save(self, *args, **kwargs):
        if self.gived_answer == self.main_task_obj.answer:
            self.score = self.main_task_obj.topic.max_score
        super().save(*args, **kwargs)


    class Meta:
        verbose_name = 'Решенная задача'
        verbose_name_plural = 'Решенные задачи'


class Test(models.Model):
    tasks = models.ManyToManyField('Task')
    created_by = models.ForeignKey('users.User', related_name='users_created_tests', on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    status = models.CharField(default='in_progress', max_length=50)
    name = models.CharField(default='', max_length=100)


    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.name = 'Тест №' + str(self.id)


    def __str__(self):
        return f'id = {self.id}'


    def get_absolute_url(self):
        return reverse('main:test',
                       args=[self.id])


class SolvedTest(models.Model):
    main_test = models.ForeignKey(Test, related_name='solved_tests', on_delete=models.CASCADE)
    users_answers = models.ManyToManyField('SolvedTask')
    checked = models.BooleanField(default=False)
    solved_by = models.ForeignKey('users.User', related_name='users_solved_tests', 
                                  on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)

    first_part_exist = models.BooleanField(default=False)
    first_part_score = models.IntegerField(default=0)
    first_part_max_score = models.IntegerField(default=0)

    second_part_exist = models.BooleanField(default=False)
    second_part_score = models.IntegerField(default=0)
    second_part_max_score = models.IntegerField(default=0)

    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)


    class Meta:
            verbose_name = 'Результат теста'
            verbose_name_plural = 'Результаты тестов'


    def count(self, *args, **kwargs):
        self.first_part_exist = 0
        self.first_part_score = 0
        self.first_part_max_score = 0
        self.second_part_exist = 0
        self.second_part_score = 0
        self.second_part_max_score = 0
        self.score = 0
        self.max_score = 0
        for task in self.main_test.tasks.all():
            if task.topic.number > 19:
                self.second_part_exist = True
                try:
                    self.second_part_max_score += task.topic.max_score
                except TypeError:
                    self.second_part_max_score += 0
            else:
                self.first_part_exist = True
                self.first_part_max_score += task.topic.max_score
        for task in self.users_answers.all():
            if task.main_task_obj.topic.number > 19:
                self.second_part_score += int(task.score)
            else:
                self.first_part_score += int(task.score)
        self.score = self.first_part_score + self.second_part_score
        self.max_score = self.first_part_max_score + self.second_part_max_score
        super().save(*args, **kwargs)



class PhotoFile(models.Model):
    file = models.FileField(upload_to='images/users_answers',
                              blank=True)
    

    class Meta:
        verbose_name = 'фото/файл'
        verbose_name_plural = 'фаото/файлы'