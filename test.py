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
sunrise = str(ephem.localtime(o.next_rising(s)))
sunset = str(ephem.localtime(o.next_setting(s)))

sunrise = sunrise.split(' ')
sunrise = sunrise[1].split(":")



print "Rising ",sunrise[0],":",sunrise[1]
print "Setting ",ephem.localtime(o.next_setting(s))
