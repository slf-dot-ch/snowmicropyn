import wx, wx.lib.dialogs
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
from wx.lib.agw import ultimatelistctrl as ulc
from wx.lib.agw.floatspin import FloatSpin
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas, NavigationToolbar2WxAgg as NavigationToolbar
from os.path import basename
import mathematics as calc
##########################################################
# Author:    Sascha Grimm
# Company:   SLF, Institute for Snow and Avalanche Research
##########################################################
#the gui script contains functions for display messages. it
#uses wx framework 
#to guarantee crossplatform compatibility
###########################################################

def openFile(message='Select multiple SMP binarys...'):
    """Open File Dialog"""
    app = wx.App(False)
    filters = 'SMP files (*.pnt)|*.pnt'
    dialog = wx.FileDialog( None, message=message, wildcard = filters, style = wx.OPEN | wx.MULTIPLE )
    print 'Selected Files:'
    if dialog.ShowModal() == wx.ID_OK:
        selected = dialog.GetPaths()
        for selection in selected:
            print '    ', selection
    else:
        selected = None
        print "Nothing was selected."
    dialog.Destroy()
    return selected

def infoScroll(message, caption="Information"):
    """Show info Message"""
    app = wx.App(False)
    dlg = wx.lib.dialogs.ScrolledMessageDialog(None, message, caption)
    dlg.ShowModal()

def ask(question, caption = 'Question'):
    """show yes/no dialog"""
    app = wx.App(False)
    dlg = wx.MessageDialog(None, question, caption, wx.YES_NO | wx.ICON_QUESTION)
    result = dlg.ShowModal() == wx.ID_YES
    dlg.Destroy()
    return result

def info(message, caption = 'Information'):
    """show simple info message"""
    app = wx.App(False)
    dlg = wx.MessageDialog(None, message, caption, wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()
    
def warn(message, caption = 'Warning!'):
    """show warning message"""
    app = wx.App(False)
    dlg = wx.MessageDialog(None, message, caption, wx.OK | wx.ICON_WARNING)
    dlg.ShowModal()
    dlg.Destroy()

class HeaderInfo(wx.Dialog):
    def __init__(self, parent, id, header, title="Header Information"):
        wx.Dialog.__init__(self, parent, id, title,size=(400,500),style=wx.DEFAULT_DIALOG_STYLE)       
        
        self.lc = wx.ListCtrl(self, -1, style=wx.LC_REPORT,size=(400,450))
        self.lc.InsertColumn(0, 'Entry')
        self.lc.InsertColumn(1, 'Value')
        self.lc.SetColumnWidth(0, 200)
        self.lc.SetColumnWidth(1, 200)
        
        info=[
              ["Original Filename" , header["File Name"]+".pnt"],
              ["Software Version" , "%.2f" %(float(header["Version"])/100)],
              ["SnowMicroPen Serial", str(header["SMP Serial"])],
              ["Date dd.mm.yyyy" ,  "%02d.%02d.%04d" %(header["Day"],header["Month"],header["Year"])],
              ["Time UTC hh:mm:ss" , "%02d:%02d:%02d" %(header["Hour"],header["Min"],header["Sec"])],
              ["Speed", "%d mm/s" %header["Speed [mm/s]"]],
              ["GPS Fix","Mode %d" %header["Fix Mode"]],
              ["GPS Coordinates", "%s, %s" %(header["Latitude"],header["Longitude"])],
              ["Pdop", "%.2f" %header["PDOP"]],
              ["Number of Samples",str(header["Force Samples"])],
              ["Distance between Samples","%.3f um" %(header["Samples Dist [mm]"]*1000)],
              ["Maximum Length","%.1f mm" %header["Length [mm]"]],
              ["Measured Length","%.1f mm" %(header["Samples Dist [mm]"]*header["Force Samples"])],
              ["Force Conversion Factor","%.4f N/mV" %(header["CNV Force [N/mV]"])],
              ["Tip Diameter","%d mm" %(header["Diameter [um]"]/1000)],
              ["Force Offset","%.2f N" %header["Offset [N]"]],
              ["Amplifier Range", "%d pC" %header["Amp Range [pC]"]],
              ["Amplifier Serial", header["Amp Serial"]],
              ["Sensor Sensitivity", "%d pC/N" %header["Sensitivity [pC/N]"]],
              ["Sensor Serial",header["Sensor Serial"]],
              ["Overload","%d N" %header["Overload [N]"]]
              ]

        index=0
        for key,value in info:
            self.lc.InsertStringItem(index,key)
            self.lc.SetStringItem(index,1,value)
            index+=1
        
        sizer = wx.BoxSizer()
        sizer.Add(self.lc,proportion=0, flag=wx.ALL, border=10)
        self.SetSizerAndFit(sizer)
        self.Centre()
                
    def OnClose(self, event):
        self.Destroy()

class PlotOptions(wx.Dialog):
    def __init__(self, parent=None, id=-1, title="Plot Options"):
        wx.Dialog.__init__(self, parent, id, title, size=(750, 230))
        
        colors=["blue","black","green","red","yellow"]
        styles=["-","-.",":","steps","..."]
        
        self.color = colors[0]
        self.style = styles[0]
        self.width = 1
        self.xlabel = "Depth [mm]"
        self.ylabel = "Force [N]"
        self.xlim = (0,300,True)
        self.ylim = (0,41,True)
        self.sampling = 2
        self.logscale = True
                
        wx.StaticBox(self, -1, 'Axis', (5, 5), size=(240, 170))
        self.autox = wx.CheckBox(self, -1 ,'Auto X',(15, 30))
        wx.StaticText(self,-1, 'X min',(15,65))
        self.xmin = wx.SpinCtrl(self,-1,size=(50,-1),pos=(60,60),min=-100,max=1800,initial=self.xlim[0])
        wx.StaticText(self,-1, 'X max',(15,95))
        self.xmax = wx.SpinCtrl(self,-1,size=(50,-1),pos=(60,90),min=0,max=1800,initial=self.xlim[1])
        self.autoy = wx.CheckBox(self, -1 ,'Auto Y',(115, 30))
        wx.StaticText(self,-1, 'Y min',(115,60))
        self.ymin = wx.SpinCtrl(self,-1,size=(50,-1),pos=(160,60),min=-1,max=45,initial=self.ylim[0])
        wx.StaticText(self,-1, 'Y max',(115,90))
        self.ymax = wx.SpinCtrl(self,-1,size=(50,-1),pos=(160,90),min=-1,max=45,initial=self.ylim[1])
        wx.StaticText(self,-1,"X Label",(15,120))
        self.optionXlabel = wx.TextCtrl(self,-1,size=(90,25),pos=(15,140),value=self.xlabel)
        wx.StaticText(self,-1,"Y Label",(115,120))
        self.optionYlabel = wx.TextCtrl(self,-1,size=(90,25),pos=(115,140),value=self.ylabel)               
        
        
        wx.StaticBox(self, -1, 'Line', (250, 5), size=(240, 170))
        wx.StaticText(self,-1, 'Color',(265,30))
        self.optionColor = wx.ComboBox(self, -1, pos=(265, 50), size=(150, -1), choices=colors, style=wx.CB_READONLY,value=self.color)

        wx.StaticText(self,-1, 'Style',(265,80))
        self.optionStyle = wx.ComboBox(self, -1, pos=(265, 100), size=(150, -1), choices=styles, style=wx.CB_READONLY,value=self.style)
        
        wx.StaticText(self,-1, 'Width',(265,140))
        self.optionWidth = wx.SpinCtrl(self, -1,name="Width",initial=1,min=0.5,max=10,pos=(325,135),size=(50,-1))

        wx.StaticBox(self, -1, 'Others', (495, 5), size=(240, 170))
        wx.StaticText(self,-1, 'Plot downsampling factor',(515,30))
        self.samp = wx.SpinCtrl(self,-1,size=(50,-1),pos=(515,60),min=1,max=10,initial=self.sampling)

        wx.Button(self, 1, 'OK', (335, 185), (80, -1))
               
        self.autox.SetValue(True)
        self.autoy.SetValue(True)
        self.ToggleX(False)
        self.ToggleY(False)
        
        self.Bind(wx.EVT_CHECKBOX, self.OnAutoX,self.autox)
        self.Bind(wx.EVT_CHECKBOX, self.OnAutoY,self.autoy)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=1)       
        
        self.Centre()

    def OnClose(self, event):
        self.updateValues()
        self.Close()
        
    def updateValues(self):
        self.color = self.optionColor.GetValue()
        self.style = self.optionStyle.GetValue()
        self.width = self.optionWidth.GetValue()
        self.xlabel = self.optionXlabel.GetValue()
        self.ylabel = self.optionYlabel.GetValue()
        self.xlim = (self.xmin.GetValue(),self.xmax.GetValue(),self.autox.GetValue())
        self.ylim = (self.ymin.GetValue(),self.ymax.GetValue(),self.autoy.GetValue())
        self.sampling = self.samp.GetValue() 
        
    def OnAutoX(self,e):
        if self.autox.GetValue()==False:
            toggle = True
        else:
            toggle = False
        
        self.ToggleX(toggle)

    def OnAutoY(self,e):
        if self.autoy.GetValue()==False:
            toggle = True
        else:
            toggle = False
        
        self.ToggleY(toggle)
            
    def ToggleX(self,enable=False):
        self.xmin.Enable(enable)
        self.xmax.Enable(enable)

    def ToggleY(self,enable=False):
        self.ymin.Enable(enable)
        self.ymax.Enable(enable)
  
class SaveOptions(wx.MultiChoiceDialog):
    """save options dialog"""
    def __init__(self, parent=None):
        wx.MultiChoiceDialog.__init__(self, parent,
                                      message = "\n",
                                      caption = "Save Options",
                                      choices = ["Save plot as image (*.png)",
                                               "Save header infos as ASCII (*.txt)",
                                               "Save measurement data as ASCII (*.dat)",
                                               "Save Shot Noise Parameters as ASCII (*.shn)"])
        self.SetSelections([0,1])
        
        self.precision = wx.SpinCtrl(parent = self, min = 0, max = 6, initial = 3, size = (50,-1), pos = (140,9))
        title_precision = wx.StaticText(self,-1,"Decimal Digits:",pos=(15,12))
        self.overlap = wx.SpinCtrl(parent = self, min = 1, max = 100,initial = 50, size = (50,-1), pos = (140,39))
        title_overlap = wx.StaticText(self,-1,"Overlap [%]:", pos = (15,42))
        self.window = wx.SpinCtrl(parent = self,min = 0.1, max = 100,initial = 2.5,size = (50,-1),pos = (320,39))
        title_window = wx.StaticText(self,-1,"Window [mm]:",pos=(220,42))
        
        self.Fit()
    
    def Overlap(self):
        return self.overlap.GetValue()  
     
    def Window(self):
        return self.window.GetValue()
    
    def Precision(self):
        return self.precision.GetValue()
        
    def plot(self):
        return 0 in self.GetSelections()
    
    def header(self):
        return 1 in self.GetSelections()
    
    def data(self):
        return 2 in self.GetSelections() 
        
    def shotnoise(self):
        return 3 in self.GetSelections()
        

class Tabs(wx.Notebook):
    """    Notebook class    """

    #----------------------------------------------------------------------
    def __init__(self, parent, extended = True):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=
                             wx.BK_DEFAULT
                             )

        self.tabAxis = wx.Panel(self)
        self.AddPage(self.tabAxis, "Axis")

        self.tabGraph = wx.Panel(self)
        self.AddPage(self.tabGraph, "Graph")

        self.tabGraph.Enable(extended)
        if not extended:
            self.tabGraph.Hide()

        #self.tabSurface = wx.Panel(self)
        #self.AddPage(self.tabSurface, "Surface")
########################################################################
class GraphOptions(wx.Dialog):
    """Graph options for plot in main window"""

    #----------------------------------------------------------------------
    def __init__(self,parent=None,extended=True):
        """Constructor"""
        wx.Dialog.__init__(self, parent, wx.ID_ANY,
                          "Graph Options",
                          size = (600,450),
                          )
        
        self.parent = parent
        colors=["blue","black","green","red","yellow","orange","pink","purple","brown",
                "gray","darkblue","silver","darkgreen","darkred","gold"]
        styles=["-","-.",":","steps","--","_"]
        
        #axis
        self.xlabel = "Depth [mm]"
        self.ylabel = "Force [N]"
        self.xlim = (0,300)
        self.auto_x = True
        self.ylim = (-1,41)
        self.auto_y = True
        self.xticks = 10
        self.auto_xticks = True
        self.yticks = 10
        self.auto_yticks = True
        self.mirrorx = False
        self.mirrory = False
        self.plot_title = "SMP Measurement"
        self.logscale = False
        #data
        self.color = colors[0]
        self.style = styles[0]
        self.width = 1
        self.sampling = 1
        #gradient
        self.grad_color = colors[3]
        self.grad_style = styles[2]
        self.grad_width = 1
        self.grad_sampling = 1000
        #median
        self.median_color = colors[9]
        self.median_style = styles[0]
        self.median_width = 1
        self.median_sampling = 200
        
        panel = wx.Panel(self)

        notebook = Tabs(panel,extended)
        confirm = wx.Button(panel, wx.ID_OK)
        self.Bind(wx.EVT_BUTTON,self.onOK,confirm)
        cancel = wx.Button(panel, wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON,self.onCancel,cancel)
        apply = wx.Button(panel, wx.ID_APPLY)
        self.Bind(wx.EVT_BUTTON,self.onApply,apply)  
                
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(notebook, 1, wx.ALL|wx.EXPAND)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(cancel)
        hsizer.Add(apply)
        hsizer.Add(confirm)
        vsizer.Add(hsizer,0,wx.ALIGN_RIGHT)
        panel.SetSizer(vsizer)
        self.Layout()
        
        #axis
        self.box_autox = wx.CheckBox(notebook.tabAxis, -1 ,'Auto X')
        self.Bind(wx.EVT_CHECKBOX,self.onUpdate,self.box_autox)
        self.box_autoy = wx.CheckBox(notebook.tabAxis, -1 ,'Auto Y')
        self.Bind(wx.EVT_CHECKBOX,self.onUpdate,self.box_autoy)
        self.box_autox_tick = wx.CheckBox(notebook.tabAxis, -1 ,'Auto X ticks')
        self.Bind(wx.EVT_CHECKBOX,self.onUpdate,self.box_autox_tick)
        self.box_autoy_tick = wx.CheckBox(notebook.tabAxis, -1 ,'Auto Y ticks')
        self.Bind(wx.EVT_CHECKBOX,self.onUpdate,self.box_autoy_tick)
        self.box_mirrorx = wx.CheckBox(notebook.tabAxis, -1 ,'Mirror X')
        self.box_mirrory = wx.CheckBox(notebook.tabAxis, -1 ,'Mirror Y')
        
        self.xmin  = FloatSpin(notebook.tabAxis,-1,value=self.xlim[0],min_val=-100.00,max_val=1800.00,increment=1,digits=3)
        label_xmin = wx.StaticText(notebook.tabAxis,-1, 'X min')
        self.ymin = FloatSpin(notebook.tabAxis,-1,value=self.ylim[0],min_val=-100.00,max_val=1800.00,increment=1,digits=3)
        label_ymin = wx.StaticText(notebook.tabAxis,-1, 'Y min')
        self.xmax = FloatSpin(notebook.tabAxis,-1,value=self.xlim[1],min_val=-100.00,max_val=1800.00,increment=1,digits=3)
        label_xmax = wx.StaticText(notebook.tabAxis,-1, 'X max')
        self.ymax = FloatSpin(notebook.tabAxis,-1,value=self.ylim[1],min_val=-100.00,max_val=1800.00,increment=1,digits=3)
        label_ymax = wx.StaticText(notebook.tabAxis,-1, 'Y max')
        
        self.xlabel_ctrl = wx.TextCtrl(notebook.tabAxis,-1,size=(200,-1),value=self.xlabel)
        label_xlabel = wx.StaticText(notebook.tabAxis,-1, 'X label')
        self.ylabel_ctrl = wx.TextCtrl(notebook.tabAxis,-1,size=(200,-1),value=self.ylabel)
        label_ylabel = wx.StaticText(notebook.tabAxis,-1, 'Y label')
        label_xticks = wx.StaticText(notebook.tabAxis,-1, 'X ticks')
        self.xticks_ctrl = wx.SpinCtrl(notebook.tabAxis,-1,size=(100,-1),min=1,max=100,initial=self.xticks,name="X ticks")
        label_yticks = wx.StaticText(notebook.tabAxis,-1, 'Y ticks')
        self.yticks_ctrl = wx.SpinCtrl(notebook.tabAxis,-1,size=(100,-1),min=1,max=100,initial=self.yticks,name="Y ticks")
        self.scale_ctrl = wx.CheckBox(notebook.tabAxis, -1, "Log Scale")
        
        self.box_autox.SetValue(True)
        self.xmin.Enable(False)
        self.xmax.Enable(False)
        self.box_autoy.SetValue(True)
        self.ymin.Enable(False)
        self.ymax.Enable(False)
        self.xticks_ctrl.Enable(False)
        self.yticks_ctrl.Enable(False)
        self.box_autox_tick.SetValue(True)
        self.box_autoy_tick.SetValue(True)
        self.box_mirrorx.SetValue(self.mirrorx)
        self.box_mirrory.SetValue(self.mirrory)
        self.scale_ctrl.SetValue(self.logscale)
        
        font = wx.Font(14,wx.DEFAULT, wx.NORMAL,wx.BOLD,True)
                
        #graph 
        label_data = wx.StaticText(notebook.tabGraph, -1, "Data Plot")
        label_sampling = wx.StaticText(notebook.tabGraph,-1, 'Down sampling Factor')
        self.sampling_ctrl = wx.SpinCtrl(notebook.tabGraph,-1,size=(100,-1),min=0,max=1000,initial=self.sampling,name="Sampling")
        label_color = wx.StaticText(notebook.tabGraph,-1, 'Line Color')
        self.color_ctrl = wx.ComboBox(notebook.tabGraph, -1, size=(150, -1), choices=colors, style=wx.CB_READONLY,value=self.color)
        label_style = wx.StaticText(notebook.tabGraph,-1, 'Line Style')
        self.style_ctrl = wx.ComboBox(notebook.tabGraph, -1, size=(150, -1), choices=styles, style=wx.CB_READONLY,value=self.style)
        label_width = wx.StaticText(notebook.tabGraph,-1, 'Line Width')
        self.width_ctrl = wx.SpinCtrl(notebook.tabGraph, -1,name="Width",initial=1,min=0.5,max=10,pos=(325,135),size=(50,-1))

        #gradient
        label_grad = wx.StaticText(notebook.tabGraph, -1, "Gradient")
        label_grad_sampling = wx.StaticText(notebook.tabGraph,-1, 'Down sampling Factor')
        self.grad_sampling_ctrl = wx.SpinCtrl(notebook.tabGraph,-1,size=(100,-1),min=0,max=1000,initial=self.grad_sampling,name="Sampling")
        label_grad_color = wx.StaticText(notebook.tabGraph,-1, 'Line Color')
        self.grad_color_ctrl = wx.ComboBox(notebook.tabGraph, -1, size=(150, -1), choices=colors, style=wx.CB_READONLY,value=self.grad_color)
        label_grad_style = wx.StaticText(notebook.tabGraph,-1, 'Line Style')
        self.grad_style_ctrl = wx.ComboBox(notebook.tabGraph, -1, size=(150, -1), choices=styles, style=wx.CB_READONLY,value=self.grad_style)
        label_grad_width = wx.StaticText(notebook.tabGraph,-1, 'Line Width')
        self.grad_width_ctrl = wx.SpinCtrl(notebook.tabGraph, -1,name="Width",initial=1,min=0.5,max=10,pos=(325,135),size=(50,-1))
        
        #median
        label_median = wx.StaticText(notebook.tabGraph, -1, "Median")
        label_median_sampling = wx.StaticText(notebook.tabGraph,-1, 'Window')
        self.median_sampling_ctrl = wx.SpinCtrl(notebook.tabGraph,-1,size=(100,-1),min=0,max=1000,initial=self.median_sampling,name="Sampling")
        label_median_color = wx.StaticText(notebook.tabGraph,-1, 'Line Color')
        self.median_color_ctrl = wx.ComboBox(notebook.tabGraph, -1, size=(150, -1), choices=colors, style=wx.CB_READONLY,value=self.median_color)
        label_median_style = wx.StaticText(notebook.tabGraph,-1, 'Line Style')
        self.median_style_ctrl = wx.ComboBox(notebook.tabGraph, -1, size=(150, -1), choices=styles, style=wx.CB_READONLY,value=self.median_style)
        label_median_width = wx.StaticText(notebook.tabGraph,-1, 'Line Width')
        self.median_width_ctrl = wx.SpinCtrl(notebook.tabGraph, -1,name="Width",initial=1,min=0.5,max=10,pos=(325,135),size=(50,-1))
            
        vert1 = wx.BoxSizer(wx.VERTICAL)
        vert2 = wx.BoxSizer(wx.VERTICAL)
        
        hor1 = wx.BoxSizer(wx.HORIZONTAL)
        hor1.Add(self.box_autoy,0,wx.ALIGN_CENTER|wx.ALL)
        hor1.Add(self.scale_ctrl,0,wx.ALIGN_CENTER|wx.ALL)        
                
        vert1.Add(self.box_autox,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert2.Add(hor1,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert1.Add(label_xmin,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert1.Add(self.xmin,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert2.Add(label_ymin,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert2.Add(self.ymin,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert1.Add(label_xmax,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert1.Add(self.xmax,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert2.Add(label_ymax,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert2.Add(self.ymax,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert1.Add(label_xlabel,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert1.Add(self.xlabel_ctrl,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert2.Add(label_ylabel,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert2.Add(self.ylabel_ctrl,0,wx.ALIGN_CENTER|wx.ALL,10)
        
        vert1.Add(self.box_autox_tick,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert1.Add(label_xticks,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert1.Add(self.xticks_ctrl,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert1.Add(self.box_mirrorx,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert2.Add(self.box_autoy_tick,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert2.Add(label_yticks,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert2.Add(self.yticks_ctrl,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert2.Add(self.box_mirrory,0,wx.ALIGN_CENTER|wx.ALL,10)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(vert1,wx.ALIGN_CENTER)
        sizer.Add(wx.StaticLine(notebook.tabAxis,style=wx.LI_VERTICAL,size=(-1,600)))
        sizer.Add(vert2,wx.ALIGN_CENTER)
        
        notebook.tabAxis.SetSizer(sizer)
            
        vert1 = wx.BoxSizer(wx.VERTICAL)
        vert2 = wx.BoxSizer(wx.VERTICAL)
        vert3 = wx.BoxSizer(wx.VERTICAL)
        
        vert1.Add(label_data,0,wx.ALIGN_CENTER|wx.ALL,20)
        vert1.Add(label_sampling,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert1.Add(self.sampling_ctrl,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert1.Add(label_color,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert1.Add(self.color_ctrl,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert1.Add(label_width,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert1.Add(self.width_ctrl,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert1.Add(label_style,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert1.Add(self.style_ctrl,0,wx.ALIGN_CENTER|wx.ALL,10)
        
        vert2.Add(label_grad,0,wx.ALIGN_CENTER|wx.ALL,20)
        vert2.Add(label_grad_sampling,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert2.Add(self.grad_sampling_ctrl,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert2.Add(label_grad_color,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert2.Add(self.grad_color_ctrl,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert2.Add(label_grad_width,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert2.Add(self.grad_width_ctrl,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert2.Add(label_grad_style,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert2.Add(self.grad_style_ctrl,0,wx.ALIGN_CENTER|wx.ALL,10)
        
        vert3.Add(label_median,0,wx.ALIGN_CENTER|wx.ALL,20)
        vert3.Add(label_median_sampling,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert3.Add(self.median_sampling_ctrl,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert3.Add(label_median_color,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert3.Add(self.median_color_ctrl,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert3.Add(label_median_width,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert3.Add(self.median_width_ctrl,0,wx.ALIGN_CENTER|wx.ALL,10)
        vert3.Add(label_median_style,0,wx.ALIGN_CENTER|wx.RIGHT,10)
        vert3.Add(self.median_style_ctrl,0,wx.ALIGN_CENTER|wx.ALL,10)
        
        label_data.SetFont(font)
        label_grad.SetFont(font)
        label_median.SetFont(font)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(vert1,wx.ALIGN_CENTER|wx.ALIGN_BOTTOM)
        sizer.Add(wx.StaticLine(notebook.tabGraph,style=wx.LI_VERTICAL,size=(-1,600)))
        sizer.Add(vert2,wx.ALIGN_CENTER|wx.ALIGN_BOTTOM)
        sizer.Add(wx.StaticLine(notebook.tabGraph,style=wx.LI_VERTICAL,size=(-1,600)))
        sizer.Add(vert3,wx.ALIGN_CENTER|wx.ALIGN_BOTTOM)
        
        notebook.tabGraph.SetSizer(sizer)
        
    def onOK(self,e):
        """OK button event"""
        self.onApply(e)
        self.Hide()
        
    def onApply(self,e):
        """Apply button event"""
        self.color = self.color_ctrl.GetValue()
        self.style = self.style_ctrl.GetValue()
        self.width = self.width_ctrl.GetValue()
        self.xlabel = self.xlabel_ctrl.GetValue()
        self.ylabel = self.ylabel_ctrl.GetValue()
        self.xlim = (self.xmin.GetValue(),self.xmax.GetValue())
        self.ylim = (self.ymin.GetValue(),self.ymax.GetValue())
        self.sampling = self.sampling_ctrl.GetValue()
        self.auto_x = self.box_autox.GetValue()
        self.auto_y = self.box_autoy.GetValue()
        self.xticks = self.xticks_ctrl.GetValue()
        self.auto_xticks = self.box_autox_tick.GetValue()
        self.yticks = self.yticks_ctrl.GetValue()
        self.auto_yticks = self.box_autoy.GetValue()
        self.mirrorx = self.box_mirrorx.GetValue()
        self.mirrory = self.box_mirrory.GetValue()
        self.grad_color = self.grad_color_ctrl.GetValue()
        self.grad_style = self.grad_style_ctrl.GetValue()
        self.grad_width = self.grad_width_ctrl.GetValue()
        self.grad_sampling = self.grad_sampling_ctrl.GetValue()
        self.logscale = self.scale_ctrl.GetValue()
        self.median_color = self.median_color_ctrl.GetValue()
        self.median_style = self.median_style_ctrl.GetValue()
        self.median_width = self.median_width_ctrl.GetValue()
        self.median_sampling = self.median_sampling_ctrl.GetValue()
        
        self.parent.draw_figure(autozoom=False)
        
    def onCancel(self,e):
        """cancel button event"""
        self.color_ctrl.SetValue(self.color)
        self.style_ctrl.SetValue(self.style)
        self.width_ctrl.SetValue(self.width)
        self.xlabel_ctrl.SetValue(self.xlabel)
        self.ylabel_ctrl.SetValue(self.ylabel)
        self.xmin.SetValue(self.xlim[0])
        self.xmax.SetValue(self.xlim[1])
        self.ymin.SetValue(self.ylim[0])
        self.ymax.SetValue(self.ylim[1])
        self.sampling_ctrl.SetValue(self.sampling)
        self.box_autox.SetValue(self.auto_x)
        self.box_autoy.SetValue(self.auto_y)
        self.xticks_ctrl.SetValue(self.xticks)
        self.box_autox_tick.SetValue(self.auto_xticks)
        self.yticks_ctrl.SetValue(self.yticks)
        self.box_autoy_tick.SetValue(self.auto_yticks)
        self.box_mirrorx.SetValue(self.mirrorx)
        self.box_mirrory.SetValue(self.mirrory)
        self.grad_color_ctrl.SetValue(self.grad_color)
        self.grad_style_ctrl.SetValue(self.grad_style)
        self.grad_width_ctrl.SetValue(self.grad_width)
        self.grad_sampling_ctrl.SetValue(self.grad_sampling)    
        self.scale_ctrl.SetValue(self.logscale)  
        self.median_color_ctrl.SetValue(self.median_color)
        self.median_style_ctrl.SetValue(self.median_style)
        self.median_width_ctrl.SetValue(self.median_width)
        self.median_sampling_ctrl.SetValue(self.median_sampling)  
        
        self.Hide()
      
    def onUpdate(self,e):
        xlim = not self.box_autox.GetValue()
        self.xmax.Enable(xlim)
        self.xmin.Enable(xlim)
        ylim = not self.box_autoy.GetValue()
        self.ymax.Enable(ylim)
        self.ymin.Enable(ylim)
        xtick = not self.box_autox_tick.GetValue()
        self.xticks_ctrl.Enable(xtick)
        ytick = not self.box_autoy_tick.GetValue()
        self.yticks_ctrl.Enable(ytick)

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    """list with Check boxes"""
    def __init__(self, parent, size):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER,size=size)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

import os
import mathematics as calc
from scipy.interpolate import interp1d
import numpy as np
class SuperPosition(wx.Frame):
    """main user interface for super position"""
  
    def __init__(self, parent=None, files=[],*args, **kwargs):
        wx.Frame.__init__(self, parent, -1, size = (800, 600))
        
        self.files = files
        self.Options = GraphOptions(self,extended=False)
        self.createMenu()
        self.setWindow()
        self.createPanel()
        self.createList()
        self.draw_figure()
        
    def createMenu(self):
        """create menu bar"""
        
        self.menubar = wx.MenuBar()  
        self.fileMenu = wx.Menu()
        self.plotMenu = wx.Menu(
                                )
        qms = self.fileMenu.Append(wx.ID_ANY, '&Save Plot')
        qec = self.fileMenu.Append(wx.ID_ANY, '&Save Data')
        self.Bind(wx.EVT_MENU, self.OnSaveData, qec)
        
        self.fileMenu.AppendSeparator()
        
        subtract = self.plotMenu.Append(100, "Subtract Plots")
        self.Bind(wx.EVT_MENU, self.OnSubtract, subtract)
        mean = self.plotMenu.Append(wx.ID_ANY, "Average Plots")
        self.Bind(wx.EVT_MENU, self.OnMean, mean)
        self.plotMenu.AppendSeparator()
        
        self.showLegend = self.plotMenu.Append(wx.ID_ANY,"Show &Legend",kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnUpdatePlot, self.showLegend)
        self.showLegend.Check(True)
        
        pltoptions = self.plotMenu.Append(wx.ID_ANY, "&Plot Options")
        self.Bind(wx.EVT_MENU,self.OnPlotOptions, pltoptions)
        
        qme = self.fileMenu.Append(wx.ID_EXIT, '&Quit')
        self.Bind(wx.EVT_MENU, self.OnQuit, qme)
        self.Bind(wx.EVT_MENU,self.OnSavePlot,qms)
        
        self.menubar.Append(self.fileMenu, '&File')
        self.menubar.Append(self.plotMenu, '&Plot')
        self.SetMenuBar(self.menubar) 
        
    def setWindow(self):
        """create main panel"""
    
        self.SetTitle("SMP Superposition Viewer")
        self.SetMinSize((600,400))
        self.Centre()
        self.Maximize()
        self.Show()
        
    def createPanel(self):
        
        self.panelPlot = wx.Panel(self)
        self.panelPlot.SetFocus()
        
        self.list = ulc.UltimateListCtrl(self.panelPlot, agwStyle=wx.LC_REPORT|wx.LC_VRULES|wx.LC_HRULES|wx.LC_SINGLE_SEL|ulc.ULC_HAS_VARIABLE_ROW_HEIGHT)
        
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.canvas = FigCanvas(self.panelPlot, -1, self.fig)
        self.axes = self.fig.add_subplot(111)     
               
        self.plot_toolbar = NavigationToolbar(self.canvas)
        self.plot_toolbar.DeleteToolByPos(8) #delete save, subplot and spacer from tool bar
        self.plot_toolbar.DeleteToolByPos(7)
        self.plot_toolbar.DeleteToolByPos(6)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.canvas, 10, wx.LEFT | wx.TOP | wx.GROW)
        vbox.Add(self.plot_toolbar, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(self.list,3, wx.LEFT | wx.TOP | wx.GROW)
        
        self.panelPlot.SetSizer(vbox)
        vbox.Fit(self)
 
    def createList(self):
        """List Elements"""
               
        #colums
        self.list.InsertColumn(0,"File Name")
        self.list.InsertColumn(1,"active")
        self.list.InsertColumn(2,"Offset x [mm]")
        self.list.InsertColumn(3,"Offset y [N]")
        self.list.InsertColumn(4, "x Stretch Factor")
        self.list.InsertColumn(5,"Smooth")
        self.list.InsertColumn(6,"Color")
        self.list.InsertColumn(7,"Style")
        self.list.InsertColumn(8,"Width")
        
        self.list.SetColumnWidth(0,500)
        self.list.SetColumnWidth(1,-2)
        self.list.SetColumnWidth(2,150)
        self.list.SetColumnWidth(3,150)
        self.list.SetColumnWidth(5,150)
        
        #entries
        for item in self.files:
            self.addItem(item)
    
    def addItem(self,item):
        colors=["blue","black","green","red","yellow","orange","pink","purple","brown",
                "gray","darkblue","silver","darkgreen","darkred","gold"]
        styles=["-","-.",":","steps","--","_"]
        #create elements
        i = self.list.GetItemCount()
        index = self.list.InsertStringItem(i, item.filename)
        box = wx.CheckBox(self.list)
        box.SetValue(True)
        dx  = FloatSpin(self.list,-1,value=- item.surface,min_val=-500.000,max_val=500.000,increment=1,digits=2)
        dy  = FloatSpin(self.list,-1,value=0.000,min_val=-50.00,max_val=50.00,increment=0.01,digits=2)
        stretch = FloatSpin(self.list,-1,value=1,min_val=0.5,max_val=1.5,increment=0.001,digits=3)
        smooth = wx.SpinCtrl(self.list,-1,min=0,max=2000,initial=200)
        color = wx.ComboBox(self.list, -1, choices=colors, style=wx.CB_READONLY,value=colors[i%len(colors)])
        style = wx.ComboBox(self.list, -1, choices=styles, style=wx.CB_READONLY,value="-")
        width = wx.SpinCtrl(self.list, -1,name="Width",initial=1,min=1,max=10)
        
        #append elements to files properties
        item.index = index
        item.box = box
        item.dx = dx
        item.dy = dy
        item.stretch = stretch
        item.smooth = smooth
        item.color = color
        item.style = style
        item.width = width
        
        #append elements to list
        self.list.SetItemWindow(index,1,item.box,expand=True)
        self.list.SetItemWindow(index,2,item.dx,expand=True)
        self.list.SetItemWindow(index,3,item.dy,expand=True)
        self.list.SetItemWindow(index,4,item.stretch,expand=True)
        self.list.SetItemWindow(index,5,item.smooth,expand=True)
        self.list.SetItemWindow(index,6,item.color,expand=True)
        self.list.SetItemWindow(index,7,item.style,expand=True)
        self.list.SetItemWindow(index,8,item.width,expand=True)
        
        #set events to update plot
        self.Bind(wx.EVT_CHECKBOX, self.OnUpdatePlot, item.box)
        self.Bind(wx.EVT_SPINCTRL, self.OnUpdatePlot, item.dx)
        self.Bind(wx.EVT_SPINCTRL, self.OnUpdatePlot, item.dy)
        self.Bind(wx.EVT_SPINCTRL, self.OnUpdatePlot, item.stretch)
        self.Bind(wx.EVT_SPINCTRL, self.OnUpdatePlot, item.smooth)
        self.Bind(wx.EVT_COMBOBOX, self.OnUpdatePlot, item.color)
        self.Bind(wx.EVT_COMBOBOX, self.OnUpdatePlot, item.style)
        self.Bind(wx.EVT_SPINCTRL, self.OnUpdatePlot, item.width)
                
    def draw_figure(self,autozoom=False):
        """draw active files"""
        
        self.setPlotOptions(autozoom) 
        active = 0
        for i in range(len(self.files)):
            current = self.files[i]
            if current.box.GetValue():
                    active += 1
                    x,y = self.adaptData(current)
                    self.axes.plot(x, y,
                                   color = current.color.GetValue(),
                                   linestyle = current.style.GetValue(),
                                   linewidth = current.width.GetValue(),
                                   label = basename(current.filename)
                                   )                       
           
        
        self.canvas.draw()
        
        self.plotMenu.Enable(100,active >= 2)
        
    def setPlotOptions(self, autozoom=False):  
    
        if autozoom:
            xlim = self.axes.get_xlim()
            ylim = self.axes.get_ylim()
            self.axes.clear()
            self.axes.set_xlim(xlim)
            self.axes.set_ylim(ylim)
        else:
            self.axes.clear()
            if not self.Options.auto_x:
                self.axes.set_xlim(self.Options.xlim[0],self.Options.xlim[1]) 
        
            if not self.Options.auto_y:
                self.axes.set_ylim(self.Options.ylim[0],self.Options.ylim[1]) 
        
        if not self.Options.auto_yticks:
            self.axes.yaxis.set_major_locator(MaxNLocator(self.Options.yticks))
        if not self.Options.auto_xticks:
            self.axes.xaxis.set_major_locator(MaxNLocator(self.Options.xticks))

        self.axes.grid(True)
        
        self.axes.tick_params(labeltop=self.Options.mirrorx,labelright=self.Options.mirrory)
        
        self.axes.set_xlabel(self.Options.xlabel)  
        self.axes.set_ylabel(self.Options.ylabel)

        self.axes.set_title("SMP Super Position Viewer") 
        
        if self.showLegend.IsChecked():
            print "show legend"
            self.axes.legend(loc = "upper left")
        
    def OnUpdatePlot(self,e):      
        self.draw_figure(True)
        
    def OnAddItem(self,e):
        files = openFile()
        if files != None:
            for entry in files:
                item = smp.Pnt(entry)
                self.addItem(item)
        self.drawPlot()
        
    def OnSavePlot(self,e):
        """Save Plot Event"""
        
        file_choices = "PNG (*.png)|*.PNG"
        filename = "_SuperPos.png"
        
        dlg = wx.FileDialog(
            self, 
            message = "Save Plot as...",
            defaultDir = os.getcwd(),
            defaultFile = filename,
            wildcard = file_choices,
            style = wx.SAVE|wx.OVERWRITE_PROMPT)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            
        dlg.Destroy()      
    
    def OnSaveData(self,e):
        wx.MessageBox('Not implemented yet', 'Info', 
                            wx.OK | wx.ICON_INFORMATION)
        lines = self.axes.lines
        """
        data = []
        for line in lines:
            data.append(line.get_data())
        
        np.savetxt(fname = "/home/grimm/Desktop/test.txt", 
                   X = np.array(data),
                   fmt = '%.18e',
                   delimiter = '\t',
                   newline = '\n',
                   header = '# Automatic written file from SMP SUper Position Viewer',
                   comments='# ')
    
        """
    
    def OnPlotOptions(self,e):
        self.Options.Show()
            
    def OnSubtract(self,e):
        choices = []
        files = []
        for entry in self.files:
            if entry.box.GetValue():
                choices.append(os.path.basename(entry.filename))
                files.append(entry)
                
        dlg = wx.SingleChoiceDialog(parent = self,
                                    message = "select reference",
                                    caption = "Subtract Plots",
                                    choices = choices,
                                    )
        
        if dlg.ShowModal() == wx.ID_OK:
            ref = files[dlg.GetSelection()]
            files.pop(dlg.GetSelection())
            xref, yref = self.adaptData(ref)
            fref = interp1d(xref,yref)
            xref_min = np.min(xref)
            xref_max = np.max(xref)
            
            for entry in files:
                xsub, ysub = self.adaptData(entry)
                fsub = interp1d(xsub,ysub)
                xsub_min = np.min(xsub)
                xsub_max = np.max(xsub)
                
                if xsub_min >= xref_min: xmin = xsub_min
                else:                    xmin = xref_min
                if xsub_max >= xref_max: xmax = xref_max
                else:                    xmax = xsub_max                              
                
                x_new = np.arange(xmin,xmax,0.1)
                f_ref = fref(x_new)
                f_sub = fsub(x_new)
                y_new =  f_ref - f_sub
                
                rsme = calc.rsme(f_ref, f_sub)
                                              
                self.axes.plot(x_new, y_new,
                               linestyle = "--",
                               color = entry.color.GetValue(),
                               label = basename(entry.filename) + " - " + basename(ref.filename) + ", rsme = %0.3g" %rsme)
                              
        self.axes.legend(loc = "upper left")
        self.axes.autoscale(False)
        self.canvas.draw()
        dlg.Destroy()
        
    def OnMean(self,e):
            #get prepared data
            data = []
            for entry in self.files:
                if entry.box.GetValue():
                    data.append(self.adaptData(entry))
                    
            
            #find common range
            xmins = []
            xmaxs = []               
            for entry in data:
                xmins.append(entry[0][0])
                xmaxs.append(entry[0][-1])
                
            xmin = np.amax(xmins)
            xmax = np.amin(xmaxs)
            x_new = np.arange(xmin,xmax,0.004)
            y_new = []
            #interpolate data to get same number of data points
            for entry in data:
                fint = interp1d(entry[0],entry[1])
                y_new.append(fint(x_new)) 
            y_new = np.transpose(np.array(y_new))
            y_mean = np.mean(y_new,1)        
            
            #plot average
            self.setPlotOptions()
            
            self.axes.plot(x_new, y_mean,
                               linestyle = "-",
                               color = "r",
                               label = "mean")
                              
            self.canvas.draw()
  
    def adaptData(self, pnt):
        x_corrected = (calc.downsample(pnt.data[:,0],pnt.smooth.GetValue()) + pnt.dx.GetValue()) * pnt.stretch.GetValue()
        y_corrected = calc.downsample(pnt.data[:,1],pnt.smooth.GetValue()) + pnt.dy.GetValue()
        return x_corrected,y_corrected
    
    def OnQuit(self,e):
        self.Destroy()
        
if __name__ == "__main__":  
    
    app = wx.App(False)
    window = GraphOptions()
    window.ShowModal()
    app.MainLoop()