import time
from keypad import keypad
from display_handler import showText,clearDisplay
from subprocess import call


def input_price():

	kp = keypad(columnCount = 4)   
	seq = []
	gotprice = False
	clearDisplay()
	showText(0,0,"Preis eingeben")
	while gotprice is False:
		
		digit = None
			
		digit = kp.getKey()
			
		if digit is not None: 
				
			seq.append(digit)

			if len(seq) == 4:
				if seq[1] == "*":
					gotprice = True

			elif len(seq) == 5:
				gotprice = True		
			

			s = ""
			numb= s.join(seq).replace("*",".")
			clearDisplay()
			showText(0,0,numb)
			print numb

			

		
	
	clearDisplay()
	showText(0,0,"Preis: "+numb)
	
	time.sleep(0.4)

	return numb

def take_picture(product_ean=False,picnumber=False):

	clearDisplay()
	showText(0,0,"Foto aufnehmen")
	showText(0,10,"A druecken")

	kp = keypad(columnCount = 4)   
	picture_taken = False

	while picture_taken == False:

		button = None
			
		button = kp.getKey()

		if button == "A" and product_ean is not False:
			
			picPath ="static/product_pics/"+str(product_ean)+".jpg"
			
			call(["fswebcam","-r","640x480",picPath])
			
			clearDisplay()
			showText(0,0,"Foto")
			showText(0,10,"gespeichert")

			picture_taken=True

			return picPath
		
		elif button == "A" and picnumber is not False:
			
			picPath ="static/pics/pic_"+str(picnumber)+".jpg"
			
			call(["fswebcam","-r","640x480",picPath])
			
			clearDisplay()
			showText(0,0,"Foto")
			showText(0,10,"gespeichert")

			picture_taken=True

			return picPath


def take_bon_picture(basket_id):
	
	clearDisplay()
	showText(0,0,"Kassenbon Foto?")
	showText(0,10,"A: ja")
	showText(0,20,"B: nein")

	kp = keypad(columnCount = 4)   
	picture_taken = False

	while picture_taken == False:

		button = None
			
		button = kp.getKey()

		if button == "A":
			
			picPath ="static/bon_pics/"+str(basket_id)+"_bon.jpg"
			
			call(["fswebcam","-r","640x480",picPath])
			
			clearDisplay()
			showText(0,0,"Foto")
			showText(0,10,"gespeichert")

			picture_taken=True

			return picPath
		
		if button == "B":
			
			clearDisplay()
			showText(0,0,"Abbruch")
			showText(0,10,"Kein Foto")
			showText(0,20,"aufgenommen")
			picPath=None
			picture_taken=True
			return picPath
