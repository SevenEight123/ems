from subprocess import call


def take_picture(basket_id):

	call(["fswebcam","-r","640x480","pictures/"+basket_id+".jpg"])

	

take_picture("19")	