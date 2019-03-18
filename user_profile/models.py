from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.core.mail import send_mail
from records.models import Record, RecordOks
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models.signals import pre_delete
import os

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)





class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    allowed_region = models.CharField(max_length=120, blank=True, null=True)
    allowed_site = models.CharField(max_length=200, blank=True, null=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class RecordAnalytics(Record):

    class Meta:
        proxy = True
        verbose_name_plural = verbose_name = 'Выгрузка данных'
        app_label = 'records'


class UserFiles(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.CharField(_("Файл"), blank=True, max_length=380, null=True)
    count_files = models.IntegerField(_("Кол-во файлов"), blank=True, null=True)
    status = models.CharField(_("Статус"), max_length=240, blank=True, null=True)
    is_active = models.BooleanField(_("Активность"), default=False)
    date_create = models.DateTimeField(_("Дата создания"), blank=True, null=True)
    date_expired = models.DateTimeField(_("Дата удаления"), blank=True, null=True)


    class Meta:
        db_table = 'UserFiles'
        verbose_name = 'Файл Пользователя'
        verbose_name_plural = "Файлы Пользователя"


def delete_user_files(sender, instance, **kwargs):
    if instance.file:
        path = os.path.abspath(instance.file)
        if os.path.exists(path):
            os.remove(path)


pre_delete.connect(delete_user_files, sender=UserFiles)
