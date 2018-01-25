

from platform import system
import os, wx, sys
import errno, shutil
import struct
import zipfile

def make_zipfile(output_filename, source_dir):
    relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(source_dir):
            # add directory (needed for empty dirs)
            zip.write(root, os.path.relpath(root, relroot))
            for file in files:
                filename = os.path.join(root, file)
                if os.path.isfile(filename): # regular files only
                    arcname = os.path.join(os.path.relpath(root, relroot), file)
                    zip.write(filename, arcname)

def copy(src, dest):
    """copy files and folders recursively"""
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)

app = wx.App(False)
dlg = wx.DirDialog(None, message = "Select build path")
if dlg.ShowModal() == wx.ID_OK:
    
    #generate buildname
    opsys = system() 
    print("%s Operating System Detected" %opsys)  
    bits = "_%dbit" %(struct.calcsize("P") * 8)
    build_name = "SnowMicroPyn_" + opsys + bits
    
    base = dlg.GetPath()
    savepath = os.path.join(base,build_name)
    dlg.Destroy()
    bin = os.path.dirname(sys.argv[0])
    src = os.path.dirname(bin)
    buildpath = os.path.join(src,"extensions","build")
    distpath = os.path.join(src,"extensions","dist")
    binpath = os.path.join(src,"SnowMicroPyn.py")
    artworkpath = os.path.join(src,"artwork")
    iconpath = os.path.join(artworkpath,"icon.ico")
    changelog = os.path.join(os.path.dirname(src),"CHANGELOG.txt")
    readme = os.path.join(os.path.dirname(src),"README.txt")
    zip = os.path.join(base, build_name + ".zip")
    
    print "Save path: %s"%savepath
    print "Binary path: %s"%binpath
    print "Artwork path: %s"%iconpath
    print "Changelog file: %s"%changelog
    print "Readme file: %s"%readme
    
    if not os.path.exists(savepath):
        os.mkdir(savepath)
    if not os.path.exists(buildpath):
        os.mkdir(buildpath)
    
    cmd = "pyinstaller -wF %s"%(binpath)
    wincmd = "pyinstaller -wF --icon=%s %s"%(iconpath, binpath)
    
    if opsys == "Windows":
        exe = wincmd
    else:
        exe = cmd
    print "Executing command:\n%s" %exe 
    
    if os.system(exe):
        print "BUILD FAILED"
     
    #remove temporary files
    for root, dirs, files in os.walk(buildpath, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(buildpath)
    
    #add help files and artwork to root
    copy(readme,savepath)
    copy(changelog,savepath)
    copy(src,os.path.join(savepath,"src"))
    
    #copy and remove built exe
    for root, dirs, files in os.walk(distpath, topdown=False):
        for name in files:
            copy(os.path.join(root,name),os.path.join(savepath,name))
     
    for root, dirs, files in os.walk(distpath, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(distpath)       
    
    #zip everything
    make_zipfile(zip,savepath)