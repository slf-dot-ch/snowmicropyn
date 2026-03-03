import time
from snowmicropyn import Profile
from snowmicropyn.pyngui.document import Document

p = Profile.load('/home/lrrr/Documents/SLF_local/projects_local/AWI_Disko/AWI_Disko/01_data/level0_stitched_pnts/20240411_Transect2/S31M0549_S31M0550.PNT')
doc = Document(p)

# Warm up / first run
doc.recalc_derivatives_old()

# Timed run
start = time.perf_counter()
doc.recalc_derivatives_old()
elapsed = time.perf_counter() - start
print(f"\nSequential: {elapsed:.3f}s")


# Warm up / first run
doc.recalc_derivatives()

# Timed run
start = time.perf_counter()
doc.recalc_derivatives()
elapsed = time.perf_counter() - start
print(f"\nParallel: {elapsed:.3f}s")
