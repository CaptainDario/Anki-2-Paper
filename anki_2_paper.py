from typing import List, Tuple
import random
import math

from PIL import Image, ImageFont, ImageDraw, ImageChops
import ankipandas
from ankipandas import Collection



collection_path = r"C:\Users\dario\AppData\Roaming\Anki2"
user_name = "User 1"
deck_name = r"Sprachen\x1fSpanisch\x1fSpanisch Vokabeln"
print_tag = "print"
output_file = "out"

inch = 25.4
scale = 300
a4 = (math.ceil(297 * scale / inch), math.ceil(210 * scale / inch))
a8 = (int(math.ceil(74 * scale / inch)), math.ceil(52 * scale / inch)) 



def trim(im : Image, col : Tuple[int, int, int]) -> Image:
    """ Trims an image by removing borders which have the given color `col`

    Args:
        im  : The image from which the borders should be trimmed
        col : the color which should be trimmed away from the borders of the image

    Returns:
        The trimmed image
    """

    bg = Image.new(im.mode, im.size, col)
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""

    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def get_text_dimensions(text_string : str, font : ImageFont) -> Tuple[int, int]:
    """ Calculates and returns the size of the given string while using the given font when rendered.
    source: https://stackoverflow.com/a/46220683/9263761

    Args:
        text_string : the string to render
        font        : the font used to render `text_string`

    Returns:
        A Tuple (width, height) of the rendered text
    """
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)


def break_text_in_two_lines(text : str, font : ImageFont, w : int) -> str:
    """ breaks the given text in two lines with maximum wdith `w`

    Args:
        text : the text which should be broken in two lines
        font : the font which should be used for width calculation
        w    : the maximum width the text should use for one line

    Returns:

    """
                
    l_t_1, l_t, cnt = text[0], "", 1

    while(cnt < len(text) and get_text_dimensions(l_t_1 + text[cnt], font)[0] < w):
        l_t_1 += text[cnt]
        cnt += 1
    l_t = l_t_1 + "\n"
    
    if(cnt < len(text)):
        l_t_2 = "" 
        while(cnt < len(text) and get_text_dimensions(l_t_2 + text[cnt], font)[0] < w):
            l_t_2 += text[cnt]
            cnt += 1
        l_t += l_t_2

    return l_t


def put_notes_on_flashcard(notes : List[Tuple[str, str]]) -> Image:
    """ Writes all Tuples of `notes` on an A4 sized image while laying them out on A8 sub images. 

    Args:
        notes : A List of Tuples with the word and its translation to be written on a flash card
        
    Returns:
        The PIL.Image with the flashcards written on it.
    """

    img = Image.new("RGB", (a4[0], a4[1]), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    c = 0
    for x in range(4):
        for y in range(4):
            # draw A8 card frame
            x_1, y_1 = a8[0] * x, a8[1] * y
            x_2, y_2 = a8[0] * (x+1), a8[1] * (y+1)
            draw.rectangle((x_1, y_1, x_2, y_2), outline=(0, 0, 0), width=4)

            h, w = a8[1] / 5, a8[0] // 2
            
            # draw lines to separate vocabulary horizontaly on one card
            for l in range(5):
                draw.line((x_1, y_1 + h * (l + 1), x_2, y_1 + h * (l + 1)), "black", width=2)
                    
                # get the text which should be written on the cards
                l_text = notes[c][0] if  c < len(notes) else "-"
                r_text = notes[c][1] if c < len(notes) else "-"

                # assure that the text is not too big for a card
                font = ImageFont.truetype("Noto_Sans_JP/NotoSansJP-Black.otf", 50)
                l_t, r_t = break_text_in_two_lines(l_text, font, w), break_text_in_two_lines(r_text, font, w)

                # write vocabulary
                draw.text((x_1 + 5, y_1 + h * l - 10), l_t, (0, 0, 0), font=font)
                draw.text((x_1 + w + 5, y_1 + h * l - 10), r_t, (0, 0, 0), font=font)

                c += 1
            
            # draw lines to separate vocabulary verticaly on one card
            draw.line(
                (x_1 + w, y_1,
                 x_1 + w, y_1 + a8[1]
                ), "black", width=2)
    
    img = trim(img, (255, 255, 255))
    return img



if __name__ == "__main__":

    ankipandas.set_debug_log_level()
    col = Collection(collection_path, user=user_name)
    cards = col.cards.merge_notes()
    cards["cdeck"].unique()
    #notes_from_deck = cards.query(f"cdeck == '{deck_name}'")
    notes_from_deck = cards.query(r"cdeck == 'Sprachen\x1fSpanisch\x1fSpanisch Vokabeln'")
   
    # get all notes which have the tag 'print'
    notes = notes_from_deck[["nflds", "ntags"]]
    filtered = [note for tags, note in zip(notes["ntags"], notes["nflds"]) if print_tag in tags]

    if(len(filtered) == 0):
        raise Exception(f"There are no notes marked with the tag: '{print_tag}'. Only notes with this tag will be used for creating flash cards!")

    for c, f in enumerate(list(chunks(filtered, 5*4*4))):
        img = put_notes_on_flashcard(f)
        img.save(f"{output_file}{str(c)}.png")