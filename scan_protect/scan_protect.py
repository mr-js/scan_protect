from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
import re
import sys


# working directory
PATH = os.getcwd()
# command line argument #1


def filename_check(filename):
    for c in r'\/:*?"<>|':
        filename = filename.replace(c, ' ')
    filename = filename.replace('\n', ' ')
    filename = re.sub(' +', ' ', filename).strip()
    return filename


def create_watermark(text, size):
    watemark_text = text
    watemark_density = 32
    watemark_image_resolution = 8000
    watemark_image_size = (watemark_image_resolution, watemark_image_resolution)
    watemark_image = Image.new('RGBA', watemark_image_size, (255,255,255,0))
    watemark_draw = ImageDraw.Draw(watemark_image)
    watemark_font_size = int(size)
    watemark_font = ImageFont.truetype('font.ttf', watemark_font_size)
    watemark_text_size = ImageDraw.Draw(Image.new('RGB', (watemark_image_resolution, watemark_image_resolution))).multiline_textbbox((0, 0), watemark_text, watemark_font)[2:4]
    offset_x = watemark_image_size[0]//watemark_density
    offset_y = watemark_image_size[1]//watemark_density
    start_x = watemark_image_size[0]//watemark_density - watemark_text_size[0]//2
    start_y = watemark_image_size[1]//watemark_density - watemark_text_size[1]//2
    for a in range(0, watemark_density, 2):
        for b in range(0, 2*watemark_density, 2):
            x = start_x + a*offset_x//2
            y = start_y + b*offset_y//2
            watemark_draw.multiline_text((x, y), watemark_text, (0, 0, 0, 64), font=watemark_font)
    watemark_image = watemark_image.rotate(-45, expand=True, fillcolor=(0,0,0,0))
    return watemark_image, watemark_image_size


def combine_watemark(file, watemark):
    watemark_image, watemark_image_size = watemark
    file_name, file_ext = os.path.splitext(file)
    original_image = Image.open(file).convert("RGBA")
    original_image_size = original_image.size
    temp_image = Image.new('RGBA', original_image_size, (255,255,255,0))
    temp_image.paste(watemark_image, (-watemark_image_size[0]//2, -watemark_image_size[1]//2))
    combined_image = Image.alpha_composite(original_image, temp_image)
    return combined_image.convert('RGB')


def scan_protect(title = '', subject = '', destination = '', date = '', size = ''):
    if date == '':
        date = str(datetime.today().strftime('%d.%m.%Y'))
    if size == '':
        size = 32
    text = f"""\
    {title}
    Subject: {subject}
    To: {destination}
    Date: {date}\
    """
    watermark = create_watermark(text, size)
    imagelist = []
    for file in os.listdir(PATH):
        if os.path.isfile(os.path.join(PATH, file)):
            name, ext = os.path.splitext(os.path.join(PATH, file))
            if ext.lower() == '.jpg' or ext.lower() == '.png' or ext.lower() == '.bmp':
                print(f'{file}')
                imagelist.append(combine_watemark(os.path.join(PATH, file), watermark))
    pdf_title = f'{subject} ({destination}, {date}) - {title}'
    pdf_subject = f'{subject} ({destination}, {date})'
    pdf_filename = f'{filename_check(pdf_title)}'
    imagelist[0].save(os.path.join(PATH, f'{pdf_filename}.pdf'), save_all=True, append_images=imagelist[1:], title = pdf_title, subject=pdf_subject)
    print(pdf_filename)
    if not os.path.isdir(os.path.join(PATH, pdf_filename)):
        os.mkdir(os.path.join(PATH, pdf_filename))
    image_counter = 0
    for image in imagelist:
        image_counter += 1
        image.save(os.path.join(PATH, pdf_filename, f'{image_counter}.jpg'))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        PATH = sys.argv[1]
    while (True):
        print(f'\ndocuments path: {PATH}\n')
        destination = input('destination organization for documents:\n')
        date = input('date (press Enter to set current date):\n')
        title = input('title (press Enter to set default title):\n')
        subject = input('subject (press Enter to set default subject):\n')
        size = input('size (press Enter to set default size):\n')
        scan_protect(title, subject, destination, date, size)
