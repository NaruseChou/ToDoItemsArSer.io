from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
# Imports for Reordering Feature
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.list import ListView
from django.http import HttpResponse
from django.db import connection
from django.shortcuts import render
from django.contrib import messages
from django.db import transaction

from .forms import PositionForm
from .models import Task


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')


class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Существующий код (оставляем без изменений)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(title__contains=search_input)
        context['search_input'] = search_input

        # Новый код: добавляем общее количество задач через raw SQL
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM base_task WHERE user_id = %s",
                [self.request.user.id]
            )
            context['total_count'] = cursor.fetchone()[0]

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'base_task'
                ORDER BY ordinal_position
            """)
            context['table_structure'] = cursor.fetchall()

        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)  # Валидация 100 символов работает автоматически через модель

class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')


class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
    def get_queryset(self):
        owner = self.request.user
        return self.model.objects.filter(user=owner)


class TaskReorder(View):
    def post(self, request):
        form = PositionForm(request.POST)

        if form.is_valid():
            positionList = form.cleaned_data["position"].split(',')

            with connection.cursor() as cursor:
                for idx, task_id in enumerate(positionList, start=1):
                    cursor.execute(
                        "UPDATE base_task SET _order = %s WHERE id = %s AND user_id = %s",
                        [idx, task_id, request.user.id]
                    )

        return redirect(reverse_lazy('tasks')
                        )



def get_task_count(request):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM base_task WHERE user_id = %s",
            [request.user.id]
        )
        count = cursor.fetchone()[0]  # fetchone() возвращает кортеж, например (5,)
    return HttpResponse(f"Total tasks: {count}")


def get_table_info(request):
    if not request.user.is_authenticated:
        return HttpResponse("Please log in to view table info", status=401)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'base_task'
        """)
        columns = cursor.fetchall()

        # Форматируем вывод в читаемом виде
        result = "<h2>Database Table Structure: base_task</h2><ul>"
        for name, dtype in columns:
            result += f"<li><b>{name}</b>: {dtype}</li>"
        result += "</ul>"

        return HttpResponse(result)