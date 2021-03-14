# install: pip install --upgrade arabic-reshaper
import arabic_reshaper

# install: pip install python-bidi
from bidi.algorithm import get_display

# install: pip install Pillow
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import textwrap

def write_into_instgram_image(text, text_size=0):
    # use a good font!
    fontFile = "media/instgram/fonts/t.ttf"

    # this was a 400x400 jpg file
    imageFile = "../media/instgram/post_image.png"
    font = ImageFont.truetype(fontFile, 50)
    font2 = ImageFont.truetype(fontFile, 30)
    image = Image.open(imageFile)
    text = text
    text_fixed = 'إستفسار جديد من المنصة'
    text_fixed2 = 'قم بزيارة المنصة وأعطي رأيك www.raykomfi.com'
    text = "\n".join(textwrap.wrap(text, width=30))
    reshaped_text_fixed = arabic_reshaper.reshape(text_fixed)    # correct its shape
    reshaped_text_fixed2 = arabic_reshaper.reshape(text_fixed2)
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)           # correct its direction
    bidi_text_fixed = get_display(reshaped_text_fixed)           # correct its direction
    bidi_text_fixed2 = get_display(reshaped_text_fixed2)


    W, H = (1000,840)



    # start drawing on image
    draw = ImageDraw.Draw(image)
    w, h = draw.textsize(text, font=font)
    draw.text((250,250), bidi_text_fixed, (255,255,0), font=font, align='center')
    if text_size > 30:
        draw.text((200,(H-h)/2), bidi_text, (255,255,255), font=font, align='center')
    else:
        draw.text(((W-w)/2,(H-h)/2), bidi_text, (255,255,255), font=font, align='center')
    draw.text((200,750), bidi_text_fixed2, (255,255,0), font=font2, align='center')
    draw = ImageDraw.Draw(image)
    image = image.convert('RGB')

    # save it
    image.save("media/instgram/generated_post_image/output.jpg")