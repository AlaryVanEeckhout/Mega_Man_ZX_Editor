# Mega_Man_ZX_Editor
## What this is
 This is an attempt at creating a tool that will make editing Mega Man ZX much easier.<br>
 If you need to know where specific assets, values, or code sections are in the game, please see the(unfinished) [wiki page](https://github.com/AlaryVanEeckhout/Mega_Man_ZX_Editor/wiki), as it contains documentation I accumulated on the game.
## Progress
Currently, the editor can edit, export and import english dialogue files and save them to the ROM. Other files can be viewed but I have not yet implemented the code to view them in their converted format.<br>
For now, I'm trying to find and understand data in the game to add it to my wiki page and to have a better idea of how my editor should handle each of the game's files.
### Done
- Dialogue text converter
- Functional User Interface
- File export with options for converted file formats
- File import with support for converted file formats
### Todo
- (Dialogue text converter)Find use of special values 0xF4, 0xF5, 0xF7, 0xF9, 0xFA, and 0xFF
- Graphics converter
- Graphics Editor
- OAM Editor*
- Sound/Music Editor*
- Movie Editor*
- Physics Editor*
- Level Editor*
- Game Logic Editor*

*This feature may not be implemented/is not currently prioritized since I haven't looked into it and it looks hard to do at first glance. 
## Setup for usage
Currently, there are no releases and I'm not sure how to include the dependencies in my project, so:
- [Download&Install Python v3.10 or higher](https://www.python.org/downloads/)
- Now that you have Python, you can use pip(Package Installer for Python) to install the two following modules:
- [Download&Install NDS Py](https://pypi.org/project/ndspy/)
- [Download&Install PyQt6](https://pypi.org/project/PyQt6/)
- This project > Code > Download ZIP
- Extract the contents of the .zip file to a folder wherever you want
- That's it! Now you can run RunEditor.bat (or run MME_NDS.py, from command line)
## Credits
- Rom extracting/saving: https://ndspy.readthedocs.io/en/latest/
- GUI(PyQt6): https://www.riverbankcomputing.com/software/pyqt/
- Icons: https://p.yusukekamiyamane.com/
- icon_biometals-creation.png: Mega Man ZX devs, taken from [here](https://www.spriters-resource.com/ds_dsi/megamanzx/sheet/180723/) and truncated by me using GIMP
- Dark theme: https://raw.githubusercontent.com/NiklasWyld/Wydbid/main/Assets/stylesheet (modified by me)

Some parts of code I copied(and modified) from other people who asked for help(for example: on stack overflow) on topics I myself needed help on.
