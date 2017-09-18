import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

RST = 24
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
disp.begin()
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()
disp.clear()
draw.rectangle((0,0,width,height), outline=0, fill=0)
disp.display()

def showText(x,y,text):

	
	draw.text((x, y),str(text), font=font, fill=255)
	disp.image(image)
	disp.display()
def clearDisplay():
	
	disp.clear()
	draw.rectangle((0,0,width,height), outline=0, fill=0)
	disp.display()