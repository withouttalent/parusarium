from django import forms
from user_profile.models import *
from records.models import Cities


class UserAllowForm(forms.ModelForm):
    class ModelChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, obj):
            return obj.key
    sites = (
        ('', '-------'),
        ('avito', 'Авито'),
        ('cian', 'Циан'),
    )
    allowed_region = ModelChoiceField(queryset=Cities.objects.all(), to_field_name='key', required=False)
    allowed_site = forms.ChoiceField(choices=sites, required=False)


