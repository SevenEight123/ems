import requests

def triggerBuycott(product_ean):

	if len(product_ean) != 13:

		product_ean = product_ean.zfill(13)


	data = {"barcode":product_ean,"access_token":"_kDWp4BZmfj16SZ5uo2GJyJLsR6sMLD8QSs81ryC"}
	url ="https://www.buycott.com/api/v4/products/lookup"

	response = requests.get(url,params=data)
	
	res_data = response.json()
		
	if res_data["success"] == True:
		
		product_data= res_data["products"][0]
		
		product = {
						"ean": product_ean,
						"name": product_data["product_name"],
						"detailname": product_data["brand_name"],
						"vendor": product_data["manufacturer_name"],
						"maincat": product_data["category_name"],
						"subcat": " ",
						"descr": product_data["product_description"],
						"origin":product_data["country_of_origin"]
						}

		return product
	
	else:
		return False

	

