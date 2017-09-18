
import time,sys, subprocess, os
from flask import Flask, render_template, flash, redirect,request, url_for, session, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField,PasswordField,SelectField,validators
from passlib.hash import sha256_crypt
from functools import wraps
from openEAN_api import parse_db_data, error_msg, triggerOpenEAN
from buycott_api import triggerBuycott
#import scan_func
#from scan_func import start_scanner


app = Flask(__name__)

# Config mysql

app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] ='root'
app.config['MYSQL_PASSWORD'] ='secret'
app.config['MYSQL_DB'] ='ems'
app.config['MYSQL_CURSORCLASS'] ='DictCursor'

# init
mysql = MySQL(app)
command = ["python","/home/pi/ems/scan_func.py"]
scanner = subprocess.Popen(command)
global s_pid
s_pid = scanner.pid


# check if user is logged in 
def is_logged_in(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'logged_in' in session:
			return f(*args,**kwargs)
		else:
			flash('Nicht eingeloggt! Kein Zugriff!','danger')
			return redirect(url_for('login'))
	return wrap 

def shutdown_server():
	func = request.environ.get('werkzeug.server.shutdown')
	if func is None:
		raise RuntimeError('Not running with the Werkzeug Server')
	func()

### ROUTES ###

@app.route('/shutdown')
@is_logged_in
def shutdown():
	
	subprocess.Popen(["kill","-9",str(s_pid)])

	shutdown_server()

	
	return "Server offline"

#index
@app.route('/')
def index():





	return render_template("home.html")

@app.route('/sketches')
@is_logged_in
def sketches():

	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM sketches")
	sketches = cur.fetchall()
	cur.close()



	return render_template("sketches.html",sketches = sketches)


@app.route('/sketch/<string:sketch_id>',methods = ['GET','POST'])
@is_logged_in
def sketch(sketch_id):

	if request.method == 'POST':
		
		sketch_name = request.form["name"]

		cur = mysql.connection.cursor()
		cur.execute("UPDATE sketches SET name = %s WHERE id = %s",(sketch_name,sketch_id))
		mysql.connection.commit()
		cur.close()		

		


	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM sketches WHERE id = %s",[sketch_id])
	sketch = cur.fetchone()
	cur.close()



	return render_template("sketch.html",sketch = sketch)




@app.route('/mealplan')
@is_logged_in
def mealplan():


	cur = mysql.connection.cursor()	
	cur.execute("SELECT * FROM mealplan WHERE id=(SELECT MAX(id) FROM mealplan)")
	mealplan = cur.fetchone()
	
	cur.execute("SELECT * FROM meals")
	meals = cur.fetchall()
	
	cur.close()

	return render_template("mealplan.html",mealplan = mealplan,meals = meals)

@app.route("/newmealplan")
@is_logged_in
def newmealplan():
	
	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM meals ORDER BY RAND() LIMIT 7")
	meals = cur.fetchall()
	cur.execute("INSERT INTO mealplan(mo,di,mi,do,fr,sa,so,mo_mn,di_mn,mi_mn,do_mn,fr_mn,sa_mn,so_mn) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (meals[0]["id"],meals[1]["id"],meals[2]["id"],meals[3]["id"],meals[4]["id"],meals[5]["id"],meals[6]["id"],meals[0]["name"],meals[1]["name"],meals[2]["name"],meals[3]["name"],meals[4]["name"],meals[5]["name"],meals[6]["name"]))
	mysql.connection.commit()
	cur.close()
	
	return redirect(url_for("mealplan"))

@app.route("/changemeal/<string:mealplanid>/<string:day>/<string:mealid>")
@is_logged_in
def changemeal(mealplanid,day,mealid):

	namefield = ""
	cur = mysql.connection.cursor()

	cur.execute("SELECT * FROM meals WHERE id= %s",[mealid])
	newMeal = cur.fetchone()

	if day == "mo":
		
		cur.execute("UPDATE mealplan SET mo=%s, mo_mn=%s WHERE	id=%s",(mealid,newMeal["name"],mealplanid))
		mysql.connection.commit()
		cur.close()

	elif day =="di":
		
		cur.execute("UPDATE mealplan SET di=%s, di_mn=%s WHERE	id=%s",(mealid,newMeal["name"],mealplanid))
		mysql.connection.commit()
		cur.close()

	elif day =="mi":

		cur.execute("UPDATE mealplan SET mi=%s, mi_mn=%s WHERE	id=%s",(mealid,newMeal["name"],mealplanid))
		mysql.connection.commit()
		cur.close()

	elif day == "do":

		cur.execute("UPDATE mealplan SET do=%s, do_mn=%s WHERE	id=%s",(mealid,newMeal["name"],mealplanid))
		mysql.connection.commit()
		cur.close()

	elif day == "fr":

		cur.execute("UPDATE mealplan SET fr=%s, fr_mn=%s WHERE	id=%s",(mealid,newMeal["name"],mealplanid))
		mysql.connection.commit()
		cur.close()


	elif day == "sa":

		cur.execute("UPDATE mealplan SET sa=%s, sa_mn=%s WHERE	id=%s",(mealid,newMeal["name"],mealplanid))
		mysql.connection.commit()
		cur.close()


	elif day == "so": 	

		cur.execute("UPDATE mealplan SET so=%s, so_mn=%s WHERE	id=%s",(mealid,newMeal["name"],mealplanid))
		mysql.connection.commit()
		cur.close()

	
	return redirect(url_for("mealplan"))


@app.route('/meal/<string:mealid>')
@is_logged_in
def meal(mealid):

	cur = mysql.connection.cursor()

	cur.execute("SELECT * FROM meals WHERE id = %s",[mealid])
	meal = cur.fetchone()
	
	cur.close()

	
	cur = mysql.connection.cursor()

	cur.execute("SELECT * FROM ingrd WHERE mealid = %s",[mealid])

	ingrds= cur.fetchall()

	cur.close()
	

	return render_template("meal.html",meal = meal, ingrds = ingrds)

@app.route('/add_meal',methods = ['GET','POST'])
@is_logged_in
def add_meal():

	if request.method == 'POST':

		name = request.form["name"]
		recipe = request.form["recipe"]
		ingrd = request.form["ingrd"]


		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO meals(name,recipe,ingrd) VALUES (%s,%s,%s)", (name,recipe,ingrd))
		
		mysql.connection.commit()

		cur.close()
		

		flash("Rezept eingetragen!","success")

		return redirect(url_for("receipts"))

	return render_template("add_meal.html")


@app.route('/receipts')
@is_logged_in
def receipts():

	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM meals")
	meals = cur.fetchall()
	cur.close()
	


	return render_template("receipts.html",meals = meals)


@app.route('/pictures')
@is_logged_in
def pictures():

	cur = mysql.connection.cursor()

	cur.execute("SELECT * FROM pictures")

	pictures = cur.fetchall()	

	cur.close()


	return render_template("pictures.html",pictures=pictures)

@app.route('/buylist')
@is_logged_in
def buylist():

	cur = mysql.connection.cursor()

	cur.execute("SELECT * FROM buylist")

	buylist = cur.fetchall()	

	cur.close()

	return render_template("buylist.html",buylist=buylist)


@app.route('/buylist_add/<string:product_ean>')
@is_logged_in
def buylist_add(product_ean):

	cur = mysql.connection.cursor()

	exists = cur.execute("SELECT * FROM buylist WHERE ean = %s",[product_ean])

	cur.close()

	if exists == 0:

		cur = mysql.connection.cursor()

		cur.execute("SELECT * FROM products WHERE ean = %s",[product_ean])

		product = cur.fetchone()

		cur.close()


		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO buylist(ean,name,detailname) VALUES (%s,%s,%s)",(product_ean,product["name"],product["detailname"]))

		mysql.connection.commit()

		cur.close()

	return redirect(url_for("products"))

@app.route('/buylist_remove/<string:product_ean>')
@is_logged_in
def buylist_remove(product_ean):

	cur = mysql.connection.cursor()

	cur.execute("DELETE FROM buylist WHERE ean = %s ",[product_ean] )

	mysql.connection.commit()

	cur.close()

	return redirect(url_for("buylist"))


#show profile details
@app.route('/profile',methods=['GET','POST'])
@is_logged_in
def profile():
	
	form = NoteForm(request.form)
	author = session['username']
	
	if request.method == 'POST':
		
		
		note = form.note.data
		cur=mysql.connection.cursor()

		cur.execute("INSERT INTO notes(author,note) VALUES (%s,%s)",(author,note))

		mysql.connection.commit()

		cur.close()



		return redirect(url_for("profile"))
	
	cur = mysql.connection.cursor()

	cur.execute("SELECT * FROM notes WHERE author = %s",[author])

	notes = cur.fetchall()
	
	return render_template("profile.html",form = form,notes=notes)      


@app.route('/dbupdate/<string:product_ean>/<string:database>')

def dbupdate(product_ean,database):
	
	if database == "openEAN":

		product = triggerOpenEAN(product_ean)

		if type(product) is dict:

					
			cur = mysql.connection.cursor()

			cur.execute("UPDATE products SET name = %s,detailname = %s,vendor = %s,maincat = %s,subcat = %s,descr = %s,origin = %s WHERE ean = %s",(product["name"],product["detailname"],product["vendor"],product["maincat"],product["subcat"],product["descr"],product["origin"],product_ean))
					
			mysql.connection.commit()
					
			cur.close()
					
		
			flash("Produktdaten aktualisiert.(OpenEAN)","success")
					
			return redirect(url_for("products"))  

		else:	
		
			flash("Keine Daten empfangen ","danger")
		
			return redirect(url_for("products"))
						  
	
	elif database == "buycott":   

		product= triggerBuycott(product_ean)

		if type(product) is dict:

			cur = mysql.connection.cursor()

			cur.execute("UPDATE products SET name = %s,detailname = %s,vendor = %s,maincat = %s,subcat = %s,descr = %s,origin = %s WHERE ean = %s",(product["name"],product["detailname"],product["vendor"],product["maincat"],product["subcat"],product["descr"],product["origin"],product_ean))
					
			mysql.connection.commit()
					
			cur.close()

			flash("Produktdaten aktualisiert.(Buycott)","success")
					
			return redirect(url_for("products"))   
		
		else:	
		
			flash("Keine Daten empfangen ","danger")
		
			return redirect(url_for("products"))


# add a new product to db
@app.route('/add_product', methods=['GET','POST'])
@is_logged_in
def add_product():

	if request.method == 'POST':

		product_ean = request.form["product_ean"]
		price = request.form["product_price"]
		
		if (len(product_ean) >= 8):
			
			cur = mysql.connection.cursor()

			exists = cur.execute("SELECT * FROM products WHERE ean = %s",[product_ean])
			
			

			if (exists != 0):

				product = cur.fetchone()   
		
				cur.close()                 
				success = True
				flash("Produkt bereits in Datenbank vorhanden!","success")

				return render_template("add_product.html",product=product, success=success)

			else:       
				
				cur.close()
				
				
				product=triggerOpenEAN(product_ean)

				if type(product) is dict:

					cur = mysql.connection.cursor()

					cur.execute("INSERT INTO products(ean,name,detailname,vendor,maincat,subcat,descr,origin,price) VALUES ( %s,%s,%s,%s,%s,%s,%s,%s,%s)",(product["ean"],product["name"],product["detailname"],product["vendor"],product["maincat"],product["subcat"],product["descr"],product["origin"],price))
					
					mysql.connection.commit()
					
					cur.close()
					
					success = True
					flash("Produktdaten erhalten, Eintrag vorgenommen(OpenEAN).","success")
					return render_template("add_product.html",product=product, success=success,price=price)

				
				else:       
					
					
					product = triggerBuycott(product_ean)

					if type(product) is dict:

						cur = mysql.connection.cursor()

						cur.execute("INSERT INTO products(ean,name,detailname,vendor,maincat,subcat,descr,origin,price) VALUES ( %s,%s,%s,%s,%s,%s,%s,%s,%s)",(product["ean"],product["name"],product["detailname"],product["vendor"],product["maincat"],product["subcat"],product["descr"],product["origin"],price))                  
						mysql.connection.commit()
					
						cur.close()

						success = True
						flash("Produktdaten erhalten, Eintrag vorgenommen(Buycott).","success")
						return render_template("add_product.html",product=product, success=success,price=price)

					else:
						
						cur = mysql.connection.cursor()

						cur.execute("INSERT INTO products(ean) VALUES (%s,%s)",(product_ean,price))
					
						mysql.connection.commit()
					
						cur.execute("SELECT * FROM products WHERE ean = %s",[product_ean])

						product = cur.fetchone()  

						cur.close()

						flash("Keine Produktdaten erhalten, Eintrag nur mit EAN vorgenommen.","success")
						success= False
						return render_template("edit_product.html",product=product,price=price)                             
		else:
			

			flash('Die EAN muss zwischen 8-13 Zeichen lang sein!','danger')
			success = False

			return render_template("add_product.html", success = success)
	
	else:
		return render_template("add_product.html")              
				
@app.route("/edit_product/<string:product_ean>",methods=['GET','POST'])
@is_logged_in
def edit_product(product_ean):

	if request.method == 'POST':

		product = {
		"name" : request.form["name"],
		"detailname" : request.form["detailname"],
		"vendor" : request.form["vendor"],
		"maincat" : request.form["maincat"],
		"subcat" : request.form["subcat"],
		"descr" : request.form["descr"],
		"origin" : request.form["origin"],
		"price" : request.form["price"]
		}

		cur = mysql.connection.cursor()

		cur.execute("UPDATE products SET name = %s,detailname = %s,vendor = %s,maincat = %s,subcat = %s,descr = %s,origin = %s,price = %s WHERE ean = %s",(product["name"],product["detailname"],product["vendor"],product["maincat"],product["subcat"],product["descr"],product["origin"],product["price"],product_ean))

		mysql.connection.commit()

		cur.close()

		flash("Eintrag aktualisert","success")
		time.sleep(1)
		redirect(url_for("edit_product",product_ean=product_ean))
		

	cur = mysql.connection.cursor()

	cur.execute("SELECT * FROM products WHERE ean = %s",[product_ean])
			
	product = cur.fetchone()     
		
	cur.close()

	return render_template("/edit_product.html",product_ean=product_ean,product=product)    


@app.route("/delete_product/<string:product_ean>")
@is_logged_in
def delete_product(product_ean):

	cur = mysql.connection.cursor()

	cur.execute("DELETE FROM products WHERE ean = %s ",[product_ean] )

	mysql.connection.commit()

	cur.close()
	
	flash("Produkt geloescht!","danger")

	return redirect(url_for('products'))

@app.route("/delete_basket/<string:basket_id>")
@is_logged_in
def delete_basket(basket_id):

	cur = mysql.connection.cursor()

	cur.execute("DELETE FROM baskets WHERE id = %s ",[basket_id] )

	mysql.connection.commit()

	cur.execute("DELETE FROM purchased_items WHERE basket_id = %s ",[basket_id] )

	mysql.connection.commit()

	cur.close()
	
	flash("Warenkorb geloescht!","danger")

	return redirect(url_for('baskets'))

# show all products
@app.route('/products')
@is_logged_in
def products():

	cur = mysql.connection.cursor()

	cur.execute("SELECT * FROM products")

	products = cur.fetchall()

	cur.close()

	return render_template("products.html",products=products)

# show details of single product
@app.route('/product/<string:ean>')
@is_logged_in
def product(ean):
	return render_template("product.html",ean=ean)


@app.route('/delete/<string:basket_id>/<string:product_ean>/<string:p_id>')
@is_logged_in   
def delete(basket_id,product_ean,p_id):

				
		cur = mysql.connection.cursor()

		cur.execute("DELETE FROM purchased_items WHERE basket_id = %s AND ean = %s AND p_id = %s ",(basket_id,product_ean,p_id) )

		mysql.connection.commit()

		cur.close()
				
		return redirect(url_for('basket',basket_id=basket_id))

@app.route('/basket/<string:basket_id>', methods=['GET','POST'])
@is_logged_in
def basket(basket_id):

	if request.method == 'POST':

		if request.form['addProductToBasket']:

			product_ean = request.form['addProductToBasket']

			cur = mysql.connection.cursor()

			exists = cur.execute("SELECT * FROM products WHERE ean = %s",[product_ean])
			
			cur.close() 

			if (exists != 0):

				cur = mysql.connection.cursor()

				cur.execute("INSERT INTO purchased_items(basket_id,ean) VALUES (%s,%s)",(basket_id,product_ean))

				mysql.connection.commit()

				cur.close()

			else:
			
				flash("Keine EAN gefunden!","danger")   
		
							
	cur = mysql.connection.cursor()

	cur.execute("SELECT purchased_items.ean,purchased_items.p_id, products.* FROM purchased_items JOIN products ON products.ean=purchased_items.ean WHERE basket_id=%s",[basket_id])

	basket_items = cur.fetchall()   

	cur.execute("SELECT baskets.id, baskets.date, shops.shop_name, baskets.user,baskets.bonpic FROM baskets JOIN shops ON shops.id = baskets.shop WHERE baskets.id=%s",[basket_id])

	basket_info = cur.fetchone()

	cur.close()
	basket_price = 0.00
	for item in basket_items:

		basket_price = basket_price + float(item["price"])


	return render_template("basket.html",basket_id=basket_id, basket_items=basket_items,basket_info=basket_info,basket_price=basket_price)


# login
@app.route('/login', methods =['GET','POST'])
def login():
	if request.method == 'POST':
		#get fields
		username = request.form['username']
		password_canidate = request.form['password']

		# create cursor

		cur = mysql.connection.cursor()

		#get user by username 
		result = cur.execute("SELECT * FROM users WHERE username = %s",[username])
		if result > 0:
			# get stored hash
			data = cur.fetchone()
			password = data['password']
			# compare if pw is correct

			if sha256_crypt.verify(password_canidate,password):
				app.logger.info('Password matched')
				# passed
				session['logged_in'] = True
				session['username'] = username

				return redirect(url_for('index'))
			else:
				app.logger.info('Password mismatch')
				error = "Falsches Passwort"
				return render_template('login.html',error=error)    
		else:
			
			app.logger.info('no user')
			error = 'Username existiert nicht'
			return render_template('login.html', error=error)       

	return render_template("login.html")

#Logout
@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('Du bist nun ausgeloggt','success')

	return redirect(url_for('login'))

# spawn new basket
@app.route('/add_basket', methods=['GET','POST'])
@is_logged_in
def add_basket():

	form = BasketInputForm(request.form)

	if request.method == 'POST' and form.validate():
		
		shop = form.shop.data
		user = session['username']
		
		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO baskets(shop,user) VALUES (%s,%s)",(shop,user))
		
		mysql.connection.commit()

		result = cur.execute("SELECT LAST_INSERT_ID()")

		if result > 0:

			data = cur.fetchone()
			session['cur_basket'] = str(data["LAST_INSERT_ID()"])

		cur.close()

		flash("Warenkorb mit ID "+session['cur_basket']+" angelegt!","success")

		return redirect(url_for("baskets"))
	return render_template("add_basket.html", form=form)
	

# User Registration
@app.route('/register', methods=['GET','POST'])
@is_logged_in
def register():
	
	form = RegisterForm(request.form)
	
	if request.method == 'POST' and form.validate():
		
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))

		

		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO users(name,email,username,password) VALUES(%s,%s,%s,%s)",
			(name,email,username,password))

		mysql.connection.commit()

		cur.close()

		flash('Registrierung erfolgreich!','success')

		return redirect(url_for('login'))

		
	return render_template('register.html', form=form)

# show baskets
@app.route('/baskets')
@is_logged_in
def baskets():

	
	cur = mysql.connection.cursor()

	cur.execute("SELECT baskets.id, shops.shop_name, baskets.date, baskets.user FROM baskets INNER JOIN shops ON baskets.shop=shops.id ORDER BY baskets.id ASC ")

	baskets = cur.fetchall()

	cur.close()


	return render_template('baskets.html',baskets=baskets)


### FORM CLASSES ###
class RegisterForm(Form):
	
	name = StringField('Name',[validators.Length(min=1,max=50)])
	username = StringField('Username',[validators.Length(min=3,max=25)])
	email = StringField('Email',[validators.Length(min=6,max=50)])
	password = PasswordField('Password',[
		validators.DataRequired(),
		validators.EqualTo('confirm',message='Passwords do not match')
	])
	confirm = PasswordField('Confirm Password')

class BasketInputForm(Form):
	
	shop = SelectField('Einkaufsort', choices=[('111', 'Aldi Leutzsch'), ('112', 'Konsum Leutzsch'), ('113', 'Kaufland Lindenau'), ('114', 'Rewe Leutzsch'), ('115', 'Penny Leutzsch'), ('116', 'LoeschDepot Leutzsch')])


class NoteForm(Form):

	note =TextAreaField('Notitz', [validators.Length(min=30)])
class ProductInputForm(Form):

	ean = StringField('EAN',[validators.Length(min=8,max=13)])



if __name__ == '__main__':
	app.secret_key='@@l(oux0=r@ydlc)+w-(io7r=pti7=_&)myd)!966x7q1ky-mo'
	app.run(host='0.0.0.0',debug=True)
