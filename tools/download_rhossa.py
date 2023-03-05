#!/usr/bin/env python3

#https://tc.copernicus.org/articles/14/1829/2020/
#https://www.envidat.ch/dataset/wfj_rhossa

import os
import shutil

url_file = "./envidatS3paths.txt"
cmd = f"wget --no-host-directories --force-directories --input-file={url_file}"
os.system(cmd)

location = "./envicloud/slf/sph-ct/2020_rhossa_paper_calonne_tc/data"
target = "../data/rhossa"
shutil.move(location, target)
shutil.rmtree("./envicloud")
