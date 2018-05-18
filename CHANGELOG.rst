snowmicropyn Changelog
======================

Version 0.1.0a1
---------------

NOT YET RELEASED

Huge overhaul of snowmicropyn including:
- Restructuring/Rewrite of code base.
- Deployment as package on PyPI.
- Source code repository moved to GitHub.
- Documentation (using Sphinx), publishing on Read the Docs.
- New UI called "snowmicropyn pyngui".

Pre Overhaul Changelog
----------------------

2018-02-XX

- Version 0.0.26 alpha
- Python packaging
- Packaging for Anaconda (conda recipe)

????-??-??

- Version 0.0.25 alpha
- Man kann jetzt unter Menu -> View -> Show Density oder -> Show SSA
  auswählen
- Dann wird SSA oder Dichte mit zweiter y-Achse geplottet.

????-??-??

- Version 0.0.24 alpha
- Show surface und show ground default-mässig aktiviert
- MessageBox wenn versucht wird SSA und Density gleichzeitig zu plotten
  (geht nur einzeln)
- Im Menu Export->shot noise parameters geändert zu Export
  -> ShotNoiseParameters, Density and SSA

????-??-??

- Version 0.0.23 alpha
- Dichte- oder SSA-profil in plot zeichnen
- Beim öffnen der files werden shotnoiseparameter für jedes file
  berechnet, daher etwas langsamer beim öffnen (vor allem bei vielen
  dateien)
- Range für zweite y-Achse festgelegt: Dichte: 0-700 kg/m^3. SSA: 0-60
  m^2/kg.

????-??-??

- Version 0.0.22 alpha
- Shotnoise parameter in file schreiben inklusive dichte und ssa

????-??-??

- Version 0.0.21 alpha
- Shotnoise-auswertung von evalSMP-skript hier reinkopiert und etwas
  angepasst
- Zusätzlich dichte und ssa ausrechnen und alles ins shotnoise-file
  schreiben
- Ausserdem default-filename und -ordner für shotnoise-file geändert:
  Jetzt gleichen namen und ordner wie pnt-file nur andere endung

2014-07-10

- Version 0.0.19 alpha
- Allowed negative and comma values for axes in graph options
- New variable self.pathOpen as default file opening path (location of
  last opened file)
- New variable self.pathSave as default save path

2014-04-29

- GPS coordinates sign bug fixed
- Fixed bug, where noise, drift offset could not be shown

2014-04-04

- Implemented options for subtracted median in options window
- Implemented shot noise and added shot noise save options

2014-04-02

- Fixed surface tool visibility bug
- Introduced overwrite prompt to some save functions
- Arrow keys can be used to switch plot
- Fixed indexing bug in shotnoise()

2014-04-01

- Improved mean.py
- Introduced view menu, exported functions from data menu

2014-03-28

- Use scroll wheel to zoom in/out of plot
- Up/down/left/right to navigate through open files
- Ctrl+ left click moves surface to location
- Shift + left click moves ground to location

2014-03-27

- Implemented average menu to data (/extensions/mean.py)
- Started to use click event on canvas
- Left click on plot shows x//y coordinates

2014-03-24

- Implemented average curves to superposition viewer
- Implemented log for y axis to graph options, default = True
- Implemented subtract median to view menu

2014-03-21

- Call class graphoptions with .show() -> parent.draw_figure actualizes
  parent plot

2014-03-20

- Version 0.0.14 alpha
- Add ground level analog to surface
- Add overload to info screen

2014-03-17

- Version 0.0.13 alpha
- Add option to hide legend in super position viewer

2014-03-16

- Implemented graph options to super position viewer
- Hide surface tool if not checked
- Get_surface returns now max instead of a rounded value, if no surface
  was found
- Created a pyinstaller build script to create build archives

2014-02-24

- Bug fix in OnClose()

2014-02-21

- Renamed software to SnowMicroPyn

2014-02-19

- Fixed bug in export surface
- Fixed surface tool bug

2014-02-18

- Additions in Super Position Viewer:
  - Subtract plot has same color as corresponding curve
  - Legend for subtracted graphs
  - RSME is shown mathematics.rsme(x_ref,x_sub, norm)

2014-02-17

- Version 0.0.11 alpha
- Fixed surface tool inactivation bug for windows
- Maximize super position viewer at start
- Deactivated surface tab in graph options
- Cancel possibility in GPS viewer if no coordinates available
- Precision option in save options for ascii data
- Enabled keyboard short cuts for windows
- Correct exec_path detection (for exe)

2014-02-16

- Version 0.0.10 alpha
- Super position viewer: show only basename in reference selection
- Fixed bug in file number text control in tool bar
- Use Ubuntu icons for tool bar in all operating systems

2014-02-15

- Changed standard gradient down sampling factor to 1000

2014-02-10

- Fixed logo location bug

2014-02-10

- Changed version to 0.0.9 alpha
- Changed getsurface algorithm

2014-02-08

- Improved filter function

2014-02-08

- Implemented experimental butterworth low pass filter and automatic cut
  off frequency search using residual analysis

2014-02-07

- Upgrade to 0.0.8 alpha
- Implemented open files as command line arguments -> "open with"
- Implemented error caching to open file function
- Reneamed pnt header dict keys with units -> header infos contain units
- Cleaned code in smp.py
- Introduced savezoom() to updatefigure()
- Disable preferences when no file is loaded

2014-02-06

- Upgraded version to 0.0.7 alpha
- Implemented auto zoom boolean to draw_plot -> zoom ratio is kept when
  changing preferences
- Implemented gradient to analysis menu
- Better surface detection algorithm
- Implemented new surface detection algorithm based on 2nd deviation
- Fixed bug: smooth in Super Position Viewer works now
- Removed subplot from navigation tool bar
- Added additional tabs and options to graph options
- Implemeted manual surface correction to tool bar
- Outsourced getsurface to mathematics.py
- Outsourced linfit to mathematics.py
- Implemented "keep zoom"
- Added legend to super position viewer

2014-02-04

- Improved getData from smp.py
- Replaced smooth with downsample in getsurface
- Introduced arg boolean "show" to draw_plot -> circumvents double
  plotting while saving plot
- Implemented "subtract plot" to SuperPosition
- Improved surface detection

2014-02-03

- Update version to 0.0.6 alpha
- New class SuperPosition in menus.py
- Introduced SuperPosition (not fully developed yet) to data menu

2014-02-02

- Added more colors and styles to plot options
- Moved class checklstctr from map to menus

2014-01-31

- Changed version number to 0.0.5 alpha
- Introduced new graph options windows with enhanced functionality.

2014-01-30

- Changed "preferences" to "graph options" and moved to data menu
- Renamed "view" to "analysis"
- Introduced save options to single file save method
- Changed graph options tool bar icon
- Changed quit icon to cross mark (probably nicer in windows)
- Renamed "Map" to "GPS Map View"
- Removed "save" from mpl tool bar
- Introduced save all and save single to tool bar
- New save options menu using wx.multichoice dialog in menus.py

2014-01-29

- Corrected SLF institute labels
- Tool bar info button now shows header instead of license
- Deactivated next/prev buttons in tool bar, if no file is open
- Decoupled "max force" off surface
- Changed export "max force and penetration" to "max force and surface"
- Added text in plot to autom. surface and max force detection
- Fixed bug, where prev button jumped over a measurement
- Setup plot renamed to graph options

2014-01-24

- Changed version number to 0.0.4 alpha
- Introduced error catching for icon and logo
- Improved down  sampling function
- Removed automatic y axis restriction for plots

2014-01-20

- Removed icon call from main function in PyNTReader.py

2014-01-17

- Add standard deviation to noise, drift and offset export function
- Labels in map.py repeat now, if num lables > num ascii_uppercase

2014-01-16

- Changed version to 0.0.3 alpha
- Corrected save path in export functions due to incompatibility in
  MacOS
- Fixed bug: noise and drift works again without surface option being
  checked in menu

2014-01-15

- Deleted unused import urllib
- Use wx.App(False) instead of deprecated wx.PySimpleApp()
- Tested program under wxPython 3.0.0
- Export coordinates as .coords instead of .txt
- Excluded "hardness test" from data menu (former used by team snow
  sports)
- Introduced plot update after noise data export
- Moved options button from mpl tool bar to custom tool bar due to
  compatibility issues in windows
- Introduced plot options menu to file menu
- Linked slf.ch to license
- Created icon.ico as task bar icon
- Actualized requirements.txt
- In maps SLF location is shown if no coordinates present

2014-01-13

- Changed PyNTReader version number to 0.0.2 alpha.
- Introduced class SaveOptions to menus.py
- OnSaveAll calls SaveOptions
- In map.py items can't be checked anymore if GPS off
- Introduced experimental feature
  "app.SetMacSupportPCMenuShortcuts(True)" and OS detection in main
  function -> not tested yet

2014-01-12

- Introduced file selection drop down list to tool bar
- Introduced down sampling factor to plot options
- Introduced array down sampling function to mathematics.py
- Cleaned and documented code

2014-01-09

- (P)released PyNTReader version 0.0.1 alpha
