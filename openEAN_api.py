import requests


def parse_db_data(key,signs,data):
	
	d = data
	val = d[(d.find(key)+signs):(d.find("\n",(d.find(key))))]
	return val


def error_msg(error_id,product_ean):
		
		val = ""
		
		if error_id == "1": 
			val = product_ean + "\n" + "not found"
		elif error_id == "2": 
			val = product_ean +"\n"+ "checksum incorrect"
		elif error_id == "3": 
			val = product_ean + "\n" +"EAN-format incorrect"
		elif error_id == "4":
			val =  product_ean + "\n" +"not a global, unique EAN"     
		elif error_id == "5":
			val = product_ean + "\n" +"access limit exceeded"    
		elif error_id == "6":
			val = product_ean + "\n" +"no product name"      
		elif error_id == "7":
			val = product_ean + "\n" +"product name too long"    
		elif error_id == "8":
			val = product_ean + "\n" +"no or wrong main category id" 
		elif error_id == "9":
			val = product_ean + "\n" +"no or wrong sub category id"  
		elif error_id == "10":
			val = product_ean + "\n" +"illegal data in vendor field"
		elif error_id == "11":
			val = product_ean + "\n" +"illegal data in description field"
		elif error_id == "12":
			val = product_ean + "\n" +"data already submitted"
		elif error_id == "13":
			val = product_ean + "\n" +"queryid missing or wrong "
		elif error_id == "14":
			val = product_ean + "\n" +"unknown command"

		return str(val)  


def triggerOpenEAN(product_ean):
	
	
	database_request = requests.get("http://opengtindb.org/?ean="+product_ean+"&cmd=query&queryid=400000000")

	d = database_request.text
		
	error = d[(d.find("error=")+6):(d.find("\n",(d.find("error"))))]
	
	
	if (error == "0"):

		name = parse_db_data("name=",5,d)
		detailname = parse_db_data("detailname=",11,d)
		vendor = parse_db_data("vendor=",7,d)
		maincat = parse_db_data("maincat=",8,d)
		subcat = parse_db_data("subcat=",7,d)
		descr = parse_db_data("descr=",6,d)
		origin = parse_db_data("origin=",7,d)

		product = {
						"ean": product_ean,
						"name": name,
						"detailname": detailname,
						"vendor": vendor,
						"maincat": maincat,
						"subcat": subcat,
						"descr": descr,
						"origin":origin
						}

		
		
		return product
	
	else:
		
		
		error_txt = error_msg(error,product_ean)

		return error_txt

