#!/usr/bin/env python3

#https://tc.copernicus.org/articles/14/1829/2020/
#https://www.envidat.ch/dataset/wfj_rhossa

import os
import pathlib
import shutil

# Download all available manual pits plus a single SMP measurement for this location:
url_file = "./envidatS3paths.txt"
dl_cmd = f"wget --no-host-directories --force-directories --input-file={url_file}"
os.system(dl_cmd)

location = "./envicloud/slf/sph-ct/2020_rhossa_paper_calonne_tc/data"
target = "../data/rhossa"
if not os.path.exists(target):
    os.makedirs(target, exist_ok=True)

# Find all SMP and manual profiles, rename them according to their parent folder (the date),
# and move them to a different location:
extensions = [".pnt", ".caaml"]
profiles = [pro for pro in pathlib.Path(location).rglob("*") if pro.suffix in extensions]
for pro in profiles:
    parent = pathlib.PurePath(pro.parent).name
    shutil.move(pro, f"{target}/{parent}{pro.suffix}")

# Now the manual and SMP profiles are connected via their file names and contained within
# a single folder. Delete wget's (empty) download directory:
shutil.rmtree("./envicloud")
