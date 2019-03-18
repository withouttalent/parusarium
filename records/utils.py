from PIL import ImageDraw
from PIL import Image
from PIL import ImageFont


def watermark_text(input_image_path,
                   output_image_path,
                   text, pos):
    photo = Image.open(input_image_path)
    drawing = ImageDraw.Draw(photo)
    black = (3, 8, 12)
    font = ImageFont.truetype("/home/workspace/Documents/Roboto-Regular.ttf", 16)
    drawing.text(pos, text, font=font, fill=black)
    drawing.text(pos, text, fill=black, font=font)
    photo.save(output_image_path)


if __name__ == '__main__':
    img = '/home/workspace/Downloads/2c858a7992ec4a9388af3bf8d9f6818f.jpg'
    watermark_text(img, f'/home/workspace/PycharmProjects/watermark2.jpg',
                   text=f'''
Дата обращения к странице сайта: {date_added}
URL: https://irkutsk.cian.ru/sale/suburban/196362298/
''',
                   pos=(10, 180))