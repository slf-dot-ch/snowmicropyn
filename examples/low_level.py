from snowmicropyn import Pnt

header, raw_samples = Pnt.load('./some_directory/S31M0067.pnt')

print(header[Pnt.Header.TIMESTAMP_YEAR].value)
print(raw_samples[2000:2005])
