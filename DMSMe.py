#!/usr/bin/python

from PIL import Image, ImageFont, ImageDraw
from numpy import linalg, array
import requests
import random
import json
import sys
import traceback
from io import BytesIO
from os import environ
from keys import keys


class Sign(object):
    def __init__(self, path, size, coords, font, fontSize, pad):
        self.path = path
        self.size = size
        self.coords = coords
        self.font = ImageFont.truetype(font, fontSize)
        self.fontSize = fontSize
        self.pad = pad


# signs  - image path, coords, font path, size,
signs = { 0:Sign("signs/0.JPG", (3,20), ((218,126),(541,120),(542,181),(219,186)), "Fonts/bold_led_board-7.ttf", 21, 3),
          1:Sign("signs/1.JPG", (3,20), ((677,216),(1578,210),(1580,403),(680,407)), "Fonts/bold_led_board-7.ttf", 50, 10),
          2:Sign("signs/2.jpg", (3,20), ((936,536),(2391,557),(2394,865),(926,845)), "Fonts/enhanced_led_board-7.ttf", 80, 30),
        }



def get_transform_data(pts8, backward=True ):
    '''This method returns a perspective transform 8-tuple (a,b,c,d,e,f,g,h).

    Use to transform an image:
    X = (a x + b y + c)/(g x + h y + 1)
    Y = (d x + e y + f)/(g x + h y + 1)

    Image.transform: Use 4 source coordinates, followed by 4 corresponding
        destination coordinates. Use backward=True (the default)

    To calculate the destination coordinate of a single pixel, either reverse
        the pts (4 dest, followed by 4 source, backward=True) or use the same
        pts but set backward to False.

    @arg pts8: four source and four corresponding destination coordinates
    @kwarg backward: True to return coefficients for calculating an originating
        position. False to return coefficients for calculating a destination
        coordinate. (Image.transform calculates originating position.)
    '''
    assert len(pts8) == 8, 'Requires a tuple of eight coordinate tuples (x,y)'

    b0,b1,b2,b3,a0,a1,a2,a3 = pts8 if backward else pts8[::-1]

    # CALCULATE THE COEFFICIENTS
    A = array([[a0[0], a0[1], 1,     0,     0, 0, -a0[0]*b0[0], -a0[1]*b0[0]],
               [    0,     0, 0, a0[0], a0[1], 1, -a0[0]*b0[1], -a0[1]*b0[1]],
               [a1[0], a1[1], 1,     0,     0, 0, -a1[0]*b1[0], -a1[1]*b1[0]],
               [    0,     0, 0, a1[0], a1[1], 1, -a1[0]*b1[1], -a1[1]*b1[1]],
               [a2[0], a2[1], 1,     0,     0, 0, -a2[0]*b2[0], -a2[1]*b2[0]],
               [    0,     0, 0, a2[0], a2[1], 1, -a2[0]*b2[1], -a2[1]*b2[1]],
               [a3[0], a3[1], 1,     0,     0, 0, -a3[0]*b3[0], -a3[1]*b3[0]],
               [    0,     0, 0, a3[0], a3[1], 1, -a3[0]*b3[1], -a3[1]*b3[1]]] )
    B = array([b0[0], b0[1], b1[0], b1[1], b2[0], b2[1], b3[0], b3[1]])

    return linalg.solve(A,B)


def createText(multi, sign):
    multi = multi.replace("[fo1]","")
    multi = multi.upper()
    multi = multi.split("[NL]")
    multi = multi[:sign.size[0]]

    size = (sign.coords[1][0]-sign.coords[0][0],abs(sign.coords[2][1]-sign.coords[1][1]))
    textImg = Image.new("RGBA",size)
    textd = ImageDraw.Draw(textImg)

    MAX_W = size[0]
    pad = sign.pad
    current_h = pad
    for line in multi:
            w, h = textd.textsize(line, font=sign.font)
            textd.text(((MAX_W - w) / 2, current_h), line, (255,76,0),font=sign.font)
            current_h += h + pad

    return textImg


def createSign(multiImg, sign):
    size = multiImg.size

    # transform the text
    signOut = Image.open(signs[sign_no].path)
    ar = ((0,0), (size[0],0), size, (0,size[1])) + sign.coords
    transform = get_transform_data(ar)
    txtOut = multiImg.transform(signOut.size, Image.PERSPECTIVE, transform, Image.BICUBIC)

    signOut.paste(txtOut, (1,1), txtOut)
    return signOut

def post(hex_data, type):
    url = "https://hipchat.datasys.swri.edu/v2/room/" + str(room) + "/share/file?auth_token=" + token

    files = {'file': ('out.'+type, hex_data, 'image/'+type)}

    s = requests.Session()
    req = requests.Request('POST',url,files=files)
    prep = req.prepare()
    prep.headers['Content-Type'] = prep.headers['Content-Type'].replace('form-data','related')
    resp = s.send(prep)
    s.close()


def postImage(imagePath):
    output = BytesIO()
    image.save(output, format='JPEG')
    hex_data = output.getvalue()
    post(hex_data, 'JPEG')


def sendToRoom(message,room, token):
    url = 'https://hipchat.datasys.swri.edu/v2/room/' + str(room) + '/notification?auth_token=' + token
    payload = {"color":"green","message":message,"notify":False,"message_format":"text"}
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)

def createGif(images):
    import imageio
    ioImages = []
    for img in images:
        buff = BytesIO()
        img.save(buff, format='gif')
        hex_data = buff.getvalue()
        ioImages.append(imageio.imread(hex_data))

    out = BytesIO()
    imageio.mimwrite(out, ioImages, format='gif', fps=0.75)
    hex_data = out.getvalue()
    post(hex_data,'gif')

testString = '{"event": "room_message", "item": {"message": {"date": "2017-05-06T16:37:20.492531+00:00", "from": {"id": 186, "links": {"self": "6"}, "mention_name": "n", "name": ".", "version": "YEG9Y3RO"}, "id": "9", "mentions": [], "message": "/dmsme 0[np]1[np]2", "type": "message"}, "room": {"id": 96, "is_archived": false, "links": {"members": "", "participants": "", "self": "", "webhooks": ""}, "name": "testroom", "privacy": "private", "version": "BTOFTL1R"}}, "oauth_client_id": "1", "webhook_id": 152}'

if 'REQUEST_METHOD' in environ :
	data = sys.stdin.read()
else:
	data = testString
dataJ = json.loads(data)

room = int(dataJ[u'item'][u'room'][u'id'])
if not keys.has_key(room):
    sys.exit(0)

token = keys[room]
try:
    message = "useage: /dmsme multi string[nl]next line"
    messages =  dataJ[u'item'][u"message"][u'message'].split(' ',1)
    if len(messages) == 1:
        # send usage info
        sendToRoom(message, room, token)
        sys.exit(0)

    if len(messages) == 2:
            message = messages[1]

    multi = message

    sign_no= random.randint(0, len(signs)-1)
    sign = signs[sign_no]

    if '[NP]' in multi.upper():
        images = list()
        for phase in multi.upper().split('[NP]')[:10]:
            multiImg = createText(phase, sign)
            image = createSign(multiImg, sign)
            image.thumbnail((500, image.size[1]*500/image.size[0]), Image.ANTIALIAS)
	    images.append(image)
        createGif(images)

    else:
        multiImg = createText(multi, sign)
        image = createSign(multiImg, sign)
        postImage(image)

except:
    tb = traceback.format_exc()
    print tb
    if room == 96:
        sendToRoom(str(tb), room, token)
