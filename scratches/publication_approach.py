# "Publication approach" as discussed on 5th of April

from snowmicropyn.proksch2015_classapproach import Proksch2015
from snowmicropyn import Profile

p = Profile.load('/Users/marcel/Dropbox/SMP/pnt_examples/S31M0067.pnt')

print(Proksch2015.pubinfo.authors)
print(Proksch2015.pubinfo.journal)
print(Proksch2015.pubinfo.title)

result = Proksch2015.apply(p)
