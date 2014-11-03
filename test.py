from pyzipcode import ZipCodeDatabase
zcdb = ZipCodeDatabase()
zipcode = zcdb[23229]
print zipcode.zip
print zipcode.city
print zipcode.state
print zipcode.longitude
print zipcode.latitude
print zipcode.timezone
