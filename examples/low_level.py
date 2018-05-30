import snowmicropyn as smp
header, raw_samples = smp.Pnt.load('profiles/S37M0876.pnt')

print(header[smp.Pnt.Header.TIMESTAMP_YEAR].value)
print(raw_samples[2000:2005])
