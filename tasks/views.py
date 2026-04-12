from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
from .models import Task, SubTask, Note, Category, Priority
from .forms import TaskForm, SubTaskForm, NoteForm, CategoryForm, PriorityForm





@login_required
def dashboard(request):
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status="Completed").count()
    pending_tasks = Task.objects.filter(status="Pending").count()
    in_progress_tasks = Task.objects.filter(status="In Progress").count()
    total_subtasks = SubTask.objects.count()
    total_notes = Note.objects.count()

    recent_tasks = Task.objects.select_related('category', 'priority').order_by('-created_at')[:5]

    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'total_subtasks': total_subtasks,
        'total_notes': total_notes,
        'recent_tasks': recent_tasks,
    }
    return render(request, 'tasks/dashboard.html', context)





@login_required
def task_list(request):
    qs = Task.objects.select_related('category', 'priority')

    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    sort = request.GET.get('sort', '-created_at')

    if query:
        qs = qs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    if status_filter:
        qs = qs.filter(status=status_filter)
    if category_filter:
        qs = qs.filter(category__id=category_filter)

    valid_sorts = ['title', '-title', 'created_at', '-created_at', 'deadline', '-deadline', 'status', '-status']
    if sort in valid_sorts:
        qs = qs.order_by(sort)

    paginator = Paginator(qs, 10)
    try:
        tasks = paginator.page(request.GET.get('page', 1))
    except Exception:
        tasks = paginator.page(1)

    context = {
        'tasks': tasks,
        'categories': Category.objects.all(),
        'query': query,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'sort': sort,
        'status_choices': [("Pending", "Pending"), ("In Progress", "In Progress"), ("Completed", "Completed")],
    }
    return render(request, 'tasks/task_list.html', context)



@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    subtasks = task.subtasks.all()
    notes = task.notes.all()
    subtask_form = SubTaskForm()
    note_form = NoteForm()
    context = {
        'task': task,
        'subtasks': subtasks,
        'notes': notes,
        'subtask_form': subtask_form,
        'note_form': note_form,
    }
    return render(request, 'tasks/task_detail.html', context)



@login_required
def task_create(request):
    form = TaskForm(request.POST or None)
    if form.is_valid():
        task = form.save()
        messages.success(request, f'Task "{task.title}" created successfully.')
        return redirect('task_detail', pk=task.pk)
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Create'})



@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    form = TaskForm(request.POST or None, instance=task)
    if form.is_valid():
        form.save()
        messages.success(request, f'Task "{task.title}" updated successfully.')
        return redirect('task_detail', pk=task.pk)
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Edit', 'task': task})



@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        title = task.title
        task.delete()
        messages.success(request, f'Task "{title}" deleted.')
        return redirect('task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'object': task, 'type': 'Task'})





@login_required
def subtask_create(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    form = SubTaskForm(request.POST or None)
    if form.is_valid():
        subtask = form.save(commit=False)
        subtask.parent_task = task
        subtask.save()
        messages.success(request, 'Subtask added.')
        return redirect('task_detail', pk=task_pk)
    return render(request, 'tasks/task_detail.html', {
        'task': task, 'subtask_form': form,
        'subtasks': task.subtasks.all(), 'notes': task.notes.all(), 'note_form': NoteForm()
    })



@login_required
def subtask_update(request, pk):
    subtask = get_object_or_404(SubTask, pk=pk)
    form = SubTaskForm(request.POST or None, instance=subtask)
    if form.is_valid():
        form.save()
        messages.success(request, 'Subtask updated.')
        return redirect('task_detail', pk=subtask.parent_task.pk)
    return render(request, 'tasks/subtask_form.html', {'form': form, 'subtask': subtask})



@login_required
def subtask_delete(request, pk):
    subtask = get_object_or_404(SubTask, pk=pk)
    task_pk = subtask.parent_task.pk
    if request.method == 'POST':
        subtask.delete()
        messages.success(request, 'Subtask deleted.')
        return redirect('task_detail', pk=task_pk)
    return render(request, 'tasks/task_confirm_delete.html', {'object': subtask, 'type': 'Subtask'})





@login_required
def note_create(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    form = NoteForm(request.POST or None)
    if form.is_valid():
        note = form.save(commit=False)
        note.task = task
        note.save()
        messages.success(request, 'Note added.')
    return redirect('task_detail', pk=task_pk)



@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk)
    task_pk = note.task.pk
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted.')
        return redirect('task_detail', pk=task_pk)
    return render(request, 'tasks/task_confirm_delete.html', {'object': note, 'type': 'Note'})





@login_required
def category_list(request):
    query = request.GET.get('q', '')
    qs = Category.objects.all()
    if query:
        qs = qs.filter(name__icontains=query)
    paginator = Paginator(qs, 10)
    try:
        categories = paginator.page(request.GET.get('page', 1))
    except Exception:
        categories = paginator.page(1)
    return render(request, 'tasks/category_list.html', {'categories': categories, 'query': query})



@login_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Category created.')
        return redirect('category_list')
    return render(request, 'tasks/category_form.html', {'form': form, 'action': 'Create'})



@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        messages.success(request, 'Category updated.')
        return redirect('category_list')
    return render(request, 'tasks/category_form.html', {'form': form, 'action': 'Edit'})



@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted.')
        return redirect('category_list')
    return render(request, 'tasks/task_confirm_delete.html', {'object': category, 'type': 'Category'})





@login_required
def priority_list(request):
    query = request.GET.get('q', '')
    qs = Priority.objects.all()
    if query:
        qs = qs.filter(name__icontains=query)
    paginator = Paginator(qs, 10)
    try:
        priorities = paginator.page(request.GET.get('page', 1))
    except Exception:
        priorities = paginator.page(1)
    return render(request, 'tasks/priority_list.html', {'priorities': priorities, 'query': query})



@login_required
def priority_create(request):
    form = PriorityForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Priority created.')
        return redirect('priority_list')
    return render(request, 'tasks/priority_form.html', {'form': form, 'action': 'Create'})



@login_required
def priority_update(request, pk):
    priority = get_object_or_404(Priority, pk=pk)
    form = PriorityForm(request.POST or None, instance=priority)
    if form.is_valid():
        form.save()
        messages.success(request, 'Priority updated.')
        return redirect('priority_list')
    return render(request, 'tasks/priority_form.html', {'form': form, 'action': 'Edit'})



@login_required
def priority_delete(request, pk):
    priority = get_object_or_404(Priority, pk=pk)
    if request.method == 'POST':
        priority.delete()
        messages.success(request, 'Priority deleted.')
        return redirect('priority_list')
    return render(request, 'tasks/task_confirm_delete.html', {'object': priority, 'type': 'Priority'})




@login_required
def subtask_list(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    qs = SubTask.objects.select_related('parent_task')
    if query:
        qs = qs.filter(Q(title__icontains=query) | Q(parent_task__title__icontains=query))
    if status_filter:
        qs = qs.filter(status=status_filter)
    paginator = Paginator(qs, 10)
    try:
        subtasks = paginator.page(request.GET.get('page', 1))
    except Exception:
        subtasks = paginator.page(1)
    status_choices = [("Pending", "Pending"), ("In Progress", "In Progress"), ("Completed", "Completed")]
    return render(request, 'tasks/subtask_list.html', {
        'subtasks': subtasks, 'query': query,
        'status_filter': status_filter, 'status_choices': status_choices
    })




@login_required
def note_list(request):
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', '-created_at')
    qs = Note.objects.select_related('task')
    if query:
        qs = qs.filter(Q(content__icontains=query) | Q(task__title__icontains=query))
    if sort in ['created_at', '-created_at']:
        qs = qs.order_by(sort)
    else:
        qs = qs.order_by('-created_at')
    paginator = Paginator(qs, 10)
    try:
        notes = paginator.page(request.GET.get('page', 1))
    except Exception:
        notes = paginator.page(1)
    return render(request, 'tasks/note_list.html', {'notes': notes, 'query': query, 'sort': sort})

def custom_logout(request):
    auth_logout(request)
    return redirect('/accounts/login/')
