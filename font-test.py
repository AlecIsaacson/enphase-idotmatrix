from PIL import Image, ImageDraw, ImageFont

# fonts = ['../PixelOperator.ttf','../PixelOperatorSC.ttf','../PixelOperatorMono.ttf','../PixelOperatorMono8.ttf','../PixelOperator8.ttf']
# fonts = ['../10x20.pil','../ter-x20b-cp1250.pil','../ter-x20b-iso8859-1.pil','../ter-x20b-iso8859-2.pil']
fonts = ['../matrix-fonts/6-series/MatrixChunky6.bdf','../matrix-fonts/6-series/MatrixChunky6X.bdf','../matrix-fonts/8-series/MatrixChunky8.bdf','../matrix-fonts/8-series/MatrixChunky8X.bdf','../matrix-fonts/8-series/MatrixLight8.bdf','../matrix-fonts/8-series/MatrixLight8X.bdf']

X = 1
Y = 1

image = Image.new("RGB", (64,64), (0,0,0))

for fontName in fonts:
   print(fontName)
#   image = Image.new("RGB", (64, 64), (0,0,0))
   draw = ImageDraw.Draw(image)
   try:
      font = ImageFont.truetype(fontName, size=6)
   except:
      font = ImageFont.truetype(fontName, size=8)
#   font = ImageFont.load(fontName)
   draw.fontmode='1'
   draw.text((X,Y), '110 120 130 140', font=font)
   Y+=10 
   

image.save('combined.png')
#   print(font.getname()[0])
