import evdev, requests, time
import MySQLdb as mdb
from evdev import InputDevice, categorize, ecodes
from display_handler import showText, clearDisplay
from input_handler import input_price, take_picture, take_bon_picture
from buycott_api import triggerBuycott
from openEAN_api import triggerOpenEAN, parse_db_data, error_msg

dev = InputDevice('/dev/input/event0')

# Provided as an example taken from my own keyboard attached to a Centos 6 box:
scancodes = {
    # Scancode: ASCIICode
    0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
    10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'q', 17: u'w', 18: u'e', 19: u'r',
    20: u't', 21: u'y', 22: u'u', 23: u'i', 24: u'o', 25: u'p', 26: u'[', 27: u']', 28: u'CRLF', 29: u'LCTRL',
    30: u'a', 31: u's', 32: u'd', 33: u'f', 34: u'g', 35: u'h', 36: u'j', 37: u'k', 38: u'l', 39: u';',
    40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'z', 45: u'x', 46: u'c', 47: u'v', 48: u'b', 49: u'n',
    50: u'm', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 56: u'LALT', 57: u' ', 100: u'RALT'
}

capscodes = {
    0: None, 1: u'ESC', 2: u'!', 3: u'@', 4: u'#', 5: u'$', 6: u'%', 7: u'^', 8: u'&', 9: u'*',
    10: u'(', 11: u')', 12: u'_', 13: u'+', 14: u'BKSP', 15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
    20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'{', 27: u'}', 28: u'CRLF', 29: u'LCTRL',
    30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u':',
    40: u'\'', 41: u'~', 42: u'LSHFT', 43: u'|', 44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
    50: u'M', 51: u'<', 52: u'>', 53: u'?', 54: u'RSHFT', 56: u'LALT',  57: u' ', 100: u'RALT'
}

x = ''
caps = False
username = None
shop = None
curBasket = None

dev.grab()

db = mdb.connect("localhost","root","baer156537","ems" )


clearDisplay()    
showText(0,0,"Willkommen bei EMS")



for event in dev.read_loop():
    if event.type == ecodes.EV_KEY:
        data = categorize(event)  # Save the event temporarily to introspect it
        if data.scancode == 42:
            if data.keystate == 1:
                caps = True
            if data.keystate == 0:
                caps = False
        if data.keystate == 1:  # Down events only
            if caps:
                key_lookup = u'{}'.format(capscodes.get(data.scancode)) or u'UNKNOWN:[{}]'.format(data.scancode)  # Lookup or return UNKNOWN:XX
            else:
                key_lookup = u'{}'.format(scancodes.get(data.scancode)) or u'UNKNOWN:[{}]'.format(data.scancode)  # Lookup or return UNKNOWN:XX
            if (data.scancode != 42) and (data.scancode != 28):
                x += key_lookup  
            if(data.scancode == 28):
                
                scan_code = x
                
                if (scan_code == "max" or scan_code == "julia") and (username is None):     

                    username = scan_code
                    
                    clearDisplay()      
                    showText(0,0,"Hallo "+str(username))
                    showText(0,10,"Bitte Einkaufsort")
                    showText(0,20,"scannen")  

                

                elif (scan_code == "111" or scan_code =="112" or scan_code =="113" or scan_code =="114" or scan_code =="115" or scan_code =="116") and (shop is None) and (username is not None) :

                    shop = scan_code 
                    user = username

                    cur = db.cursor(mdb.cursors.DictCursor)

                    cur.execute("INSERT INTO baskets(shop,user) VALUES (%s,%s)",(shop,user))
        
                    db.commit()

                    result = cur.execute("SELECT LAST_INSERT_ID()")

                    if result > 0:

                        data = cur.fetchone()
                        curBasket = str(data["LAST_INSERT_ID()"])

                        cur.close()

                        clearDisplay()
                        showText(0,0,"User "+str(username))  
                        showText(0,10,"Warenkorb "+str(curBasket))    

                        bonpic = take_bon_picture(curBasket)

                        cur = db.cursor(mdb.cursors.DictCursor)

                        cur.execute("UPDATE baskets SET bonpic = %s WHERE id = %s",(bonpic,curBasket))

                        db.commit()

                        cur.close()

                        clearDisplay()
                        showText(0,0,"User "+str(username))  
                        showText(0,10,"Warenkorb "+str(curBasket))
                        showText(0,20,"Produkt Scan beginnen!")

                elif (len(scan_code) >= 8) and (curBasket is not None):

                    product_ean = scan_code
                    basket_id = curBasket
                    
                    cur = db.cursor(mdb.cursors.DictCursor)

                    exists = cur.execute("SELECT * FROM products WHERE ean = %s",[product_ean])
            
                    cur.close()

                    if (exists != 0):

                        cur = db.cursor(mdb.cursors.DictCursor)

                        cur.execute("INSERT INTO purchased_items(basket_id,ean) VALUES (%s,%s)",(basket_id,product_ean))

                        db.commit()

                        cur.close()

                        clearDisplay()    
                        showText(0,0,str(product_ean))
                        showText(0,10,"In WK "+str(curBasket))  
                        showText(0,20,"eingetragen")
                        showText(0,30,"Scan fortsetzen")  
                    else:

                        clearDisplay()    
                        showText(0,0,"Kein DB Eintrag,")
                        showText(0,10,"Hole Daten...")

                        product = triggerOpenEAN(product_ean)
                    
                        if type(product) is dict:
                            
                            price = input_price()
                            
                            cur = db.cursor(mdb.cursors.DictCursor)

                            cur.execute("INSERT INTO products(ean,name,detailname,vendor,maincat,subcat,descr,origin,price) VALUES ( %s,%s,%s,%s,%s,%s,%s,%s,%s)",(product_ean,product["name"],product["detailname"],product["vendor"],product["maincat"],product["subcat"],product["descr"],product["origin"],price))
                    
                            db.commit()
                    
                            cur.close()


                            cur = db.cursor(mdb.cursors.DictCursor)

                            cur.execute("INSERT INTO purchased_items(basket_id,ean) VALUES (%s,%s)",(basket_id,product_ean))

                            db.commit()

                            cur.close()

                            clearDisplay()
                            showText(0,0,str(product_ean))
                            showText(0,10,"Daten von OpenEAN")   
                            showText(0,20,"in DB+WK eingetragen.")     
                            showText(0,30,"Scan fortsetzen")      

                        else:
                            
                            product = triggerBuycott(product_ean)

                            if type(product) is dict:

                                price = input_price()
                            
                                cur = db.cursor(mdb.cursors.DictCursor)

                                cur.execute("INSERT INTO products(ean,name,detailname,vendor,maincat,subcat,descr,origin,price) VALUES ( %s,%s,%s,%s,%s,%s,%s,%s,%s)",(product_ean,product["name"],product["detailname"],product["vendor"],product["maincat"],product["subcat"],product["descr"],product["origin"],price))
                    
                                db.commit()
                    
                                cur.close()


                                cur = db.cursor(mdb.cursors.DictCursor)

                                cur.execute("INSERT INTO purchased_items(basket_id,ean) VALUES (%s,%s)",(basket_id,product_ean))

                                db.commit()

                                cur.close()

                                clearDisplay()
                                showText(0,0,str(product_ean))
                                showText(0,10,"Daten von Buycott")   
                                showText(0,20,"in DB+WK eingetragen.")     
                                showText(0,30,"Scan fortsetzen")  

                            else:


                                
                                pic = take_picture(basket_id)
                                price = input_price()
                                
                                cur = db.cursor(mdb.cursors.DictCursor)

                                cur.execute("INSERT INTO products(ean,price,pic) VALUES ( %s,%s,%s)",(product_ean,price,pic))
                    
                                db.commit()
                    
                                cur.close()

                                cur = db.cursor(mdb.cursors.DictCursor)

                                cur.execute("INSERT INTO purchased_items(basket_id,ean) VALUES (%s,%s)",(basket_id,product_ean))

                                db.commit()

                                cur.close()

                                clearDisplay()
                                showText(0,0,str(product_ean))
                                showText(0,10,"Keine DB Daten erhalten")   
                                showText(0,20,"Nur EAN eingetragen.") 
                                showText(0,30,"Scan fortsetzen") 
                    
                elif scan_code=="stop":

                    username=None
                    shop=None
                    curBasket=None

                    clearDisplay()
                    showText(0,0,"Einkauf eingetragen.")  
                    time.sleep(2)
                    clearDisplay()                    
                    
                else:
                
                    clearDisplay()
                    showText(0,0,"Erst einloggen")
                    showText(0,10,"und Einkaufsort")
                    showText(0,20,"angeben")  
                    time.sleep(2)
                    clearDisplay()   


                x = ''

                 