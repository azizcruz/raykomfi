# install: pip install --upgrade arabic-reshaper
import arabic_reshaper

# install: pip install python-bidi
from bidi.algorithm import get_display

# install: pip install Pillow
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import textwrap

def write_into_instgram_image(text):
    # use a good font!
    fontFile = "media/instgram/fonts/t.ttf"

    # this was a 400x400 jpg file
    imageFile = "media/instgram/post_image.png"
    font = ImageFont.truetype(fontFile, 50)
    image = Image.open(imageFile)
    text = text
    text = "\n".join(textwrap.wrap(text, width=40))
    reshaped_text = arabic_reshaper.reshape(text)    # correct its shape
    bidi_text = get_display(reshaped_text)           # correct its direction

    W, H = (1000,840)

    

    # start drawing on image
    draw = ImageDraw.Draw(image)
    w, h = draw.textsize(text, font=font)
    draw.text((80,(H-h)/2), bidi_text, (255,255,255), font=font, align='center')
    draw = ImageDraw.Draw(image)

    # save it
    image.save("media/instgram/output.png")