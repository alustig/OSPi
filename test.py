import ephem, sys
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

print sunrise
sunrise = sunrise.split(' ')
sunrise = sunrise[1].split(":")
if (sunrise[0]<13):
	sunrise[2] = 'AM' 
else:
	sunrise[0] = str(int(sunrise[0])-12)
	sunrise[2] = 'PM'

print sunset
sunset = str(ephem.localtime(o.next_setting(s)))
sunset = sunset.split(' ')
sunset = sunset[1].split(":")
if (sunset[0]<13):
	sunset[2] = 'AM' 
else:
	sunset[0] = str(int(sunset[0])-12)
	sunset[2] = 'PM'

srise = sunrise[0]+":"+sunrise[1]+" "+sunrise[2]
sset = sunset[0]+":"+sunset[1]+" "+sunset[2]
print "Rising ",srise
print "Setting ",sset
