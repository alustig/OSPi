import ephem
from pyzipcode import ZipCodeDatabase

zcdb = ZipCodeDatabase()
zipcode = zcdb[23229]
print zipcode.zip
print zipcode.city
print zipcode.state
print zipcode.latitude
print zipcode.longitude
print zipcode.timezone

o=ephem.Observer()
o.lat=zipcode.latitude
o.long=zipcode.longitude
s=ephem.Sun()
s.compute()
print "Rising ",ephem.localtime(o.next_rising(s))
print "Setting ",ephem.localtime(o.next_setting(s))
