import wx
from cStringIO import StringIO
import urllib2
import os
import string
from menus import CheckListCtrl

#globals
map_types = ["Satellite","Road Map","Hybrid","Terrain"]
slf_coords = [46.812151, 9.847202] 
icon = "http://tinyurl.com/p93j947"

class Map(wx.Frame):
    """main Frame"""
    def __init__(self, parent, id, files=[], title="Measurement Locations"):
        wx.Frame.__init__(self, parent, id, title, size = (800, 500))
        
        self.picture = wx.StaticBitmap(self)
        
        self.files = files
        self.center = 0
        self.label = []
        self.zoom = 14
        self.maptype = "satellite"
        
        
        if self.internet_on():
            self.createItems()
            if  self.isListChecked():
                self.bmp = self.getImage()
                self.updatePicture()
                self.createLayout()
                self.Centre()
                self.Show()
        else:
            self.Destroy() 
        
    def getImage(self, resolution="250x250"):
        """ capture image from google static api"""
        
        self.GetCenter()
        base = "http://maps.googleapis.com/maps/api/staticmap?"
        center = "center=" + str(self.center[0]) + "," + str(self.center[1])
        size = "&size=" + resolution
        zoom = "&zoom=" + str(self.zoom)
        maptype = "&maptype=" + self.maptype
        scale = "&scale=2"
        marker = self.GetLabel()
        sensor = "&sensor=false"
        url = base + center + size + zoom + scale + maptype + marker + sensor
        #print url
        imagedata = StringIO(urllib2.urlopen(url).read())
        self.stream = wx.ImageFromStream(imagedata)
        bmp = wx.BitmapFromImage(self.stream)
        return bmp
    
    def updatePicture(self):
        """update image"""
        self.picture.SetFocus()
        self.picture.SetBitmap(self.bmp)
        
    def createItems(self):
        """create all items"""
        #menu
        self.menubar = wx.MenuBar()  
        self.fileMenu = wx.Menu()
        qms = self.fileMenu.Append(wx.ID_SAVE, '&Save Image')
        self.Bind(wx.EVT_MENU, self.OnSave, qms)
        qec = self.fileMenu.Append(wx.ID_ANY, '&Export Coordinates')
        self.Bind(wx.EVT_MENU, self.OnExport, qec)
        qme = self.fileMenu.Append(wx.ID_EXIT, '&Quit')
        self.Bind(wx.EVT_MENU, self.OnQuit, qme)
        self.menubar.Append(self.fileMenu, '&File')
        self.SetMenuBar(self.menubar) 
        
        #image options
        self.zoomTxt = wx.StaticText(self, 200, "Zoom Factor")
        self.slider = wx.Slider(self, 300, value=14, minValue=1, maxValue=20, style=wx.SL_HORIZONTAL,size=(500,-1))
        self.combo = wx.ComboBox(self, 500, "Satellite",choices=map_types, style=wx.CB_READONLY,size=(180,-1))
        
        wx.EVT_SLIDER(self,300,self.OnEvent)
        wx.EVT_COMBOBOX(self,500,self.OnEvent)
        
        
        #list
        self.list = CheckListCtrl(self,size=(675,500))
        self.list.InsertColumn(0, 'Label')
        self.list.InsertColumn(1, 'File Name')
        self.list.InsertColumn(2, 'Latitude')
        self.list.InsertColumn(3, 'Longitude')
        self.list.InsertColumn(4, 'PDOP')
        self.list.SetColumnWidth(0, 50)
        self.list.SetColumnWidth(1, 150)
        self.list.SetColumnWidth(2, 200)
        self.list.SetColumnWidth(3, 200)
        self.list.SetColumnWidth(4, 50)
        
        self.list.OnCheckItem = self.OnCheckItem
        
        wx.EVT_CHECKBOX(self.list,600,self.OnEvent)
        
        #create list entries  
        letters = string.ascii_uppercase
        i = 0
        num_labels = 0       
        for entry in self.files:
            lat = self.files[i].header["Latitude"]
            long = self.files[i].header["Longitude"]
            name = os.path.basename(self.files[i].filename)
            pdop = self.files[i].header["PDOP"]
              
            if -180<=lat<=180:
                try:
                    label = letters[num_labels]
                    num_labels += 1
                except:
                    label = letters[0]
                    num_labels = 1
                
            else:
                label = "-"
            
            self.label.append(label)
            self.list.InsertStringItem(i,label)
            if not label == "-": self.list.CheckItem(i, True)    
            self.list.SetStringItem(i,1,name)
            self.list.SetStringItem(i,2,str(lat))
            self.list.SetStringItem(i,3,str(long))
            self.list.SetStringItem(i,4,"%.1f"%pdop)
            i+=1
    
    def isListChecked(self):
        if [index for index in range(self.list.ItemCount)
                if self.list.IsChecked(index)] == []:
                    return self.nothingToShow()
        else:
            return True
        
    def OnCheckItem(self, index, flag):
        """checking item event"""
        if self.files[index].header["Latitude"] == 0.0 or self.files[index].header["Latitude"] > 180:
            self.list.CheckItem(index, False)
        else:
            self.zoom = self.slider.GetValue()
            map = self.combo.GetValue()
            "Satellite","Road Map","Hybrid","Terrain"
            if map == "Satellite":  self.maptype = "satellite"
            if map == "Road Map":   self.maptype = "roadmap"
            if map == "Hybrid":     self.maptype = "hybrid"
            if map == "Terrain":    self.maptype = "terrain"
            
            
            self.bmp = self.getImage()
            self.updatePicture()
            self.createLayout()
            self.Update()
           
    def GetCenter(self): 
        """get center of active coordinates"""           
        try:
            sum_lat = 0
            sum_long = 0
            i = 0
            for entry in range(len(self.files)):
                if self.list.IsChecked(entry):
                    sum_lat += self.files[entry].header["Latitude"]
                    sum_long += self.files[entry].header["Longitude"]
                    i += 1
            self.center = [sum_lat/float(i),sum_long/float(i)]
                    
        except:
            self.center = slf_coords
            pass
     
    def GetLabel(self):
        """create labels for google static api"""
        try:
            label = []
            for entry in range(len(self.files)):
                if self.list.IsChecked(entry):
                    label.append("&markers=size:mid|color:red%7Clabel:" + self.label[entry] + "%7C" + str(self.files[entry].header["Latitude"]) + "," + str(self.files[entry].header["Longitude"]))                    
        except:
            label = "&markers=size:mid|color:red%7Clabel:" + "A" + "%7C" + str(slf_coords[0]) + "," + str(slf_coords[1])
            pass
        if label == []:
            label = "&markers=icon:"+ icon + "|" + str(slf_coords[0]) + "," + str(slf_coords[1])
                
        marker = "".join(label)
        
        return marker
            
    def createLayout(self):
        """set window layout"""
        
        sizer = wx.BoxSizer()
        
        leftbox = wx.BoxSizer(wx.VERTICAL)   
        leftbox.Add(item=self.picture, flag=wx.ALL, border=10)
        leftbox.Add(item=self.zoomTxt, flag=wx.CENTER,border=10)
        leftbox.Add(item=self.slider, flag=wx.LEFT,border=10)       
        leftbox.Add(item=self.combo, flag=wx.CENTER,border=10)
        leftbox.AddSpacer(10)
        
        rightbox = wx.BoxSizer(wx.VERTICAL)
        rightbox.Add(self.list,flag=wx.ALL, border=10)
        
        sizer.Add(leftbox)
        sizer.Add(rightbox)
        self.SetSizerAndFit(sizer)

    def internet_on(self):
        """check if internet connection can be established"""
        try:
            urllib2.urlopen('http://74.125.228.100',timeout=2)
            return True
        except urllib2.URLError:
            message = """No Internet Connection established.
                        Can't show google maps."""
            caption = "Warning"
            warning = wx.MessageDialog(self,message,caption,wx.OK) 
            warning.ShowModal()
            warning.Destroy()
            return False
    
    def OnEvent(self,e):
        """define user events"""
        self.zoom = self.slider.GetValue()
        map = self.combo.GetValue()
        "Satellite","Road Map","Hybrid","Terrain"
        if map == "Satellite":  self.maptype = "satellite"
        if map == "Road Map":   self.maptype = "roadmap"
        if map == "Hybrid":     self.maptype = "hybrid"
        if map == "Terrain":    self.maptype = "terrain"
        
        self.bmp = self.getImage()
        self.updatePicture()
        self.createLayout()
        self.Update()

    def OnSave(self,e):
        """save button functionality"""
        
        file_choices = "PNG (*.png)|*.png"
        
        dlg = wx.FileDialog(
            self, 
            message="Save Map as...",
            defaultDir=os.getcwd(),
            defaultFile="Map.png",
            wildcard=file_choices,
            style=wx.SAVE|wx.OVERWRITE_PROMPT)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            image = self.getImage("800x800")
            image.SaveFile(path, wx.BITMAP_TYPE_PNG)
            
        dlg.Destroy()

    def OnQuit(self,e):
        print "exit"
        self.Destroy()
        
    def OnExport(self,e):
        """export coordinates"""
        
        file_choices = "COORD (*.coord)|*.COORD"
        
        dlg = wx.FileDialog(
            self, 
            message="Save Coordinates as...",
            defaultDir=os.getcwd(),
            defaultFile="SMP_Coordinates.txt",
            wildcard=file_choices,
            style=wx.SAVE|wx.OVERWRITE_PROMPT)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            f = open(path, 'w')
            f.write('#Automatic written Coordinates by PyNTReader\n'
                '#SLF Institute for Snow and Avalanche Research\n\n'
                "#Filename\tLongitude\tLatitude\tPdop\n")

            for i in range(len(self.files)):
                line = "%s\t%f\t%f\t%.2f\n" %(os.path.basename(self.files[i].filename),self.files[i].header["Longitude"],self.files[i].header["Latitude"],self.files[i].header["PDOP"])
                f.write(line)
            f.close()
            
        dlg.Destroy()
        
    def nothingToShow(self):
            caption = "Warning"
            message = """Oooops, no coordinates to display.\nShow SLF in Davos, instead?"""
            warning = wx.MessageDialog(None,
                                       message,
                                       caption,
                                       wx.YES_NO|wx.ICON_EXCLAMATION)
             
            return warning.ShowModal() == wx.ID_YES
            
        
class MyApp(wx.App):
    def OnInit(self):
        frame = Map(None, -1)
        self.SetTopWindow(frame)
        return True

if __name__=="__main__":
    app = MyApp(0)
    app.MainLoop()