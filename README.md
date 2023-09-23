# Mega_Man_ZX_Editor
## What this is
 This is an attempt at creating a tool that will make editing Mega Man ZX much easier.<br>
 If you need to know where specific assets, values, or code sections are in the game, please see the(unfinished) [wiki page](https://github.com/AlaryVanEeckhout/Mega_Man_ZX_Editor/wiki), as it contains documentation I accumulated on the game.
## Progress
Currently, the editor can edit english dialogue files and save them to the ROM. Other files can be viewed but I have not yet implemented the code to view them in their converted format.<br>
For now, I'm working on the editor's GUI and import/export features.
### Done
- Dialogue text converter
- Functional User Interface
### Todo
- Proper export/import with options for file formats
- Insert file feature
- Sprite Editor
- Sound/Music Editor*
- Movie Editor*
- Physics Editor*
- Level Editor*
- Game Logic Editor*

*This feature may not be implemented/is not currently prioritized since I haven't looked into it and it looks hard to do at first glance. 
## Setup for usage
Currently, there are no releases and I'm not sure how to include the dependencies in my project, so:
- [Download&Install Python](https://www.python.org/downloads/)
- Now that you have Python, you can use pip(Package Installer for Python) to install the two following modules:
- [Download&Install NDS Py](https://pypi.org/project/ndspy/)
- [Download&Install PyQt6](https://pypi.org/project/PyQt6/)
- This project > Code > Download ZIP
- Extract the contents of the .zip file to a folder wherever you want
- That's it! Now you can run RunEditor.bat (or run MME_NDS.py, from command line)
## Credits
- Rom extracting/saving : https://ndspy.readthedocs.io/en/latest/
- GUI(PyQt6) : https://www.riverbankcomputing.com/software/pyqt/
- Icons : https://p.yusukekamiyamane.com/
- icon_biometals-creation.png : Mega Man ZX devs, taken from [here](https://www.spriters-resource.com/ds_dsi/megamanzx/sheet/180723/)
