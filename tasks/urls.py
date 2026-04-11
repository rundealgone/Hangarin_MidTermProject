from django.urls import path
from . import views

urlpatterns = [
    # SubTask & Note list pages
    path('subtasks/', views.subtask_list, name='subtask_list'),
    path('notes/', views.note_list, name='note_list'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Tasks
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/edit/', views.task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),

    # Subtasks
    path('tasks/<int:task_pk>/subtasks/add/', views.subtask_create, name='subtask_create'),
    path('subtasks/<int:pk>/edit/', views.subtask_update, name='subtask_update'),
    path('subtasks/<int:pk>/delete/', views.subtask_delete, name='subtask_delete'),

    # Notes
    path('tasks/<int:task_pk>/notes/add/', views.note_create, name='note_create'),
    path('notes/<int:pk>/delete/', views.note_delete, name='note_delete'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Priorities
    path('priorities/', views.priority_list, name='priority_list'),
    path('priorities/create/', views.priority_create, name='priority_create'),
    path('priorities/<int:pk>/edit/', views.priority_update, name='priority_update'),
    path('priorities/<int:pk>/delete/', views.priority_delete, name='priority_delete'),
]
