import ephem
from pyzipcode import ZipCodeDatabase
from datetime import datetime

zcdb = ZipCodeDatabase()
zipcode = zcdb[23229]
print zipcode.zip
print zipcode.city
print zipcode.state
print zipcode.latitude
print zipcode.longitude
print zipcode.timezone

now = datetime.now()
o = ephem.Observer()
o.pressure = 0
o.horizon = '-0:34'
o.date = now
o.lat=str(zipcode.latitude)
o.long=str(zipcode.longitude)
s=ephem.Sun()
print "Rising ",ephem.localtime(o.next_rising(s))
print "Setting ",ephem.localtime(o.next_setting(s))
