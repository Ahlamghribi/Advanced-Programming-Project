from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('choose_category/<str:user_id>/', views.choose_category, name='choose_category'), 
    path('quiz/<str:user_id>/', views.quiz, name='quiz'),  
    path('result/<str:user_id>/', views.result, name='result'), 
     path('save_quiz_history/<str:user_id>/', views.save_quiz_history, name='save_quiz_history'),
    path('export_history/<str:user_id>/', views.export_history, name='export_history'),

]
