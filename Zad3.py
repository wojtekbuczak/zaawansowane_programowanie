from Property import Property
from House import House
from Flat import Flat

house = House(area=120, rooms=5, price=300000, address="123 Elm Street", plot=500)
flat = Flat(area=75, rooms=3, price=200000, address="456 Oak Avenue", floor=4)

print(house)
print(flat)