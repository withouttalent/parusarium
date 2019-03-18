from celery import shared_task
from .models import Record, RecordOks
from user_profile.models import UserFiles, User
import xlwt
from datetime import datetime
import os
import zipfile
from django.utils import timezone
from PIL import ImageDraw, Image, ImageFont
from django.contrib.contenttypes.models import ContentType
import time
import uuid


@shared_task
def create_excel(model, records_id, request_id):
    if model == "record":
        records = Record.objects.filter(id__in=records_id)
    elif model == "recordoks":
        records = RecordOks.objects.filter(id__in=records_id)
    user = User.objects.get(pk=request_id)
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Выборка')
    ws.col(0).width = 256 * 36
    ws.col(3).width = 256 * 22
    ws.col(6).width = 256 * 18
    ws.col(8).width = 256 * 12
    ws.col(9).width = 256 * 32
    ws.col(10).width = 256 * 12
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Дата размещение объявления', 'Цена', 'Площадь', 'Кадастровый номер', 'Адрес', 'Описание',
               'Номер телефона', 'Сайт', 'URL', 'Дата обращение к странице сайта', 'Скриншоты']
    for i, column in enumerate(columns):
        ws.write(row_num, i, column, font_style)
    columns = ['DEAL_DATE', 'DEAL_PRICE', 'VALUE', 'CADASTRAL_NUMBER', 'REGION']
    row_num += 1
    for i, column in enumerate(columns):
        ws.write(row_num, i, column, font_style)
    for record in records:
        row_num += 1
        if record.date_added:
            date_added = datetime.strftime(record.date_added, "%Y-%m-%d")
        else:
            date_added = ""
        if record.source_date_added:
            source_date_added = datetime.strftime(record.source_date_added, "%Y-%m-%d")
        else:
            source_date_added = ""
        file = record.get_file()
        if file:
            file = file.split("/")[-1]
        record_list = [source_date_added, str(record.price_rub).replace(".", ","), str(record.area).replace(".", ","),
                       record.cadastre_number,
                       record.raw_address, record.raw_text,
                       record.phone_number, record.site, record.source_url, date_added, file]
        for index, record_write in enumerate(record_list):
            ws.write(row_num, index, record_write)
    path = f"ziparchive/{records.count()}_{timezone.now()}.xls"
    wb.save(os.path.abspath(path))
    user_file = UserFiles.objects.create(user=user,
                                         date_create=timezone.now(),
                                         is_active=True,
                                         count_files=records.count(),
                                         status="Готово",
                                         file=f"ziparchive/{path.split('/')[-1]}",
                                         date_expired=timezone.now()+timezone.timedelta(days=1))


class ZipFlow:
    def __init__(self, model, records_id, request_id):
        self.model = ContentType.objects.get(model=model).model_class()
        self.records = self.model.objects.filter(id__in=records_id)
        self.user = User.objects.get(pk=request_id)
        self.user_file = UserFiles.objects.create(user=self.user, date_create=timezone.now(),
                                                  date_expired=timezone.now() + timezone.timedelta(days=1),
                                                  count_files=self.records.count())
        self.zipfile = zipfile.ZipFile(self.name_generator(), 'w')
        self.text_template = 'АС "ПАРУС". Дата обращения к странице сайта: {date}\nURL: {source_url}'

    def watermark_text(self, input_image_path, text):
        photo = Image.open(input_image_path)
        drawing = ImageDraw.Draw(photo)
        black = (3, 8, 12)
        font = ImageFont.truetype("static/parusarium/fonts/Roboto-Medium.ttf", 16)
        drawing.text((10, 180), text, fill=black, font=font)
        index = str(uuid.uuid4())
        file = f'ziparchive/trash/{index}.' + photo.format.lower()
        photo.save(file, photo.format)
        return file

    def _name_generator(self, name):
        while True:
            if os.path.exists(name):
                _name = name.split('.')[0]
                timestamp = str(time.time()).split('.')[-1]
                name = f'{_name}_{timestamp}.zip'
            else:
                self.user_file.file = name
                self.user_file.save()
                return name

    def name_generator(self):
        cities = self.records.values_list('city_key__name').distinct('city_key__name')
        cities_name = [city[0] for city in cities]
        name = f'ziparchive/{"_".join(cities_name)}_{self.records.count()}.zip'
        return self._name_generator(name)

    def create(self):
        for i, record in enumerate(self.records):
            self.user_file.status = f"загружено {i} из {self.records.count()}"
            self.user_file.save()
            file = record.get_file()
            file = f"/mnt/ftp/{file}"
            if os.path.exists(file) and os.path.isfile(file):
                text = self.text_template.format(date=record.date_added.strftime("%Y-%m-%d %H:%M:%S"),
                                                 source_url=record.source_url)
                file_stamp = self.watermark_text(file, text)
                self.zipfile.write(file_stamp, file.split("/")[-1], compress_type=zipfile.ZIP_DEFLATED)
                os.remove(file_stamp)
        self.user_file.status = "Готово"
        self.user_file.save()
        self.zipfile.close()


@shared_task
def create_zip(model, records_id, request_id):
    zip = ZipFlow(model, records_id, request_id)
    zip.create()


@shared_task
def fluud():
    files = UserFiles.objects.all()
    if files.exists():
        for file in files:
            if timezone.now() >= file.date_expired:
                if file.file:
                    path_to_file = os.path.abspath(file.file)
                    if os.path.exists(path_to_file):
                        os.remove(path_to_file)
                file.delete()

