from PIL import Image, ImageDraw, ImageFont

fontName = '../matrix-fonts/6-series/MatrixChunky6.bdf'

GREEN         = (70, 210, 70)
YELLOW        = (240, 190, 0)
RED           = (220, 55, 55)
ORANGE        = (255, 140, 0)
WHITE         = (255, 255, 255)
GREY          = (146, 146, 150)
GREY          = (106, 106, 106)
GREY          = (64, 64, 64)

# colors = ['GREEN','YELLOW','RED','ORANGE']
# numbers = ['000','110','120','130']

textList = [(GREEN,'000'),(YELLOW,'110'),(RED,'120'),(ORANGE,'130')]

production = [4700, 3800, 3600, 3200, 2900, 2100, 1500]
consumption = [835, 851, 2090, 783, 925, 917, 2260]


X = 0
Y = 0

image = Image.new("RGB", (64,64), (0,0,0))

draw = ImageDraw.Draw(image)
font = ImageFont.truetype(fontName, size=6)
draw.fontmode='1'

for text in textList:
   draw.text((X,Y), text[1], font=font, fill=text[0])
   X+=14

# 20 pixels / 300 watts per pixel
# draw.line([(0,43),(64,43)], fill=GREY, width=1)

# draw.line([(1,42),(1,23)], fill=GREEN, width=1)
# draw.line([(1,44),(1,63)], fill=RED, width=1)

# 25 pixels / 240 watts / pixel
draw.line([(0,38),(64,38)], fill=GREY, width=1)

# draw.line([(5,37),(5,13)], fill=GREEN, width=1)
# draw.line([(5,39),(5,63)], fill=RED, width=1)

X=0
for prod in production:
   pixels = prod // 240
   print(str(prod) + " " + str(pixels))
   draw.line([(X,37),(X,37 - pixels)], fill=GREEN, width=1)
   X+=1

X=0
for consume in consumption:
   pixels = consume // 240
   print(str(consume) + " " + str(pixels))
   draw.line([(X,39),(X,39 + pixels)], fill=RED, width=1)
   X+=1

image.save('combined.png')
#   print(font.getname()[0])
