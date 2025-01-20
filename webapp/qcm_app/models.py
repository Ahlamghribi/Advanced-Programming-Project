from django.db import models

class UserProfile(models.Model):
    username = models.CharField(max_length=100, unique=True)
    history = models.JSONField(default=list)

class Question(models.Model):
    question_text = models.TextField()
    options = models.JSONField()
    answer = models.CharField(max_length=1)
    time_limit = models.IntegerField(default=30)
    category = models.CharField(max_length=100)
