# Mega Man ZX Editor
> <img src="https://github.com/AlaryVanEeckhout/Mega_Man_ZX_Editor/blob/main/GitHub-page-content/Showcase-GUI.png" /><br>Graphic User Interface of the editor

> <img src="https://github.com/AlaryVanEeckhout/Mega_Man_ZX_Editor/blob/main/GitHub-page-content/Showcase-Dialogue.gif" /><br>Edited dialogue file (talk_m01_en1.bin) in-game

> <img src="https://github.com/AlaryVanEeckhout/Mega_Man_ZX_Editor/blob/main/GitHub-page-content/Showcase-Dialogue-ZXA.png" /><br>Edited dialogue file (talk_m01_en1.bin) in Mega Man ZX Advent
## What this is
This is a tool I created in an attempt to make editing Mega Man ZX much easier.<br>
If you need to know where specific assets, values, or code sections are in the game, please see the (unfinished) [wiki page](https://github.com/AlaryVanEeckhout/Mega_Man_ZX_Editor/wiki), as it contains documentation I accumulated on the game.
## Progress
Currently, I am focusing on the USA version of Mega Man ZX. This means that the editor's (full) compatibility with other versions of the game is not guarenteed at the moment (although, it's worth noting that MMZXA has the same dialogue system as MMZX, and as such, the dialogue editor works for both games).<br>
The editor can edit, export and import english dialogue files and save them to the ROM. Other files can be viewed but I have not yet implemented the code to view and/or edit most of them in their converted format.
### Done
- Dialogue text converter (for dialogue "talk_" and message "m_" files)
- Functional User Interface
- File export with options for converted file formats (WIP)
- File import with support for converted file formats (WIP)
- Togglable patches system
- Playtest button
- Graphics Editor (WIP)
- SDAT Viewer (WIP)
- ARM Viewer (WIP)
### To do
- VX Export/Import to/from video format
- Graphics Editor additional features (exporting and importing)
- Find actual patches for the game to add to the editor's "patches" tab*
- Find patches and tweaks that are helpful for playtesting purposes*
- Level Editor*
- Sound/Music Editor*
- Tweaks/Physics Editor*
- OAM Editor*
- Game Logic Editor*
<!---
- 3D Model Viewer and Exporter/Importer*
- In-game Cutscene Editor*
-->

*This feature may not be implemented/is not currently prioritized since I haven't looked into it and/or it looks/is hard to do. 
## Setup for usage
Currently, there are no releases, so:
- [Download&Install Python](https://www.python.org/downloads/) (using 3.13.2)
- Now that you have Python, you can use pip (Package Installer for Python) to install the two following modules:
- [Download&Install NDSPy](https://pypi.org/project/ndspy/) (using 4.2.0)
- [Download&Install PyQt6](https://pypi.org/project/PyQt6/) (using 6.8.1)
- [Download&Install NumPy](https://pypi.org/project/numpy/) (submodule dependency)
- [Download&Install Pillow](https://pypi.org/project/Pillow/) (submodule dependency)
- This project > Code > Download ZIP
- Extract the contents of the .zip file wherever you want
- That's it! Now you can run RunEditor.bat (or run MME_NDS.py directly, from command line)
## Credits
- Filesystem handling: https://ndspy.readthedocs.io/en/latest/
- GUI (PyQt6): https://www.riverbankcomputing.com/software/pyqt/
- Icons: https://p.yusukekamiyamane.com/
- appicon.ico: Mega Man ZX devs, taken from [here](https://www.spriters-resource.com/ds_dsi/megamanzx/sheet/180723/) and truncated by me using GIMP
- This project uses a [submodule](https://github.com/CharlesVanEeckhout/actimagine)

Some parts of code I copied (and modified) from answers to other people who asked for help (for example, on stack overflow) on topics I myself needed help on.
### Special Thanks
- My brother, who assisted me in the development of most editor features