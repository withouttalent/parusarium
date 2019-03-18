from django.contrib import admin
from .models import *
from .filters import SiteAllowedFilter, DateRangeFilter, AreaFilter, PriceFilter, CitiesAllowedFilter
from django.utils.html import mark_safe
from datetime import datetime
from django.db import connections
from django.db.models import Count, Sum, Q
from .tasks import create_excel, create_zip
from django.contrib.auth.admin import GroupAdmin, Group


admin.AdminSite.site_title = "Парусариум"
admin.AdminSite.site_header = "Парусариум"
admin.AdminSite.index_title = ""
admin.AdminSite.empty_value_display = "Информация отсутствует"


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('id_file', 'date_added', 'is_manual', 'source_date_added', 'phone_number', 'price_rub', 'area', 'handled_text')
    fieldsets = (
        (None, {
            'fields': (('date_added', 'date_updated', 'source_date_added'),)
        }),
        ("Информация из объявления", {
           'fields': (('raw_price', 'raw_area', 'phone_number'),
                      ('source_url', 'site', 'cadastre_number'),
                      ('city_key',),
                      ('raw_text', 'raw_address'),
                      ('address_info',))
        }),
        ("Условия", {
            'fields': (('state_electricity', 'state_cold_water', 'state_hot_water'),
                       ('state_gas', 'state_heating', 'state_sewage'),
                       ('ownership_rights', 'usage_allowed'),)
        }),
        ("Скриншоты", {
            'fields': ("main_image",)
        })
    )
    show_full_result_count = False
    date_hierarchy = 'date_added'
    change_form_template = 'admin/records/change_form.html'
    list_filter = ('usage_allowed__name',
                   ('date_added', DateRangeFilter),
                   ('source_date_added', DateRangeFilter),
                   SiteAllowedFilter, AreaFilter,
                   PriceFilter, CitiesAllowedFilter)
    readonly_fields = ("main_image",)
    actions = ["download_excel", "import_zip"]

    def handled_text(self, obj):
        if len(obj.raw_text) > 30:
            return f"{obj.raw_text[:30]}..."
        elif len(obj.raw_text) >= 30:
            return obj.raw_text
        else:
            return
    handled_text.short_description = "Текст объявления"

    def save_model(self, request, obj, form, change):
        obj.is_manual = True
        obj.save()


    def id_file(self, obj):
        return mark_safe(f'<a target="_blank" href="{obj.id}/change">{obj.id}</a>')


    def main_image(self, obj):
        img = obj.get_file()
        if img:
            return mark_safe(f'<img src="https://parusarium.ru/ftp/{img}" />')
    main_image.short_description = "Скриншот"


    def get_queryset(self, request):
        qs = super(RecordAdmin, self).get_queryset(request)
        context = dict()
        if request.user.allowed_region:
            context['city_key__key'] = request.user.allowed_region
        if request.user.allowed_site:
            context['site'] = request.user.allowed_site
        return qs.filter(**context)

    def get_actions(self, request):
        actions = super(RecordAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


    def download_excel(self, request, queryset):
        self.message_user(request, "Данные приняты в обработку и будут доступны в разделе Файлы пользователя")
        records = list(queryset.values_list("id",))
        records_list = []
        for i in records:
            records_list += i
        create_excel.delay(self.model._meta.model_name, records_list, request.user.id)
    download_excel.short_description = "Импортировать выбранные объекты в Excel"


    def import_zip(self, request, queryset):
        records = list(queryset.values_list("id", ))
        records_list = []
        for i in records:
            records_list += i
        create_zip.delay(self.model._meta.model_name, records_list, request.user.id)
        self.message_user(request, "Данные приняты в обработку и будут доступны в разделе Файлы пользователя")
    import_zip.short_description = "Импортировать в zip"




@admin.register(RecordOks)
class RecordOksAdmin(RecordAdmin):

    def save_model(self, request, obj, form, change):
        record = RecordOks.objects.get(id=obj.id)
        if record.is_manual == obj.is_manual:
            obj.is_manual.save()

@admin.register(RecordStatic)
class RecordStaticAdmin(admin.ModelAdmin):
    change_list_template = "admin/records/statistics.html"

    def namedfetch(self, retrived_data):
        context = []
        for data in retrived_data:
            context.append({
                "city": data[0],
                "pk_sum": data[1],
                "avito_sum": data[2],
                "cian_sum": data[3],
                "n30_sum": data[4]
            })
        return context

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        with connections["records_db"].cursor() as cursor:
            cursor.execute("""SELECT city_key, COUNT(id), COUNT(id) FILTER(where site='avito'),
             COUNT(id) FILTER(where site='cian'), COUNT(id) FILTER(WHERE site='n30') from records
              group by records.city_key""")
            records_data = cursor.fetchall()
            cursor.execute("""SELECT city_key, COUNT(id), COUNT(id) FILTER(where site='avito'),
             COUNT(id) FILTER(where site='cian'), COUNT(id) FILTER(WHERE site='n30') from recordsoks
              group by recordsoks.city_key""")
            recordsoks_data = cursor.fetchall()
        records = self.namedfetch(records_data)
        recordsoks = self.namedfetch(recordsoks_data)
        response.context_data["records"] = records
        response.context_data["recordsoks"] = recordsoks
        return response



admin.site.register(Cities)
admin.site.register(Files)
admin.site.register(Filesoks)
