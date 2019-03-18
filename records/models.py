from django.db import models
from django.utils.translation import ugettext_lazy as _

class CatalogRealty(models.Model):
    id = models.BigAutoField(primary_key=True)
    realty = models.CharField(max_length=100)
    url_realty = models.CharField(max_length=1000)
    cities_key = models.ForeignKey('Cities', models.DO_NOTHING, db_column='cities_key')
    site = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'catalog_realty'


class Cities(models.Model):
    key = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'cities'
        verbose_name = "Город"
        verbose_name_plural = "Города"


class CommunicationStateKinds(models.Model):
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name if self.name else None

    class Meta:
        managed = False
        db_table = 'communication_state_kinds'


class AbstractFile(models.Model):
    id = models.BigAutoField(primary_key=True)
    hash = models.CharField(max_length=100)
    source_url = models.CharField(max_length=1000)
    date_added = models.DateTimeField()
    key = models.CharField(max_length=500)
    size = models.BigIntegerField()
    server_key = models.CharField(max_length=100)
    record_id = models.BigIntegerField()
    kind = models.IntegerField()

    class Meta:
        abstract = True
        managed = False

class Files(AbstractFile):

    class Meta:
        managed = False
        db_table = 'files'
        verbose_name = "Файл земельного участка"
        verbose_name_plural = "Файлы земельных участков"


class Filesoks(AbstractFile):

    class Meta:
        managed = False
        db_table = 'filesoks'
        verbose_name_plural = "Файлы объектов капитального строительства"
        verbose_name = "Файл объекта капитального строительства"


class AbstractRecord(models.Model):
    id = models.BigAutoField(primary_key=True)
    date_added = models.DateTimeField(_('Дата парсинга'))
    date_updated = models.DateTimeField(_('Дата обновления'))
    is_parsed = models.BooleanField()
    is_valid = models.BooleanField(blank=True, null=True)
    city_key = models.ForeignKey(Cities, models.DO_NOTHING, verbose_name="Город", db_column='city_key')
    source_url = models.CharField(_('Ссылка на объявление'), max_length=2000)
    raw_price = models.CharField(_("Цена из объявления"), max_length=500, blank=True, null=True)
    raw_area = models.CharField(_("Площадь из объявления"), max_length=500, blank=True, null=True)
    raw_text = models.TextField(_("Описание из объявления"), blank=True, null=True)
    raw_address = models.TextField(_("Адрес из объявления"), blank=True, null=True)
    raw_hash = models.CharField(max_length=100, blank=True, null=True)
    source_date_added = models.DateField(_("Дата размещения"), blank=True, null=True)
    price_rub = models.DecimalField(_("Цена в рублях"), max_digits=18, decimal_places=2, blank=True, null=True)
    area = models.DecimalField(_("Площадь кв.м."), max_digits=18, decimal_places=4, blank=True, null=True)
    address_info = models.TextField(_("Адрес"), blank=True, null=True)
    cadastre_number = models.CharField(_("Кадастровый номер"), max_length=50, blank=True, null=True)
    communications = models.TextField(_("Коммуникации"), blank=True, null=True)
    phone_number = models.CharField(_("Номер телефона"), max_length=50)
    is_manual = models.BooleanField(_('Руч. прав.'), blank=True, null=True)
    state_electricity = models.ForeignKey(CommunicationStateKinds,
                                          models.DO_NOTHING, verbose_name="Электричество",
                                          db_column='state_electricity',
                                          related_name="%(app_label)s_%(class)s_state_electricity", blank=True, null=True)
    state_cold_water = models.ForeignKey(CommunicationStateKinds,
                                         models.DO_NOTHING, verbose_name="Холодная вода",
                                         db_column='state_cold_water',
                                         related_name='%(app_label)s_%(class)s_state_cold_water', blank=True, null=True)
    state_hot_water = models.ForeignKey(CommunicationStateKinds,
                                        models.DO_NOTHING, verbose_name="Горячая вода",
                                        db_column='state_hot_water',
                                        related_name='%(app_label)s_%(class)s_state_hot_water', blank=True, null=True)
    state_gas = models.ForeignKey(CommunicationStateKinds,
                                  models.DO_NOTHING, verbose_name="Газ",
                                  db_column='state_gas',
                                  related_name='%(app_label)s_%(class)s_state_gas', blank=True, null=True)
    state_heating = models.ForeignKey(CommunicationStateKinds,
                                      models.DO_NOTHING, verbose_name="Отопление",
                                      db_column='state_heating',
                                      related_name='%(app_label)s_%(class)s_state_heating', blank=True, null=True)
    state_sewage = models.ForeignKey(CommunicationStateKinds,
                                     models.DO_NOTHING, verbose_name="Канализация",
                                     db_column='state_sewage',
                                     related_name='%(app_label)s_%(class)s_state_sewage', blank=True, null=True)
    condition = models.TextField(_("Условия"), blank=True, null=True)
    usage_allowed = models.ForeignKey('UsageKinds',
                                      models.DO_NOTHING, verbose_name="Разрешенное использование",
                                      db_column='usage_allowed',
                                      related_name='%(app_label)s_%(class)s_usage_allowed', blank=True, null=True)
    usage_actual = models.ForeignKey('UsageKinds',
                                     models.DO_NOTHING,
                                     db_column='usage_actual',
                                     related_name='%(app_label)s_%(class)s_usage_actual', blank=True, null=True)
    ownership_rights = models.ForeignKey('RightsKinds',
                                         models.DO_NOTHING, verbose_name="Права на использования",
                                         db_column='ownership_rights',
                                         related_name='%(app_label)s_%(class)s_ownership_rights', blank=True, null=True)
    site = models.CharField(_('Сайт'), max_length=50, blank=True, null=True)


    class Meta:
        abstract = True
        managed = False




class Record(AbstractRecord):
    price_usd = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    price_recurrence = models.IntegerField(blank=True, null=True)
    kladr = models.CharField(max_length=50, blank=True, null=True)
    locality = models.CharField(max_length=500, blank=True, null=True)
    district = models.CharField(max_length=500, blank=True, null=True)
    official_address = models.CharField(max_length=2000, blank=True, null=True)


    def get_file(self):
        try:
            file = Files.objects.get(record_id=self.id, kind=1)
            url = f"{self.site}/{self.city_key.key}/ZU/{file.key}"
            return url
        except self.DoesNotExist:
            pass

    class Meta:
        managed = False
        db_table = 'records'
        verbose_name_plural = 'Земельные участки'
        verbose_name = 'Земельный участок'

class RecordOks(AbstractRecord):


    def get_file(self):
        try:
            file = Filesoks.objects.get(record_id=self.id, kind=1)
            if self.usage_actual:
                if self.usage_actual.id == 9:
                    prefix = "KVARTIRA"
                else:
                    prefix = "OKS"
                url = f"{self.site}/{self.city_key.key}/{prefix}/{file.key}"
                return url
        except self.DoesNotExist:
            pass

    class Meta:
        managed = False
        db_table = 'recordsoks'
        verbose_name_plural = 'Объекты недвижимости'
        verbose_name = 'Объект недвижимости'


class RightsKinds(models.Model):
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'rights_kinds'


class SpiderUpdates(models.Model):
    id = models.BigAutoField(primary_key=True)
    version = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    hash = models.CharField(max_length=200)
    size = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'spider_updates'


class UsageKinds(models.Model):
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'usage_kinds'
        verbose_name = _('Разрешенное использование')
        verbose_name_plural = _('Разрешенное использование')


class RecordStatic(Record):

    class Meta:
        proxy = True
        verbose_name = _("Общая статистика")
        verbose_name_plural = _("Общая статистика")