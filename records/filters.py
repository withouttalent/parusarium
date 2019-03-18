from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
import datetime
from .models import Cities
from .models import *
try:
    import pytz
except ImportError:
    pytz = None

from collections import OrderedDict

from django import forms
from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.templatetags.static import StaticNode
from django.utils.translation import ugettext as _
from django.contrib.admin.widgets import AdminDateWidget, AdminSplitDateTime as BaseAdminSplitDateTime


class AdminSplitDateTime(BaseAdminSplitDateTime):
    def format_output(self, rendered_widgets):
        return format_html('<p class="datetime">{}</p><p class="datetime rangetime">{}</p>',
                           rendered_widgets[0],
                           rendered_widgets[1])


class DateRangeFilter(admin.filters.FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg_gte = '{}__gte'.format(field_path)
        self.lookup_kwarg_lte = '{}__lte'.format(field_path)

        super(DateRangeFilter, self).__init__(field, request, params, model, model_admin, field_path)
        self.request = request
        self.form = self.get_form(request)

    def get_timezone(self, request):
        return timezone.get_default_timezone()

    @staticmethod
    def make_dt_aware(value, timezone):
        if settings.USE_TZ and pytz is not None:
            default_tz = timezone
            if value.tzinfo is not None:
                value = default_tz.normalize(value)
            else:
                value = default_tz.localize(value)
        return value

    def choices(self, cl):
        yield {
            # slugify converts any non-unicode characters to empty characters
            # but system_name is required, if title converts to empty string use id
            # https://github.com/silentsokolov/django-admin-rangefilter/issues/18
            'system_name': slugify(self.title) if slugify(self.title) else id(self.title),
            'query_string': cl.get_query_string(
                {}, remove=self._get_expected_fields()
            )
        }

    def expected_parameters(self):
        return self._get_expected_fields()

    def queryset(self, request, queryset):
        if self.form.is_valid():
            validated_data = dict(self.form.cleaned_data.items())
            if validated_data:
                return queryset.filter(
                    **self._make_query_filter(request, validated_data)
                )
        return queryset

    def _get_expected_fields(self):
        return [self.lookup_kwarg_gte, self.lookup_kwarg_lte]

    def _make_query_filter(self, request, validated_data):
        query_params = {}
        date_value_gte = validated_data.get(self.lookup_kwarg_gte, None)
        date_value_lte = validated_data.get(self.lookup_kwarg_lte, None)

        if date_value_gte:
            query_params['{0}__gte'.format(self.field_path)] = self.make_dt_aware(
                datetime.datetime.combine(date_value_gte, datetime.time.min),
                self.get_timezone(request),
            )
        if date_value_lte:
            query_params['{0}__lte'.format(self.field_path)] = self.make_dt_aware(
                datetime.datetime.combine(date_value_lte, datetime.time.max),
                self.get_timezone(request),
            )

        return query_params

    def get_template(self):
        return 'rangefilter/date_filter.html'

    template = property(get_template)

    def get_form(self, request):
        form_class = self._get_form_class()
        return form_class(self.used_parameters)

    def _get_form_class(self):
        fields = self._get_form_fields()

        form_class = type(
            str('DateRangeForm'),
            (forms.BaseForm,),
            {'base_fields': fields}
        )
        form_class.media = self._get_media()
        # lines below ensure that the js static files are loaded just once
        # even if there is more than one DateRangeFilter in use
        request_key = 'DJANGO_RANGEFILTER_ADMIN_JS_SET'
        if (getattr(self.request, request_key, False)):
            form_class.js = []
        else:
            setattr(self.request, request_key, True)
            form_class.js = self.get_js()
        return form_class

    def _get_form_fields(self):
        return OrderedDict((
                (self.lookup_kwarg_gte, forms.DateField(
                    label='',
                    widget=AdminDateWidget(attrs={'placeholder': _('From date')}),
                    localize=True,
                    required=False
                )),
                (self.lookup_kwarg_lte, forms.DateField(
                    label='',
                    widget=AdminDateWidget(attrs={'placeholder': _('To date')}),
                    localize=True,
                    required=False
                )),
        ))

    @staticmethod
    def get_js():
        return [
            StaticNode.handle_simple('admin/js/calendar.js'),
            StaticNode.handle_simple('admin/js/admin/DateTimeShortcuts.js'),
        ]

    @staticmethod
    def _get_media():
        js = [
            'calendar.js',
            'admin/DateTimeShortcuts.js',
        ]
        css = [
            'widgets.css',
        ]
        return forms.Media(
            js=['admin/js/%s' % url for url in js],
            css={'all': ['admin/css/%s' % path for path in css]}
        )


class DateTimeRangeFilter(DateRangeFilter):
    def _get_expected_fields(self):
        expected_fields = []
        for field in [self.lookup_kwarg_gte, self.lookup_kwarg_lte]:
            for i in range(2):
                expected_fields.append('{}_{}'.format(field, i))

        return expected_fields

    def _get_form_fields(self):
        return OrderedDict((
                (self.lookup_kwarg_gte, forms.SplitDateTimeField(
                    label='',
                    widget=AdminSplitDateTime(attrs={'placeholder': _('From date')}),
                    localize=True,
                    required=False
                )),
                (self.lookup_kwarg_lte, forms.SplitDateTimeField(
                    label='',
                    widget=AdminSplitDateTime(attrs={'placeholder': _('To date')}),
                    localize=True,
                    required=False
                )),
        ))

    def _make_query_filter(self, request, validated_data):
        query_params = {}
        date_value_gte = validated_data.get(self.lookup_kwarg_gte, None)
        date_value_lte = validated_data.get(self.lookup_kwarg_lte, None)

        if date_value_gte:
            query_params['{0}__gte'.format(self.field_path)] = self.make_dt_aware(
                date_value_gte, self.get_timezone(request)
            )
        if date_value_lte:
            query_params['{0}__lte'.format(self.field_path)] = self.make_dt_aware(
                date_value_lte, self.get_timezone(request)
            )

        return query_params















class CitiesAllowedFilter(admin.SimpleListFilter):
    title = _('Ограничение региона')

    parameter_name = 'city_key__key'

    def lookups(self, request, model_admin):
        if request.user.allowed_region:
            city = Cities.objects.get(key=request.user.allowed_region)
            return ((city.key, city.name),)
        else:
            city_list = []
            cities = Cities.objects.all()
            for city in cities:
                city_list.append((city.key, city.name))
            return city_list

    def queryset(self, request, queryset):
        if request.user.allowed_region:
            return queryset.filter(city_key__key=request.user.allowed_region)
        elif self.value():
            return queryset.filter(city_key__key=self.value())
        else:
            return queryset





class SiteAllowedFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Ограничение ресурса')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'site'

    def lookups(self, request, model_admin):
        if request.user.allowed_site:
            if request.user.allowed_site == 'avito':
                return ('avito', _('Авито')),
            if request.user.allowed_site == 'cian':
                return ('cian', _('Циан')),
            if request.user.allowed_site == "n30":
                return ('n30', _('n30'))
            # if request.user.allowed_site == 'ngs':
            #     return ('ngs', _('ngs'))
        return (
            ('avito', _('Авито')),
            ('cian', _('Циан')),
            ('n30', _('n30')),
            # ('ngs', _('ngs')),
        )

    def queryset(self, request, queryset):
        if request.user.allowed_site:
            return queryset.filter(site=request.user.allowed_site)
        else:
            if self.value():
                return queryset.filter(site=self.value())



class AreaFilter(admin.SimpleListFilter):

        # super(AreaLteFilter).__init__(self, request, params, model, model_admin)
    template = 'filters/during.html'
    title = "Площадь"
    parameter_name = "area"
    def lookups(self, request, model_admin):
        return ((),)

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice

    def queryset(self, request, queryset):
        area_filter = dict()
        if self.value():
            area_filter['area__gte'], area_filter['area__lte'] = self.value().split(";")
            return queryset.filter(**area_filter)


class PriceFilter(admin.SimpleListFilter):
    template = 'filters/during.html'
    title = "Цена"
    parameter_name = "price_rub"

    def lookups(self, request, model_admin):
        return ((),)

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice

    def queryset(self, request, queryset):
        area_filter = dict()
        if self.value():
            area_filter['price_rub__gte'], area_filter['price_rub__lte'] = self.value().split(";")
            return queryset.filter(**area_filter)
