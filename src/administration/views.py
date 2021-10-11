from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, UpdateView

from src.accounts.models import User

allowed_decorators = [login_required, user_passes_test(lambda u: u.is_superuser)]


@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'administration/dashboard.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        user_total = User.objects.all().count()
        user_admins = User.objects.filter(is_staff=True, is_superuser=True).count()
        user_customers = User.objects.filter(is_staff=False, is_superuser=False).count()
        user_unpaid = User.objects.filter(is_staff=False, is_superuser=False, is_paid=False).count()
        user_paid = User.objects.filter(is_staff=False, is_superuser=False, is_paid=True).count()

        data['user_total'] = user_total
        data['user_admins'] = user_admins
        data['user_customers'] = user_customers
        data['user_unpaid'] = user_unpaid
        data['user_paid'] = user_paid

        return data


""" USERS """


@method_decorator(login_required, name='dispatch')
class UserListView(ListView):
    model = User
    paginate_by = 20
    template_name = 'administration/user_list.html'

    def get_queryset(self):
        return User.objects.exclude(Q(is_staff=True) | Q(is_superuser=True))


@method_decorator(login_required, name='dispatch')
class UserDetailView(DetailView):
    model = User
    template_name = 'administration/user_detail.html'


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = [
        'first_name', 'last_name',
        'email', 'username', 'phone_number', 'bio', 'about',
        'interests', 'matching', 'gender', 'interested_lower_age',
        'interested_upper_age', 'interested_in_gender', 'address', 'is_identified'
    ]
    template_name = 'administration/user_update_form.html'

    def get_success_url(self):
        return reverse('admins:user-detail', kwargs={'pk': self.object.pk})


@method_decorator(login_required, name='dispatch')
class UserPasswordResetView(View):

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = AdminPasswordChangeForm(user=user)
        return render(request, 'administration/admin_password_reset.html', {'form': form})

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = AdminPasswordChangeForm(data=request.POST, user=user)
        if form.is_valid():
            form.save(commit=True)
            messages.success(request, f"{user.get_full_name()}'s password changed successfully.")
        return render(request, 'administration/admin_password_reset.html', {'form': form})

