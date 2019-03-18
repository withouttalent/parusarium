from django.contrib import admin
from .models import User, UserFiles, RecordAnalytics
from django.utils.translation import  gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from .forms import UserAllowForm
from django.utils.html import mark_safe


class UserFilesInline(admin.TabularInline):
    model = UserFiles
    exclude = ('status', 'is_active')
    extra = 0


@admin.register(RecordAnalytics)
class RecordAnalyticsAdmin(admin.ModelAdmin):
    change_list_template = 'admin/user_profile/analytics.html'
    list_max_show_all = 999999

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        return response


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = UserAllowForm
    inlines = [UserFilesInline, ]
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('allowed_region', 'allowed_site', 'is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    def save_model(self, request, obj, form, change):
        if request.POST:
            if "allowed_region" in request.POST:
                if request.POST['allowed_region']:
                    obj.allowed_region = request.POST['allowed_region']
            obj.save()


@admin.register(UserFiles)
class UserFilesAdmin(admin.ModelAdmin):
    list_display = ('get_link_file', 'count_files', 'status', 'date_create', 'date_expired')
    readonly_fields = ('get_link_file',)
    list_display_links = ()


    def get_queryset(self, request):
        qs = super(UserFilesAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


    def get_link_file(self, obj):
        file = obj.file
        if file:
            return mark_safe(f'<a href="https://parusarium.ru/{file}">{file.split("/")[-1]}</a>')
        else:
            return mark_safe('<span>-</span>')
