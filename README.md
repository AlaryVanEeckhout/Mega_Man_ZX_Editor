# Mega Man ZX Editor
<img src="https://github.com/AlaryVanEeckhout/Mega_Man_ZX_Editor/blob/main/GitHub-page-content/Showcase-GUI.png" /><br>Graphic User Interface of the editor<br>
<img src="https://github.com/AlaryVanEeckhout/Mega_Man_ZX_Editor/blob/main/GitHub-page-content/Showcase-Dialogue.gif" /><br>Edited dialogue file(talk_m01_en1.bin) in-game<br>
<img src="https://github.com/AlaryVanEeckhout/Mega_Man_ZX_Editor/blob/main/GitHub-page-content/Showcase-Dialogue-ZXA.png" /><br>Edited dialogue file(talk_m01_en1.bin) in Mega Man ZX Advent<br>
## What this is
This is an attempt at creating a tool that will make editing Mega Man ZX much easier.<br>
If you need to know where specific assets, values, or code sections are in the game, please see the(unfinished) [wiki page](https://github.com/AlaryVanEeckhout/Mega_Man_ZX_Editor/wiki), as it contains documentation I accumulated on the game.
## Progress
Currently, I am focusing on the USA version of Mega Man ZX. This means that the editor's (full) compatibility with other versions of the game is not guarenteed at the moment(although, it's worth noting that MMZXA has the same dialogue system as MMZX, and as such, the dialogue editor works for both games).<br>
The editor can edit, export and import english dialogue files and save them to the ROM. Other files can be viewed but I have not yet implemented the code to view and/or edit them in their converted format.<br>
For now, I'm making controlled and measured corruptions to the game to better understand how the different files work.
### Done
- Dialogue text converter(for dialogue "talk_" and message "m_" files)
- Functional User Interface
- File export with options for converted file formats(except graphics)
- File import with support for converted file formats(except graphics)
- Converter for binary to pyqt widget(image)
- Togglable patches system
- Test button
- Graphics Viewer(WIP)
- SDAT Viewer(WIP)
### To do
- Graphics Editor(saving, exporting, and importing)
- Find actual patches for the game to add to the editor's "patches" tab
- Find patches and tweaks that are helpful for testing purposes
- OAM Editor*
- Sound/Music Editor*
- Movie Editor*
- Tweaks/Physics Editor*
- Level Editor*
- Game Logic Editor*
<!---
- 3D Model Editor*
- In-game Cutscene Editor*
-->

*This feature may not be implemented/is not currently prioritized since I haven't looked into it and it looks hard to do at first glance. 
## Setup for usage
Currently, there are no releases and I'm not sure how to include the dependencies in my project, so:
- [Download&Install Python v3.10 or higher](https://www.python.org/downloads/) (made with 3.11.4)
- Now that you have Python, you can use pip(Package Installer for Python) to install the two following modules:
- [Download&Install NDS Py](https://pypi.org/project/ndspy/) (made with 4.1.0)
- [Download&Install PyQt6](https://pypi.org/project/PyQt6/) (made with 6.5.2)
<!---
- [Download&Install NumPy](https://pypi.org/project/numpy/)
- [Download&Install Pillow v9.3.0 or higher](https://pypi.org/project/Pillow/)
-->
- This project > Code > Download ZIP
- Extract the contents of the .zip file wherever you want
- That's it! Now you can run RunEditor.bat (or run MME_NDS.py directly, from command line)
## Credits
- Filesystem handling: https://ndspy.readthedocs.io/en/latest/
- GUI(PyQt6): https://www.riverbankcomputing.com/software/pyqt/
- Icons: https://p.yusukekamiyamane.com/
- appicon.ico: Mega Man ZX devs, taken from [here](https://www.spriters-resource.com/ds_dsi/megamanzx/sheet/180723/) and truncated by me using GIMP

Some parts of code I copied(and modified) from answers to other people who asked for help(for example, on stack overflow) on topics I myself needed help on.
