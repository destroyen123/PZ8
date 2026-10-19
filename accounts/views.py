from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from .forms import DepartmentForm, AcademicGroupForm, CourseForm
from .models import Course, AcademicGroup, Department
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

def is_methodist(user):
    return user.is_superuser or user.groups.filter(
        name='Методист'
    ).exists()
@login_required
def profile(request):
    return render(request, 'profile.html', {
        'is_methodist': is_methodist(request.user)
    })


@login_required
def course_list(request):
    courses = Course.objects.select_related('department').all()

    return render(
        request,
        'course_list.html',
        {
        'courses': courses,
        'is_methodist': is_methodist(request.user),
        }
)

@login_required
@user_passes_test(is_methodist)
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'object_form.html', {
        'form': form,
        'title': 'Добавление курса',
    })

@login_required
@user_passes_test(is_methodist)
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'object_form.html', {
        'form': form,
        'title': 'Изменение курса',
    })

@login_required
@user_passes_test(is_methodist)
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        return redirect('course_list')
    return render(request, 'object_confirm_delete.html', {
        'object': course,
        'title': 'Удаление курса',
    })


@login_required
def profile(request):
    return render(
        request,
        'profile.html',
        {
            'is_methodist': is_methodist(
                request.user
            )
        }
    )


@login_required
def department_list(request):
    departments = Department.objects.all()

    return render(
        request,
        'department_list.html',
        {
            'departments': departments,
            'is_methodist': is_methodist(
                request.user
            ),
        }
    )

@login_required
@user_passes_test(is_methodist)
def department_create(request):
    if request.method == 'POST':

        form = DepartmentForm(
            request.POST
        )

        if form.is_valid():
            form.save()

            return redirect(
                'department_list'
            )

    else:
        form = DepartmentForm()

    return render(
        request,
        'object_form.html',
        {
            'form': form,
            'title': 'Добавление факультета',
        }
    )


@login_required
@user_passes_test(is_methodist)
def department_update(
        request,
        pk
):
    department = get_object_or_404(
        Department,
        pk=pk
    )

    if request.method == 'POST':

        form = DepartmentForm(
        request.POST,
        instance = department
        )

        if form.is_valid():
            form.save()

            return redirect(
                'department_list'
            )

    else:

        form = DepartmentForm(
            instance=department
        )

    return render(
        request,
        'object_form.html',
        {
            'form': form,
            'title': 'Изменение факультета',
        }
    )


@login_required
@user_passes_test(is_methodist)
def department_delete(
        request,
        pk
):
    department = get_object_or_404(
        Department,
        pk=pk
    )

    if request.method == 'POST':
        department.delete()

        return redirect(
            'department_list'
        )

    return render(
        request,
        'object_confirm_delete.html',
        {
            'object': department,
            'title': 'Удаление факультета',
        }
    )

@login_required
def group_list(request):
    groups = AcademicGroup.objects.all()
    return render(request, 'group_list.html', {
        'groups': groups,
        'is_methodist': is_methodist(request.user),
    })

@login_required
@user_passes_test(is_methodist)
def group_create(request):
    if request.method == 'POST':
        form = AcademicGroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('group_list')
    else:
        form = AcademicGroupForm()
    return render(request, 'object_form.html', {
        'form': form,
        'title': 'Добавление группы',
    })

@login_required
@user_passes_test(is_methodist)
def group_update(request, pk):
    group = get_object_or_404(AcademicGroup, pk=pk)
    if request.method == 'POST':
        form = AcademicGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group_list')
    else:
        form = AcademicGroupForm(instance=group)
    return render(request, 'object_form.html', {
        'form': form,
        'title': 'Изменение группы',
    })

@login_required
@user_passes_test(is_methodist)
def group_delete(request, pk):
    group = get_object_or_404(AcademicGroup, pk=pk)
    if request.method == 'POST':
        group.delete()
        return redirect('group_list')
    return render(request, 'object_confirm_delete.html', {
        'object': group,
        'title': 'Удаление группы',
    })
@login_required
def dashboard(request):
    departments = Department.objects.all()

    department_names = []
    courses_by_department = []
    groups_by_department = []

    for department in departments:
        department_names.append(department.name)
        courses_by_department.append(
            Course.objects.filter(department=department).count()
        )
        groups_by_department.append(
            AcademicGroup.objects.filter(department=department).count()
        )

    context = {
        'total_courses': Course.objects.count(),
        'total_departments': Department.objects.count(),
        'total_groups': AcademicGroup.objects.count(),
        'department_names': department_names,
        'courses_by_department': courses_by_department,
        'groups_by_department': groups_by_department,
        'is_methodist': is_methodist(request.user),
    }

    return render(request, 'dashboard.html', context)