from PyQt6 import QtGui, QtWidgets, QtCore, QtMultimedia #Qt6, Qt6.qsci
import sys, os, platform, re, math
import argparse
import bisect
#import logging, time, random
#import numpy
import ndspy
#import ndspy.graphics2D
#import ndspy.model
import ndspy.lz10
import ndspy.rom#, ndspy.code, ndspy.codeCompression
import ndspy.soundArchive
import ndspy.soundSequenceArchive
import lib

parser = argparse.ArgumentParser()
parser.add_argument("-R", "--ROM", help="NDS ROM to open using the editor.", dest="openPath")
args = parser.parse_args()
"""
class ThreadSignals(QtCore.QObject): # signals can omly be emmited by QObject
    valueChanged = QtCore.pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class RunnableDisplayProgress(QtCore.QRunnable):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = ThreadSignals()

    def run(self):
        print("runnable active")
        value = 0
        while value < 100:
            self.signals.valueChanged.emit(value)
            time.sleep(0.5)
            value += 10
        QtCore.QMetaObject.invokeMethod(w.progress, "close", QtCore.Qt.ConnectionType.QueuedConnection)
        QtCore.QMetaObject.invokeMethod(w.progress, "setValue", QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(int, 0))
        print("runnable finish")
"""

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # expected module versions
        self.VERSION_EDITOR = "0.4.4" # objective, feature, WIP
        self.VERSION_PYTHON = "3.13.2"
        self.VERSION_PYQT = "6.9.1"
        self.VERSION_NDSPY = "4.2.0"
        self.window_width = 1024
        self.window_height = 720
        self.setWindowIcon(QtGui.QIcon('icons\\appicon.ico'))
        self.setWindowTitle("Mega Man ZX Editor")
        self.temp_path = f"{os.path.curdir}\\temp\\"
        self.rom = None #ndspy.rom.NintendoDSRom # placeholder definitions
        self.rom_fat = [] # list of file addresses (see loadFat())
        self.sdat = None #ndspy.soundArchive.SDAT
        self.base_address = 0
        self.relative_address = 0
        self.romToEdit_name = ''
        self.romToEdit_ext = ''
        self.fileToEdit_name = ''
        self.fileDisplayRaw = False # Display file in 'raw'(hex) format. Else, displayed in readable format
        self.fileDisplayMode = "Adapt" # Modes: Adapt, Binary, English dialogue, Japanese dialogue, Graphics, Font, Sound, Movie, Code
        self.fileDisplayState = "None" # Same states as mode
        self.widget_set = "Empty" # Empty, Text, Graphics, Font, Sound, VX
        self.GFX_PALETTES = [
            [0xff000000+((0x0b7421*i)%0x1000000) for i in range(256)], # default
            [0xff000000, 0xffffffff]*128, # font
            [0xff639c6b, 0xff426b9c, 0xff42a5c6, 0xff84c6e7, 0xffbdefff, 0xffdeffef, 0xffb58cff, 0xffefc6ff, # generic
             0xffffdeff, 0xfff70010, 0xfff76310, 0xfff79410, 0xfff7c600, 0xfff7f710, 0xfff7f794, 0xffffffff,
             0xff7b8463, 0xff102163, 0xff395294, 0xff949cc6, 0xffd6def7, 0xffffffff, 0xff9c0029, 0xfff7394a, # ZX
             0xffff9484, 0xff108c73, 0xffffce18, 0xffffff8c, 0xffffd6bd, 0xffd68410, 0xff8c4a00, 0xff39e7c6,
             0xff000000, 0xffc6f7ff, 0xffbdd6ff, 0xffa5adf7, 0xff8c7be7, 0xff7352de, 0xff5a29ce, 0xff4200c6, # PX shield
             0xff6b10ce, 0xff8c21de, 0xffb531ef, 0xffde4aff, 0xfff763ff, 0xffff9cff, 0xffffd6ff, 0xffffffff,
             0xff000000, 0xffc6f7ff, 0xffbdd6ff, 0xffa5adf7, 0xff8c7be7, 0xff7352de, 0xff5a29ce, 0xff4200c6, # PX shield
             0xff6b10ce, 0xff8c21de, 0xffb531ef, 0xffde4aff, 0xfff763ff, 0xffff9cff, 0xffffd6ff, 0xffffffff]*4, # sprites
            [0xff000000+((0x010101*i)%0x1000000) for i in range(256)], # face
        ]
        self.gfx_palette = self.GFX_PALETTES[0]
        self.fileEdited_object = None
        self.levelEdited_object = None
        self.resize(self.window_width, self.window_height)
        # Default Preferences
        self.theme_index = 0
        self.displayBase = 16
        self.displayBase_old = 16
        self.displayAlphanumeric = True
        self.firstLaunch = True
        self.load_preferences()
        self.UiComponents()
        self.show()
        if args.openPath != None:
            self.loadROM(args.openPath)

    def load_preferences(self):
        #SETTINGS
        lib.ini_rw.read(self, "SETTINGS", property_type="int", exc=["displayAlphanumeric"])
        lib.ini_rw.read(self, "SETTINGS", property_type="bool", inc=["displayAlphanumeric"])
        #MISC
        lib.ini_rw.read(self, "MISC", property_type="bool")
        if self.firstLaunch:
            firstLaunch_dialog = QtWidgets.QMessageBox()
            firstLaunch_dialog.setWindowTitle("Mega Man ZX Editor - First Launch")
            firstLaunch_dialog.setWindowIcon(QtGui.QIcon('icons\\information.png'))
            firstLaunch_dialog.setTextFormat(QtCore.Qt.TextFormat.MarkdownText)
            firstLaunch_dialog.setText(f"""Thank you for trying out Mega Man ZX Editor!
                                       \rThe current version is {self.VERSION_EDITOR}."""
                                       )
            firstLaunch_dialog.setInformativeText(f"""Editor's current features ({self.VERSION_EDITOR.split('.')[1]}):
                                                  \r- English dialogue text editor
                                                  \r- Patcher(no patches available yet)
                                                  \r- Graphics editor
                                                  \r- Font editor

                                                  \rWIP ({self.VERSION_EDITOR.split('.')[2]}):
                                                  \r- Sound data editor
                                                  \r- VX file editor
                                                  \r- OAM editor
                                                  \r- Level editor""")
            #firstLaunch_dialog.setDetailedText("abc")
            firstLaunch_dialog.exec()

    def widgetIcon_update(self, widget: QtWidgets.QWidget, checkedicon: QtGui.QImage, uncheckedicon: QtGui.QImage):
        if widget.isChecked():
            widget.setIcon(checkedicon)
        else:
            widget.setIcon(uncheckedicon)

    def UiComponents(self):
        # reusable
        self.window_progress = QtWidgets.QMdiSubWindow()
        self.window_progress.setWindowFlags(QtCore.Qt.WindowType.Window | QtCore.Qt.WindowType.CustomizeWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.FramelessWindowHint)
        self.window_progress.resize(250, 35)
        self.window_progress.setWindowTitle("Progress")
        #self.window_progress.layout().addWidget(self.label_progress)

        self.progress = QtWidgets.QProgressBar(self.window_progress)

        self.label_progress = QtWidgets.QLabel(self.window_progress)

        self.window_progress.layout().addWidget(self.progress)
        self.window_progress.layout().addWidget(self.label_progress)
        # Menus
        self.openAction = QtGui.QAction(QtGui.QIcon('icons\\folder-horizontal-open.png'), '&Open', self)        
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.setStatusTip('Open ROM')
        self.openAction.triggered.connect(self.openCall)

        self.exportAction = QtGui.QAction(QtGui.QIcon('icons\\blueprint--arrow.png'), '&Export...', self)        
        self.exportAction.setShortcut('Ctrl+E')
        self.exportAction.setStatusTip('Export file in binary or converted format')
        self.exportAction.triggered.connect(lambda: self.exportCall(self.tree.currentItem()))
        self.exportAction.setDisabled(True)

        self.replaceAction = QtGui.QAction(QtGui.QIcon('icons\\blue-document-import.png'), '&Replace...', self)
        self.replaceAction.setShortcut('Ctrl+R')
        self.replaceAction.setStatusTip('Replace with file in binary or converted format')
        self.replaceAction.triggered.connect(lambda: self.replaceCall(self.tree.currentItem()))
        self.replaceAction.setDisabled(True)

        self.replacebynameAction = QtGui.QAction(QtGui.QIcon('icons\\blue-document-import.png'), '&Replace by name...', self)        
        self.replacebynameAction.setStatusTip('Replace with file of same name in binary or converted format')
        self.replacebynameAction.triggered.connect(self.replacebynameCall)

        self.menu_bar = self.menuBar()
        self.fileMenu = self.menu_bar.addMenu('&File')
        self.fileMenu.addActions([self.openAction, self.exportAction])
        self.importSubmenu = self.fileMenu.addMenu('&Import...')
        #self.importSubmenu.setStatusTip('Use external file to replace a file in ROM')
        self.importSubmenu.setIcon(QtGui.QIcon('icons\\blue-document-import.png'))
        self.importSubmenu.addActions([self.replaceAction, self.replacebynameAction])
        self.importSubmenu.setDisabled(True)


        self.dialog_about = QtWidgets.QDialog(self)
        self.dialog_about.setWindowIcon(QtGui.QIcon('icons\\information.png'))
        self.dialog_about.setWindowTitle("About Mega Man ZX Editor")
        self.dialog_about.resize(500, 500)
        self.text_about = QtWidgets.QTextBrowser(self.dialog_about)
        self.text_about.resize(self.dialog_about.width(), self.dialog_about.height())
        self.text_about.setText(f"""Supports:\
                                \rMEGAMANZX (Mega Man ZX)\
                                \rMEGAMANZXA (Mega Man ZX Advent)\

                                \rVersionning:\
                                \rEditor version: {self.VERSION_EDITOR} (final objective(s) completed, major functional features, WIP features)\
                                \rPython version: {self.VERSION_PYTHON} (your version is {platform.python_version()})\
                                \rPyQt version: {self.VERSION_PYQT} (your version is {QtCore.PYQT_VERSION_STR})\
                                \rNDSPy version: {self.VERSION_NDSPY} (your version is {list(ndspy.VERSION)[0]}.{list(ndspy.VERSION)[1]}.{list(ndspy.VERSION)[2]})""")
        self.aboutAction = QtGui.QAction(QtGui.QIcon('icons\\information.png'), '&About', self)
        self.aboutAction.setStatusTip('Show information about the application')
        self.aboutAction.triggered.connect(lambda: self.dialog_about.exec())

        self.dialog_settings = QtWidgets.QDialog(self)
        self.dialog_settings.setWindowTitle("Settings")
        self.dialog_settings.resize(100, 50)
        self.dialog_settings.setLayout(QtWidgets.QGridLayout())
        self.label_theme = QtWidgets.QLabel("Theme", self.dialog_settings)
        self.dropdown_theme = QtWidgets.QComboBox(self.dialog_settings)
        self.dropdown_theme.addItems(QtWidgets.QStyleFactory.keys())
        self.dropdown_theme.addItem("Custom")
        self.switch_theme(True)# Update theme dropdown with current option
        self.dropdown_theme.activated.connect(lambda: self.switch_theme())
        self.label_base = QtWidgets.QLabel("Numeric Base", self.dialog_settings)
        self.field_base = QtWidgets.QSpinBox(self.dialog_settings)
        self.field_base.setValue(self.displayBase)
        self.field_base.setRange(-1000, 1000)
        self.field_base.editingFinished.connect(lambda: setattr(self, "displayBase", self.field_base.value()))
        self.field_base.editingFinished.connect(self.reloadCall)
        self.label_alphanumeric = QtWidgets.QLabel("Alphanumeric Numbers", self.dialog_settings)
        self.checkbox_alphanumeric = QtWidgets.QCheckBox(self.dialog_settings)
        self.checkbox_alphanumeric.setChecked(self.displayAlphanumeric)
        self.checkbox_alphanumeric.toggled.connect(lambda: setattr(self, "displayAlphanumeric", not self.displayAlphanumeric))
        self.checkbox_alphanumeric.toggled.connect(self.reloadCall)
        self.dialog_settings.layout().addWidget(self.label_theme)
        self.dialog_settings.layout().addWidget(self.dropdown_theme)
        self.dialog_settings.layout().addWidget(self.label_base)
        self.dialog_settings.layout().addWidget(self.field_base)
        self.dialog_settings.layout().addWidget(self.label_alphanumeric)
        self.dialog_settings.layout().addWidget(self.checkbox_alphanumeric)

        self.settingsAction = QtGui.QAction(QtGui.QIcon('icons\\gear.png'), '&Settings', self)
        self.settingsAction.setStatusTip('Settings')
        self.settingsAction.triggered.connect(lambda: self.dialog_settings.exec())

        self.exitAction = QtGui.QAction(QtGui.QIcon('icons\\door.png'), '&Exit', self)
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.close)

        self.appMenu = self.menu_bar.addMenu('&Application')
        self.appMenu.addActions([self.aboutAction, self.settingsAction, self.exitAction])

        self.displayRawAction = QtGui.QAction(QtGui.QIcon('icons\\brain.png'), '&Converted formats', self)
        self.displayRawAction.setStatusTip('Displays files in a readable format instead of hex format.')
        self.displayRawAction.setCheckable(True)
        self.displayRawAction.setChecked(True)
        self.displayRawAction.triggered.connect(self.display_format_toggleCall)

        self.viewAdaptAction = QtGui.QAction(QtGui.QIcon('icons\\document-node.png'), '&Adapt', self)
        self.viewAdaptAction.setStatusTip('Files will be decrypted on a case per case basis.')
        self.viewAdaptAction.setCheckable(True)
        self.viewAdaptAction.setChecked(True)
        self.viewAdaptAction.triggered.connect(lambda: setattr(self, "fileDisplayMode", "Adapt"))
        self.viewAdaptAction.triggered.connect(lambda: self.treeCall())

        self.viewEndialogAction = QtGui.QAction(QtGui.QIcon('icons\\document-text.png'), '&English Dialogue', self)
        self.viewEndialogAction.setStatusTip('Files will be decrypted as in-game english dialogues.')
        self.viewEndialogAction.setCheckable(True)
        self.viewEndialogAction.triggered.connect(lambda: setattr(self, "fileDisplayMode", "English dialogue"))
        self.viewEndialogAction.triggered.connect(lambda: self.treeCall())

        self.viewGraphicAction = QtGui.QAction(QtGui.QIcon('icons\\appicon.ico'), '&Graphics', self)
        self.viewGraphicAction.setStatusTip('Files will be decrypted as graphics.')
        self.viewGraphicAction.setCheckable(True)
        self.viewGraphicAction.triggered.connect(lambda: setattr(self, "fileDisplayMode", "Graphics"))
        self.viewGraphicAction.triggered.connect(lambda: self.treeCall())

        self.viewFormatsGroup = QtGui.QActionGroup(self) #group for mutually exclusive togglable items
        self.viewFormatsGroup.addAction(self.viewAdaptAction)
        self.viewFormatsGroup.addAction(self.viewEndialogAction)
        self.viewFormatsGroup.addAction(self.viewGraphicAction)

        self.viewMenu = self.menu_bar.addMenu('&View')
        self.viewMenu.addAction(self.displayRawAction)
        self.displayFormatSubmenu = self.viewMenu.addMenu(QtGui.QIcon('icons\\document-convert.png'), '&Set edit mode...')
        self.displayFormatSubmenu.addAction(self.viewAdaptAction)
        self.displayFormatSubmenu.addSeparator()
        self.displayFormatSubmenu.addActions(self.viewFormatsGroup.actions()[1:])

        #Toolbar
        self.toolbar = QtWidgets.QToolBar("Main Toolbar")
        self.toolbar.setMaximumHeight(23)
        self.addToolBar(self.toolbar)

        self.action_save = QtGui.QAction(QtGui.QIcon('icons\\disk.png'), "Save to ROM", self)
        self.action_save.setStatusTip("Save changes to a ROM file")
        self.action_save.triggered.connect(self.saveCall)
        self.action_save.setDisabled(True)
        self.button_playtest = lib.widget.HoldButton(QtGui.QIcon('icons\\control.png'), "", self)
        self.button_playtest.setToolTip("Playtest ROM (Hold for options)")
        self.button_playtest.setStatusTip("Create a temporary ROM to test saved changes")
        self.button_playtest.allow_repeat = False
        self.button_playtest.allow_press = True
        self.button_playtest.pressed_quick.connect(lambda: self.testCall(True))
        self.button_playtest.held.connect(lambda: self.testCall(False))
        self.button_playtest.setDisabled(True)
        self.button_reload = lib.widget.HoldButton(QtGui.QIcon('icons\\arrow-circle-315.png'), "", self)
        self.button_reload.setToolTip("Reload Interface (Hold for deep refresh)")
        self.button_reload.setStatusTip("Reload the displayed data(all changes that aren't saved will be lost)")
        self.button_reload.allow_repeat = False
        self.button_reload.allow_press = True
        self.button_reload.pressed_quick.connect(lambda: self.reloadCall(1))
        self.button_reload.held.connect(lambda: self.reloadCall(2))
        self.action_sdat = QtGui.QAction(QtGui.QIcon('icons\\speaker-volume.png'), "Open Sound Data Archive", self)
        self.action_sdat.setStatusTip("Show the contents of this ROM's sdat file")
        self.action_sdat.triggered.connect(self.sdatOpenCall)
        self.action_sdat.setDisabled(True)
        self.action_arm9 = QtGui.QAction(QtGui.QIcon('icons\\processor-num-9.png'), "Open ARM9", self)
        self.action_arm9.setStatusTip("Show the contents of this ROM's ARM9")
        self.action_arm9.triggered.connect(self.arm9OpenCall)
        self.action_arm9.setDisabled(True)
        self.action_arm7 = QtGui.QAction(QtGui.QIcon('icons\\processor-num-7.png'), "Open ARM7", self)
        self.action_arm7.setStatusTip("Show the contents of this ROM's ARM7")
        self.action_arm7.triggered.connect(self.arm7OpenCall)
        self.action_arm7.setDisabled(True)
        #self.button_codeedit = QtGui.QAction(QtGui.QIcon('icons\\document-text.png'), "Open code", self)
        #self.button_codeedit.setStatusTip("Edit the ROM's code")
        #self.button_codeedit.triggered.connect(self.codeeditCall)
        #self.button_codeedit.setDisabled(True)
        self.toolbar.addActions([self.action_save, self.action_arm9, self.action_arm7, self.action_sdat])
        self.toolbar.insertWidget(self.action_arm9, self.button_playtest)
        self.toolbar.addWidget(self.button_reload)
        self.toolbar.addSeparator()

        #Tabs
        self.tabs = QtWidgets.QTabWidget(self)
        self.setCentralWidget(self.tabs)

        self.page_explorer = QtWidgets.QWidget(self.tabs)
        self.page_explorer.setLayout(QtWidgets.QHBoxLayout())

        self.page_leveleditor = QtWidgets.QWidget(self.tabs)
        self.page_leveleditor.setLayout(QtWidgets.QHBoxLayout())

        self.page_tweaks = QtWidgets.QWidget(self.tabs)
        self.page_tweaks.setLayout(QtWidgets.QVBoxLayout())

        self.page_patches = QtWidgets.QWidget(self.tabs)
        self.page_patches.setLayout(QtWidgets.QGridLayout())

        self.tabs.addTab(self.page_explorer, "File Explorer")
        self.tabs.addTab(self.page_leveleditor, "Level Editor") # Coming Soon™
        self.tabs.addTab(self.page_tweaks, "Tweaks") # Coming Soon™
        self.tabs.addTab(self.page_patches, "Patches") # Coming Soon™
        self.tabs.currentChanged.connect(self.tabChangeCall)

        #  ROM-related
        # ARM

        self.dialog_arm9 = QtWidgets.QMainWindow(self) # "independent" window: can move anywhere on screen, but still affected by main window
        self.dialog_arm9.setWindowTitle("ARM9")
        self.dialog_arm9.setWindowIcon(QtGui.QIcon('icons\\processor-num-9.png'))
        self.dialog_arm9.resize(600, 400)

        self.tabs_arm9 = QtWidgets.QTabWidget(self.dialog_arm9)
        self.dialog_arm9.setCentralWidget(self.tabs_arm9)

        self.page_arm9 = QtWidgets.QWidget(self.tabs_arm9)
        self.page_arm9.setLayout(QtWidgets.QHBoxLayout())
        self.page_arm9Ovltable = QtWidgets.QWidget(self.tabs_arm9)
        self.page_arm9Ovltable.setLayout(QtWidgets.QHBoxLayout())

        self.tabs_arm9.addTab(self.page_arm9, "Main Code")
        self.tabs_arm9.addTab(self.page_arm9Ovltable, "Overlays")

        self.tree_arm9 = lib.widget.EditorTree(self.page_arm9)
        self.page_arm9.layout().addWidget(self.tree_arm9)
        self.tree_arm9.ContextNameType = "code-section at "
        self.tree_arm9.setColumnCount(3)
        self.tree_arm9.setHeaderLabels(["RAM Address", "Name", "Implicit"])
        self.tree_arm9.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        self.tree_arm9Ovltable = lib.widget.EditorTree(self.page_arm9Ovltable)
        self.page_arm9Ovltable.layout().addWidget(self.tree_arm9Ovltable)
        self.tree_arm9Ovltable.ContextNameType = "overlay "
        self.tree_arm9Ovltable.setColumnCount(10)
        self.tree_arm9Ovltable.setHeaderLabels(["File ID", "RAM Address", "Compressed", "Size", "RAM Size", "BSS Size", "StaticInit Start", "StaticInit End", "Flags", "Verify Hash"])
        self.tree_arm9Ovltable.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)



        self.dialog_arm7 = QtWidgets.QMainWindow(self)
        self.dialog_arm7.setWindowTitle("ARM7")
        self.dialog_arm7.setWindowIcon(QtGui.QIcon('icons\\processor-num-7.png'))
        self.dialog_arm7.resize(600, 400)

        self.tabs_arm7 = QtWidgets.QTabWidget(self.dialog_arm7)
        self.dialog_arm7.setCentralWidget(self.tabs_arm7)

        self.page_arm7 = QtWidgets.QWidget(self.tabs_arm7)
        self.page_arm7.setLayout(QtWidgets.QHBoxLayout())
        self.page_arm7Ovltable = QtWidgets.QWidget(self.tabs_arm7)
        self.page_arm7Ovltable.setLayout(QtWidgets.QHBoxLayout())

        self.tabs_arm7.addTab(self.page_arm7, "Main Code")
        self.tabs_arm7.addTab(self.page_arm7Ovltable, "Overlays")

        self.tree_arm7 = lib.widget.EditorTree(self.page_arm7)
        self.page_arm7.layout().addWidget(self.tree_arm7)
        self.tree_arm7.ContextNameType = "code-section at "
        self.tree_arm7.setColumnCount(3)
        self.tree_arm7.setHeaderLabels(["RAM Address", "Name", "Implicit"])
        self.tree_arm7.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        self.tree_arm7Ovltable = lib.widget.EditorTree(self.page_arm7Ovltable)
        self.page_arm7Ovltable.layout().addWidget(self.tree_arm7Ovltable)
        self.tree_arm7Ovltable.ContextNameType = "overlay "
        self.tree_arm7Ovltable.setColumnCount(10)
        self.tree_arm7Ovltable.setHeaderLabels(["File ID", "RAM Address", "Compressed", "Size", "RAM Size", "BSS Size", "StaticInit Start", "StaticInit End", "Flags", "Verify Hash"])
        self.tree_arm7Ovltable.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        # File explorer
        self.tree = lib.widget.EditorTree(self.page_explorer)
        self.tree.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.page_explorer.layout().addWidget(self.tree, 0)
        self.tree.setMaximumWidth(450)
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["File ID", "Name", "Type"])
        self.tree.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_called = False
        self.tree.itemSelectionChanged.connect(lambda: self.treeCall(addr_reset=True))

        self.layout_editzone = QtWidgets.QVBoxLayout()
        self.page_explorer.layout().addItem(self.layout_editzone)
        self.layout_editzone_row0 = QtWidgets.QHBoxLayout()
        self.layout_editzone_row1 = QtWidgets.QHBoxLayout()
        self.layout_editzone_row2 = QtWidgets.QHBoxLayout()
        self.layout_editzone_row3 = QtWidgets.QHBoxLayout()
        self.widget_colorpick = QtWidgets.QWidget(self.page_explorer)
        self.layout_colorpick = lib.widget.GridLayout()
        self.layout_colorpick.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.layout_colorpick.setContentsMargins(0,2,5,0)
        self.layout_colorpick.setSpacing(0)
        self.widget_colorpick.setLayout(self.layout_colorpick)

        self.button_file_save = QtWidgets.QPushButton("Save file", self.page_explorer)
        self.button_file_save.setMaximumWidth(100)
        self.button_file_save.setToolTip("save this file's changes")
        self.button_file_save.pressed.connect(self.save_filecontent)
        self.button_file_save.setDisabled(True)
        self.button_file_save.hide()

        self.file_content = QtWidgets.QGridLayout()
        self.file_content_text = lib.widget.LongTextEdit(self.page_explorer)
        self.file_content_text.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        font = QtGui.QFont("Monospace")
        font.setStyleHint(QtGui.QFont.StyleHint.TypeWriter)
        self.file_content_text.setFont(font)
        self.file_content_text.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.NoContextMenu)
        self.file_content_text.textChanged.connect(lambda: self.button_file_save.setDisabled(False))
        self.file_content_text.setDisabled(True)

        self.dropdown_textindex = QtWidgets.QComboBox(self.page_explorer)
        self.dropdown_textindex.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.dropdown_textindex.previousIndex = self.dropdown_textindex.currentIndex()
        self.dropdown_textindex.currentIndexChanged.connect(lambda: self.treeCall())

        self.checkbox_textoverwite = QtWidgets.QCheckBox("Overwite\n existing text", self.page_explorer)
        self.checkbox_textoverwite.setStatusTip("With this enabled, writing text won't change filesize")
        self.checkbox_textoverwite.clicked.connect(lambda: self.file_content_text.setOverwriteMode(not self.file_content_text.overwriteMode()))

        self.layout_editzone_row1.addWidget(self.checkbox_textoverwite)
        self.layout_editzone_row1.addWidget(self.dropdown_textindex)

        self.file_content_gfx = lib.widget.GFXView(self.page_explorer)
        self.file_content_gfx.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Expanding)
        self.file_content.addWidget(self.file_content_gfx)
        self.file_content.addWidget(self.file_content_text)

        self.dropdown_gfx_depth = QtWidgets.QComboBox(self.page_explorer)
        self.dropdown_gfx_depth.addItems(["1bpp", "4bpp", "8bpp"])# order of names is determined by the enum in dataconverter
        self.dropdown_gfx_depth.currentIndexChanged.connect(lambda: self.treeCall())# Update gfx with current depth

        self.font_caps = QtGui.QFont()
        self.font_caps.setCapitalization(QtGui.QFont.Capitalization.AllUppercase)
        
        #Address bar
        self.field_address = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_address.numfill = 8
        self.field_address.setFont(self.font_caps)
        self.field_address.setValue(self.base_address+self.relative_address)
        self.field_address.isInt = True
        #self.field_address.setPrefix("0x")
        self.field_address.numbase = self.displayBase
        #self.field_address.textChanged.connect(lambda: self.value_update_Call("relative_address", library.dataconverter.baseToInt(library.dataconverter.strToBase(self.field_address.text()), self.field_address.displayIntegerBase()) - self.base_address, True))
        self.field_address.textChanged.connect(lambda: self.value_update_Call("relative_address", int(self.field_address.valueFromText(self.field_address.text()) - self.base_address), True))
        self.field_address.setDisabled(True)
        self.field_address.hide()
        #notes
        self.label_file_size = QtWidgets.QLabel(self.page_explorer)
        self.label_file_size.setContentsMargins(5,0,0,0)
        self.label_file_size.setText("Size: N/A")
        self.label_file_size.hide()
        #Tile Wifth
        self.tile_width = 8
        self.field_tile_width = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_tile_width.setStatusTip(f"Set tile width to {lib.datconv.numToStr(16, self.displayBase, self.displayAlphanumeric)} or {lib.datconv.numToStr(32, self.displayBase, self.displayAlphanumeric)} for some ZXA sprites")
        self.field_tile_width.setFont(self.font_caps)
        self.field_tile_width.setValue(self.tile_width)
        self.field_tile_width.setMinimum(1)
        self.field_tile_width.numbase = self.displayBase
        self.field_tile_width.isInt = True
        self.field_tile_width.valueChanged.connect(lambda: self.value_update_Call("tile_width", int(self.field_tile_width.value()), True))
        self.field_tile_width.valueChanged.connect(self.file_content_gfx.fitInView)

        self.label_tile_width = QtWidgets.QLabel(self.page_explorer)
        self.label_tile_width.setText(" width")

        self.layout_tile_width = QtWidgets.QVBoxLayout()
        self.layout_tile_width.addWidget(self.field_tile_width)
        self.layout_tile_width.addWidget(self.label_tile_width)
        self.layout_tile_width.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        #Tile Height
        self.tile_height = 8
        self.field_tile_height = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_tile_height.setFont(self.font_caps)
        self.field_tile_height.setValue(self.tile_height)
        self.field_tile_height.setMinimum(1)
        self.field_tile_height.numbase = self.displayBase
        self.field_tile_height.isInt = True
        self.field_tile_height.valueChanged.connect(lambda: self.value_update_Call("tile_height", int(self.field_tile_height.value()), True)) 
        self.field_tile_height.valueChanged.connect(self.file_content_gfx.fitInView)

        self.label_tile_height = QtWidgets.QLabel(self.page_explorer)
        self.label_tile_height.setText(" height")

        self.layout_tile_height = QtWidgets.QVBoxLayout()
        self.layout_tile_height.addWidget(self.field_tile_height)
        self.layout_tile_height.addWidget(self.label_tile_height)
        self.layout_tile_height.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        #Tiles Per row
        self.tiles_per_row = 8
        self.field_tiles_per_row = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_tiles_per_row.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.field_tiles_per_row.setFont(self.font_caps)
        self.field_tiles_per_row.setValue(self.tiles_per_row)
        self.field_tiles_per_row.setMinimum(1)
        self.field_tiles_per_row.isInt = True
        self.field_tiles_per_row.numbase = self.displayBase
        self.field_tiles_per_row.valueChanged.connect(lambda: self.value_update_Call("tiles_per_row", int(self.field_tiles_per_row.value()), True))
        self.field_tiles_per_row.valueChanged.connect(self.file_content_gfx.fitInView)

        self.label_tiles_per_row = QtWidgets.QLabel(self.page_explorer)
        self.label_tiles_per_row.setText(" columns")

        self.layout_tiles_per_row = QtWidgets.QVBoxLayout()
        self.layout_tiles_per_row.addWidget(self.field_tiles_per_row)
        self.layout_tiles_per_row.addWidget(self.label_tiles_per_row)
        self.layout_tiles_per_row.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        #Tiles Per Column
        self.tiles_per_column = 8
        self.field_tiles_per_column = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_tiles_per_column.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.field_tiles_per_column.setFont(self.font_caps)
        self.field_tiles_per_column.setValue(self.tiles_per_column)
        self.field_tiles_per_column.setMinimum(1)
        self.field_tiles_per_column.isInt = True
        self.field_tiles_per_column.numbase = self.displayBase
        self.field_tiles_per_column.valueChanged.connect(lambda: self.value_update_Call("tiles_per_column", int(self.field_tiles_per_column.value()), True))
        self.field_tiles_per_column.valueChanged.connect(self.file_content_gfx.fitInView)

        self.label_tiles_per_column = QtWidgets.QLabel(self.page_explorer)
        self.label_tiles_per_column.setText(" rows")

        self.layout_tiles_per_column = QtWidgets.QVBoxLayout()
        self.layout_tiles_per_column.addWidget(self.field_tiles_per_column)
        self.layout_tiles_per_column.addWidget(self.label_tiles_per_column)
        self.layout_tiles_per_column.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.layout_tile_settings = QtWidgets.QHBoxLayout()
        self.layout_tile_settings.addItem(self.layout_tile_width)
        self.layout_tile_settings.addItem(self.layout_tile_height)
        self.layout_tile_settings.addItem(self.layout_tiles_per_row)
        self.layout_tile_settings.addItem(self.layout_tiles_per_column)

        self.dropdown_gfx_index = QtWidgets.QComboBox(self.page_explorer)
        self.dropdown_gfx_index.setPlaceholderText("no section entries")
        self.dropdown_gfx_index.setToolTip("Choose index")
        self.dropdown_gfx_index.setStatusTip("Select the object index to go to in gfx file")
        self.dropdown_gfx_index.currentIndexChanged.connect(lambda: self.treeCall())
        self.dropdown_gfx_subindex = QtWidgets.QComboBox(self.page_explorer)
        self.dropdown_gfx_subindex.setPlaceholderText("no sub-entries")
        self.dropdown_gfx_subindex.setToolTip("Choose sub-index")
        self.dropdown_gfx_subindex.setStatusTip("Select the image index to go to in gfx object")
        self.dropdown_gfx_subindex.currentIndexChanged.connect(lambda: self.treeCall())

        self.checkbox_depthUpdate = QtWidgets.QCheckBox(self.page_explorer)
        self.checkbox_depthUpdate.setStatusTip("Update depth to match palette size")
        self.checkbox_depthUpdate.setChecked(True)
        self.checkbox_depthUpdate.checkStateChanged.connect(lambda: self.treeCall())

        self.label_depthUpdate = QtWidgets.QLabel(self.page_explorer)
        self.label_depthUpdate.setText("Guess correct depth")

        self.layout_other_settings = QtWidgets.QGridLayout()
        self.layout_other_settings.addWidget(self.checkbox_depthUpdate, 0,0, QtCore.Qt.AlignmentFlag.AlignRight)
        self.layout_other_settings.addWidget(self.label_depthUpdate, 0,1)
        self.layout_other_settings.addWidget(self.dropdown_gfx_index, 1,0)
        self.layout_other_settings.addWidget(self.dropdown_gfx_subindex, 1,1)

        #Palettes
        for i in range(256): #setup default palette
            setattr(self, f"button_palettepick_{i}", lib.widget.HoldButton(self.page_explorer))
            button_palettepick: lib.widget.HoldButton = getattr(self, f"button_palettepick_{i}")
            button_palettepick.allow_press = True
            button_palettepick.press_quick_threshold = 1
            button_palettepick.setStyleSheet(f"background-color: #{self.gfx_palette[i]:08x}; color: white;")
            button_palettepick.setMaximumSize(10, 10)
            self.layout_colorpick.addWidget(button_palettepick, int(i/16), int(i%16))
            button_palettepick.held.connect(lambda hold, press=None, color_index=i: self.colorpickCall(color_index, press, hold))
            button_palettepick.pressed_quick.connect(lambda press, hold=None, color_index=i: self.colorpickCall(color_index, press, hold))

        self.dropdown_gfx_palette = QtWidgets.QComboBox(self.page_explorer)
        self.dropdown_gfx_palette.addItems(["Default Palette", "Font Palette", "Sprites Palette", "BG Palette"]) # order of names is determined by the enum in dataconverter
        self.dropdown_gfx_palette.setToolTip("Choose palette")
        self.dropdown_gfx_palette.setStatusTip("Select the color palette preset that you want to use to render images")
        self.dropdown_gfx_palette.currentIndexChanged.connect(lambda: self.setPalette(self.GFX_PALETTES[self.dropdown_gfx_palette.currentIndex()])) # Update gfx with current depth
        self.dropdown_gfx_palette.currentIndexChanged.connect(lambda: self.treeCall())

        self.layout_palette_settings = QtWidgets.QHBoxLayout()
        self.layout_palette_settings.addWidget(self.dropdown_gfx_palette)

        self.layout_gfx_settings = QtWidgets.QVBoxLayout()
        self.layout_gfx_settings.addItem(self.layout_tile_settings)
        self.layout_gfx_settings.addItem(self.layout_other_settings)
        self.layout_gfx_settings.addItem(self.layout_palette_settings)

        #OAM
        self.dropdown_oam_entry = QtWidgets.QComboBox(self.page_explorer)
        self.dropdown_oam_entry.setPlaceholderText("no oam entries")
        self.dropdown_oam_entry.setToolTip("Choose entry")
        self.dropdown_oam_entry.setStatusTip("Select the OAM entry to load")
        self.dropdown_oam_entry.currentIndexChanged.connect(lambda: self.treeCall(addr_disabled=True))

        self.tabs_oam = QtWidgets.QTabWidget(self.page_explorer)
        self.page_oam_frames = QtWidgets.QWidget(self.tabs_oam)
        self.page_oam_frames.setLayout(QtWidgets.QGridLayout())
        self.page_oam_anims = QtWidgets.QWidget(self.tabs_oam)
        self.page_oam_anims.setLayout(QtWidgets.QGridLayout())
        self.tabs_oam.addTab(self.page_oam_frames, "Frames")
        self.tabs_oam.addTab(self.page_oam_anims, "Animations")
        self.tabs_oam.currentChanged.connect(lambda: self.treeCall(addr_disabled=True))

        self.dropdown_oam_anim = QtWidgets.QComboBox(self.page_oam_anims)
        self.dropdown_oam_anim.setPlaceholderText("no animation entries")
        self.dropdown_oam_anim.setToolTip("Choose animation")
        self.dropdown_oam_anim.setStatusTip("Select the animation to load")
        self.dropdown_oam_anim.currentIndexChanged.connect(lambda: self.treeCall(addr_disabled=True))

        self.dropdown_oam_animFrame = QtWidgets.QComboBox(self.page_explorer)
        self.dropdown_oam_animFrame.setPlaceholderText("no animation frames")
        self.dropdown_oam_animFrame.setToolTip("Choose frame")
        self.dropdown_oam_animFrame.setStatusTip("Select the animation frame to load")
        self.dropdown_oam_animFrame.currentIndexChanged.connect(lambda: self.treeCall(addr_disabled=True))

        self.field_oam_animFrameId = lib.widget.BetterSpinBox(self.page_oam_anims)
        self.field_oam_animFrameId.setToolTip("Frame Id")
        self.field_oam_animFrameId.setStatusTip("Frame index as seen in the frame editing tab")
        self.field_oam_animFrameId.isInt = True
        self.field_oam_animFrameId.setRange(0, 0xFF)
        self.field_oam_animFrameId.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.field_oam_animFrameId.valueChanged.connect(lambda: self.treeCall(addr_disabled=True))

        self.field_oam_animFrameDuration = lib.widget.BetterSpinBox(self.page_oam_anims)
        self.field_oam_animFrameDuration.setToolTip("Duration (Frames)")
        self.field_oam_animFrameDuration.setStatusTip("Duration of current frame; After the first frame, 0xFE and 0xFF are treated as loop and end")
        self.field_oam_animFrameDuration.isInt = True
        self.field_oam_animFrameDuration.setRange(0, 0xFF)
        self.field_oam_animFrameDuration.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.field_oam_animFrameDuration.valueChanged.connect(lambda: self.treeCall(addr_disabled=True))

        self.button_oam_animFrameAdd = QtWidgets.QPushButton("Add Frame", self.page_oam_anims)
        self.button_oam_animFrameAdd.pressed.connect(lambda: self.treeCall(addr_disabled=True))

        self.button_oam_animFrameRemove = QtWidgets.QPushButton("Remove Frame", self.page_oam_anims)
        self.button_oam_animFrameRemove.pressed.connect(lambda: self.treeCall(addr_disabled=True))

        self.checkbox_oam_animLoop = QtWidgets.QCheckBox(self.page_oam_anims)
        self.checkbox_oam_animLoop.setText("Loop")
        self.checkbox_oam_animLoop.setToolTip("Loop")
        self.checkbox_oam_animLoop.setStatusTip("Enable/Disable animation loop point")
        self.checkbox_oam_animLoop.checkStateChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.checkbox_oam_animLoop.checkStateChanged.connect(lambda: self.field_oam_animLoopStart.setEnabled(self.checkbox_oam_animLoop.isChecked()))

        self.field_oam_animLoopStart = lib.widget.BetterSpinBox(self.page_oam_anims)
        self.field_oam_animLoopStart.setToolTip("Loop Start")
        self.field_oam_animLoopStart.setStatusTip("Frame index to jump to at the end of animation")
        self.field_oam_animLoopStart.isInt = True
        self.field_oam_animLoopStart.setRange(0, 0xFF)
        self.field_oam_animLoopStart.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))

        self.button_oam_animToStart = QtWidgets.QPushButton(self.page_oam_anims)
        self.button_oam_animToStart.setIcon(QtGui.QIcon("icons\\control-skip-180.png"))
        self.button_oam_animToStart.setToolTip("To Start")
        self.button_oam_animToStart.pressed.connect(lambda: self.button_oam_animPlay.autoPause())
        self.button_oam_animToStart.pressed.connect(lambda: self.dropdown_oam_animFrame.setCurrentIndex(0))

        self.button_oam_animPlay = lib.widget.PlayButton(self.page_oam_anims)
        self.button_oam_animPlay.setToolTip("Play/Pause")
        self.button_oam_animPlay.frameRequested.connect(self.OAM_playAnimFrame)

        self.button_oam_animToEnd = QtWidgets.QPushButton(self.page_oam_anims)
        self.button_oam_animToEnd.setIcon(QtGui.QIcon("icons\\control-skip.png"))
        self.button_oam_animToEnd.setToolTip("To End")
        self.button_oam_animToEnd.pressed.connect(lambda: self.button_oam_animPlay.autoPause())
        self.button_oam_animToEnd.pressed.connect(lambda: self.dropdown_oam_animFrame.setCurrentIndex(self.dropdown_oam_animFrame.count()-1))

        self.dropdown_oam_objFrame = QtWidgets.QComboBox(self.page_explorer)
        self.dropdown_oam_objFrame.setPlaceholderText("no OAM frames")
        self.dropdown_oam_objFrame.setToolTip("Choose frame")
        self.dropdown_oam_objFrame.setStatusTip("Select the OAM frame to load")
        self.dropdown_oam_objFrame.currentIndexChanged.connect(lambda: self.treeCall(addr_disabled=True))

        self.dropdown_oam_obj = QtWidgets.QComboBox(self.page_oam_frames) #temporary until gfx interface implemented
        self.dropdown_oam_obj.previousIndex = 0
        self.dropdown_oam_obj.setPlaceholderText("no objects")
        self.dropdown_oam_obj.setToolTip("Choose object")
        self.dropdown_oam_obj.setStatusTip("Select the object to edit")
        self.dropdown_oam_obj.currentIndexChanged.connect(lambda: self.treeCall(addr_disabled=True))

        self.button_oam_objSelect = QtWidgets.QPushButton(self.page_oam_frames)
        self.button_oam_objSelect.setText("Select current object")
        self.button_oam_objSelect.pressed.connect(lambda: self.treeCall(addr_disabled=True))

        self.button_oam_objAdd = QtWidgets.QPushButton(self.page_oam_frames)
        self.button_oam_objAdd.setText("Add object")
        self.button_oam_objAdd.pressed.connect(lambda: self.treeCall(addr_disabled=True))

        self.button_oam_objRemove = QtWidgets.QPushButton(self.page_oam_frames)
        self.button_oam_objRemove.setText("Remove object")
        self.button_oam_objRemove.pressed.connect(lambda: self.treeCall(addr_disabled=True))

        self.field_objTileId = lib.widget.BetterSpinBox(self.page_oam_frames)
        self.field_objTileId.setToolTip("Tile Id (OAM)")
        self.field_objTileId.setStatusTip("OAM tile id is half the value of VRAM tile id")
        self.field_objTileId.isInt = True
        self.field_objTileId.setRange(0, 0x3FF)
        self.field_objTileId.numbase = self.displayBase
        self.field_objTileId.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.field_objTileId.valueChanged.connect(lambda: self.OAM_updateItemGFX(self.dropdown_oam_obj.currentIndex(), self.file_content_oam.item_current))

        self.checkbox_objFlipH = QtWidgets.QCheckBox(self.page_oam_frames)
        self.checkbox_objFlipH.setText("Flip H")
        self.checkbox_objFlipH.checkStateChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.checkbox_objFlipH.checkStateChanged.connect(lambda: self.file_content_oam.item_current.setPixmap(
            self.file_content_oam.item_current.pixmap().transformed(QtGui.QTransform().scale(-1,1))))

        self.checkbox_objFlipV = QtWidgets.QCheckBox(self.page_oam_frames)
        self.checkbox_objFlipV.setText("Flip V")
        self.checkbox_objFlipV.checkStateChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.checkbox_objFlipV.checkStateChanged.connect(lambda: self.file_content_oam.item_current.setPixmap(
            self.file_content_oam.item_current.pixmap().transformed(QtGui.QTransform().scale(1,-1))))

        self.slider_objSizeIndex = lib.widget.LabeledSlider(self.page_oam_frames, 0, 3, interval=1, orientation=QtCore.Qt.Orientation.Horizontal, labels=["1x1", "2x2", "4x4", "8x8"])
        self.slider_objSizeIndex.setMaximumSize(260, 60)
        self.slider_objSizeIndex.setToolTip("size increment")
        self.slider_objSizeIndex.sl.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.slider_objSizeIndex.sl.valueChanged.connect(lambda: self.OAM_updateItemGFX(self.dropdown_oam_obj.currentIndex(), self.file_content_oam.item_current))

        self.radio_objShapeSquare = QtWidgets.QRadioButton()
        self.radio_objShapeSquare.setText("Square")
        self.radio_objShapeSquare.toggled.connect(lambda: self.button_file_save.setEnabled(True))
        self.radio_objShapeWide = QtWidgets.QRadioButton()
        self.radio_objShapeWide.setText("Wide")
        self.radio_objShapeWide.toggled.connect(lambda: self.button_file_save.setEnabled(True))
        self.radio_objShapeTall = QtWidgets.QRadioButton()
        self.radio_objShapeTall.setText("Tall")
        self.radio_objShapeTall.toggled.connect(lambda: self.button_file_save.setEnabled(True))

        self.buttonGroup_oam_objShape = QtWidgets.QButtonGroup(self.page_oam_frames)
        self.buttonGroup_oam_objShape.addButton(self.radio_objShapeSquare, 0)
        self.buttonGroup_oam_objShape.addButton(self.radio_objShapeWide, 1)
        self.buttonGroup_oam_objShape.addButton(self.radio_objShapeTall, 2)
        self.buttonGroup_oam_objShape.idReleased.connect(lambda: self.slider_objSizeIndex.setLabels(lib.oam.SPRITE_DIMENSIONS[self.buttonGroup_oam_objShape.checkedId()]))
        self.buttonGroup_oam_objShape.idReleased.connect(lambda: self.OAM_updateItemGFX(self.dropdown_oam_obj.currentIndex(), self.file_content_oam.item_current))

        self.group_oam_objShape = QtWidgets.QGroupBox(self.page_oam_frames)
        self.group_oam_objShape.setTitle("Shape")
        self.group_oam_objShape.setLayout(QtWidgets.QVBoxLayout())
        self.group_oam_objShape.layout().addWidget(self.radio_objShapeSquare)
        self.group_oam_objShape.layout().addWidget(self.radio_objShapeWide)
        self.group_oam_objShape.layout().addWidget(self.radio_objShapeTall)

        self.field_objX = lib.widget.BetterSpinBox(self.page_oam_frames)
        self.field_objX.setToolTip("X")
        self.field_objX.isInt = True
        self.field_objX.setRange(-128, 127)
        self.field_objX.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.field_objX.valueChanged.connect(lambda: self.file_content_oam.item_current.setX(self.field_objX.value()))
        self.field_objY = lib.widget.BetterSpinBox(self.page_oam_frames)
        self.field_objY.setToolTip("Y")
        self.field_objY.isInt = True
        self.field_objY.setRange(-128, 127)
        self.field_objY.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.field_objY.valueChanged.connect(lambda: self.file_content_oam.item_current.setY(self.field_objY.value()))

        self.file_content_oam = lib.widget.OAMView(self.page_explorer)
        self.file_content_oam.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Expanding)
        self.file_content.addWidget(self.file_content_oam)

        self.layout_oam_navigation = QtWidgets.QGridLayout()
        self.layout_oam_navigation.addWidget(self.dropdown_oam_entry, 0, 0)
        self.page_oam_anims.layout().addWidget(self.dropdown_oam_anim, 0, 0, 1, 3)
        self.page_oam_anims.layout().addWidget(self.dropdown_oam_animFrame, 0, 3)
        self.page_oam_anims.layout().addWidget(self.field_oam_animFrameId, 1, 3)
        self.page_oam_anims.layout().addWidget(self.button_oam_animFrameAdd, 1, 4, 1, 2)
        self.page_oam_anims.layout().addWidget(self.field_oam_animFrameDuration, 2, 3)
        self.page_oam_anims.layout().addWidget(self.button_oam_animFrameRemove, 2, 4, 1, 2)
        self.page_oam_anims.layout().addWidget(self.checkbox_oam_animLoop, 1, 0)
        self.page_oam_anims.layout().addWidget(self.field_oam_animLoopStart, 2, 0)
        self.page_oam_anims.layout().addWidget(self.button_oam_animToStart, 3, 0, 1, 2)
        self.page_oam_anims.layout().addWidget(self.button_oam_animPlay, 3, 2, 1, 2)
        self.page_oam_anims.layout().addWidget(self.button_oam_animToEnd, 3, 4, 1, 2)
        self.page_oam_frames.layout().addWidget(self.dropdown_oam_objFrame, 0, 0, 1, 2)
        self.page_oam_frames.layout().addWidget(self.dropdown_oam_obj, 0, 2)
        self.page_oam_frames.layout().addWidget(self.button_oam_objAdd, 0, 3)
        self.page_oam_frames.layout().addWidget(self.field_objTileId, 1, 0, 1, 2)
        self.page_oam_frames.layout().addWidget(self.button_oam_objSelect, 1, 2)
        self.page_oam_frames.layout().addWidget(self.button_oam_objRemove, 1, 3)
        self.page_oam_frames.layout().addWidget(self.checkbox_objFlipH, 2, 0, 1, 2)
        self.page_oam_frames.layout().addWidget(self.checkbox_objFlipV, 3, 0, 1, 2)
        self.page_oam_frames.layout().addWidget(self.slider_objSizeIndex, 4, 0, 1, 2)
        self.page_oam_frames.layout().addWidget(self.group_oam_objShape, 4, 2, 1, 2)
        self.page_oam_frames.layout().addWidget(self.field_objX, 5, 0, 1, 2)
        self.page_oam_frames.layout().addWidget(self.field_objY, 5, 2, 1, 2)

        #Palette Animation
        self.dropdown_panm_entry = QtWidgets.QComboBox(self.page_explorer)
        self.dropdown_panm_entry.setPlaceholderText("no animations")
        self.dropdown_panm_entry.setToolTip("Choose palette animation")
        self.dropdown_panm_entry.setStatusTip("Palette animations for mavericks. 0=evil; 1=patrol; 2=alert")
        self.dropdown_panm_entry.currentIndexChanged.connect(lambda: self.treeCall(addr_disabled=True))

        self.dropdown_panm_frame = QtWidgets.QComboBox(self.page_explorer)
        self.dropdown_panm_frame.setPlaceholderText("no frames")
        self.dropdown_panm_frame.setToolTip("Choose animation frame")
        self.dropdown_panm_frame.setStatusTip("Each frame overwrites two colors from a 16-color palette")
        self.dropdown_panm_frame.currentIndexChanged.connect(lambda: self.treeCall(addr_disabled=True))

        self.layout_panm = QtWidgets.QGridLayout()

        self.field_panm_frameId = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_panm_frameId.setToolTip("Frame")
        self.field_panm_frameId.isInt = True
        self.field_panm_frameId.setRange(0x00, 0xFF)
        self.field_panm_frameId.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.field_panm_frameDuration = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_panm_frameDuration.setToolTip("Duration")
        self.field_panm_frameDuration.isInt = True
        self.field_panm_frameDuration.setRange(0x00, 0xFF)
        self.field_panm_frameDuration.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.checkbox_panm_loop = QtWidgets.QCheckBox(self.page_explorer)
        self.checkbox_panm_loop.setText("Loop")
        self.checkbox_panm_loop.setToolTip("Loop On/Off")
        self.checkbox_panm_loop.checkStateChanged.connect(lambda: self.field_panm_loopStart.setEnabled(self.checkbox_panm_loop.isChecked()))
        self.checkbox_panm_loop.checkStateChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.field_panm_loopStart = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_panm_loopStart.setToolTip("Loop Start")
        self.field_panm_loopStart.isInt = True
        self.field_panm_loopStart.setRange(0x00, 0xFF)
        self.field_panm_loopStart.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))

        self.label_panm_colorSlots = QtWidgets.QLabel("Color slots", self.page_explorer)
        self.label_panm_colorSlots.setMaximumHeight(50)
        self.label_panm_colorSlots.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom)
        self.field_panm_colorSlot0 = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_panm_colorSlot0.setToolTip("Color Slot 0")
        self.field_panm_colorSlot0.setStatusTip("The index of the first color to overwrite in a 16-color palette")
        self.field_panm_colorSlot0.isInt = True
        self.field_panm_colorSlot0.setRange(0x00, 0xFF)
        self.field_panm_colorSlot0.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.field_panm_colorSlot1 = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_panm_colorSlot1.setStatusTip("The index of the second color to overwrite in a 16-color palette")
        self.field_panm_colorSlot1.setToolTip("Color Slot 1")
        self.field_panm_colorSlot1.isInt = True
        self.field_panm_colorSlot1.setRange(0x00, 0xFF)
        self.field_panm_colorSlot1.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))

        self.layout_panm.addWidget(self.dropdown_panm_entry, 0, 0)
        self.layout_panm.addWidget(self.dropdown_panm_frame, 0, 1)
        self.layout_panm.addWidget(self.field_panm_frameId, 1, 1)
        self.layout_panm.addWidget(self.field_panm_frameDuration, 2, 1)
        self.layout_panm.addWidget(self.checkbox_panm_loop, 1, 0)
        self.layout_panm.addWidget(self.field_panm_loopStart, 2, 0)
        self.layout_panm.addWidget(self.label_panm_colorSlots, 3, 0)
        self.layout_panm.addWidget(self.field_panm_colorSlot0, 4, 0)
        self.layout_panm.addWidget(self.field_panm_colorSlot1, 5, 0)
        self.layout_panm.setSpacing(3)

        #Font
        self.field_font_size = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_font_size.setFont(self.font_caps)
        self.field_font_size.setMinimum(0)
        self.field_font_size.isInt = True
        self.field_font_size.numbase = self.displayBase
        self.field_font_size.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.label_font_size = QtWidgets.QLabel(self.page_explorer)
        self.label_font_size.setText("file size")
        self.layout_font_size = QtWidgets.QVBoxLayout()
        self.layout_font_size.addWidget(self.field_font_size)
        self.layout_font_size.addWidget(self.label_font_size)
        self.layout_font_size.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.field_font_width = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_font_width.setFont(self.font_caps)
        self.field_font_width.setMinimum(0)
        self.field_font_width.isInt = True
        self.field_font_width.numbase = self.displayBase
        self.field_font_width.setStatusTip("Make sure that this is an even number to prevent the game from crashing")
        self.field_font_width.valueChanged.connect(lambda: self.treeCall())
        self.field_font_width.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.field_font_width.valueChanged.connect(self.file_content_gfx.fitInView)
        self.label_font_width = QtWidgets.QLabel(self.page_explorer)
        self.label_font_width.setText("char width")
        self.layout_font_width = QtWidgets.QVBoxLayout()
        self.layout_font_width.addWidget(self.field_font_width)
        self.layout_font_width.addWidget(self.label_font_width)
        self.layout_font_width.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.field_font_height = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_font_height.setFont(self.font_caps)
        self.field_font_height.setMinimum(0)
        self.field_font_height.isInt = True
        self.field_font_height.numbase = self.displayBase
        self.field_font_height.valueChanged.connect(lambda: self.treeCall())
        self.field_font_height.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.field_font_height.valueChanged.connect(self.file_content_gfx.fitInView)
        self.label_font_height = QtWidgets.QLabel(self.page_explorer)
        self.label_font_height.setText("char height")
        self.layout_font_height = QtWidgets.QVBoxLayout()
        self.layout_font_height.addWidget(self.field_font_height)
        self.layout_font_height.addWidget(self.label_font_height)
        self.layout_font_height.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.label_font_indexingSpace = QtWidgets.QLabel(self.page_explorer)
        self.label_font_indexingSpace.setText("indexing space: ")

        self.label_font_charCount = QtWidgets.QLabel(self.page_explorer)
        self.label_font_charCount.setText("char count: ")

        self.label_font_unusedStr = QtWidgets.QLabel(self.page_explorer)
        self.label_font_unusedStr.setText("unused string: ")

        self.layout_editzone_row0.addWidget(self.button_file_save)
        self.layout_editzone_row0.addWidget(self.label_file_size)
        self.layout_editzone_row0.addWidget(self.dropdown_gfx_depth)
        self.layout_editzone_row0.addWidget(self.field_address)
        
        self.layout_editzone_row1.addWidget(self.widget_colorpick)
        self.layout_editzone_row1.addItem(self.layout_gfx_settings)
        self.layout_editzone_row1.addItem(self.layout_oam_navigation)
        self.layout_editzone_row1.addItem(self.layout_panm)

        self.layout_editzone_row2.addItem(self.layout_font_size)
        self.layout_editzone_row2.addItem(self.layout_font_width)
        self.layout_editzone_row2.addItem(self.layout_font_height)
        self.layout_editzone_row2.addWidget(self.tabs_oam)

        self.layout_editzone_row3.addWidget(self.label_font_indexingSpace)
        self.layout_editzone_row3.addWidget(self.label_font_charCount)
        self.layout_editzone_row3.addWidget(self.label_font_unusedStr)

        self.layout_editzone.addItem(self.layout_editzone_row0)
        self.layout_editzone.addItem(self.layout_editzone_row1)
        self.layout_editzone.addItem(self.layout_editzone_row2)
        self.layout_editzone.addItem(self.layout_editzone_row3)
        self.layout_editzone.addItem(self.file_content)


        #Sound Data Archive
        self.dialog_sdat = QtWidgets.QMainWindow(self)
        self.dialog_sdat.setWindowTitle("Sound Data Archive")
        self.dialog_sdat.setWindowIcon(QtGui.QIcon('icons\\speaker-volume.png'))
        self.dialog_sdat.resize(600, 400)

        self.audioOutput = QtMultimedia.QAudioOutput(self)
        self.audioOutput.setVolume(0.2)
        self.audioBuffer = QtCore.QBuffer()
        self.mediaPlayer = QtMultimedia.QMediaPlayer(self)
        self.mediaPlayer.setAudioOutput(self.audioOutput)

        self.toolbar_sdat = QtWidgets.QToolBar("SDAT Toolbar")
        self.dialog_sdat.addToolBar(self.toolbar_sdat)

        self.action_playSdat = QtGui.QAction(QtGui.QIcon('icons\\control.png'), "Play Sound", self)
        self.action_playSdat.setStatusTip("Play a SWAV or SSEQ")
        self.action_playSdat.triggered.connect(self.sdatPlayCall)

        self.toolbar_sdat.addAction(self.action_playSdat)

        self.tree_sdat = lib.widget.EditorTree()
        self.tree_sdat.setColumnCount(3)
        self.dialog_sdat.setCentralWidget(self.tree_sdat)
        self.tree_sdat.setHeaderLabels(["File ID", "Name", "Type"])
        self.tree_sdat.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        #VX
        self.label_vxHeader_length = QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_length.setText("Duration(frames): ")
        self.label_vxHeader_length.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.field_vxHeader_length = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_vxHeader_length.setFont(self.font_caps)
        self.field_vxHeader_length.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_length.numfill = 8
        self.field_vxHeader_length.isInt = True
        self.field_vxHeader_length.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_length = QtWidgets.QVBoxLayout()
        self.layout_vxHeader_length.addWidget(self.label_vxHeader_length)
        self.layout_vxHeader_length.addWidget(self.field_vxHeader_length)

        self.label_vxHeader_framerate = QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_framerate.setText("Frame rate: ")
        self.label_vxHeader_framerate.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.field_vxHeader_framerate = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_vxHeader_framerate.setDecimals(16) # increase precision to allow spinbox to respect range
        self.field_vxHeader_framerate.setRange(0x00000000,65535.9999847412109375) # prevent impossible values (max is ffff.ffff)
        #self.field_vxHeader_framerate.numfill = 8
        self.field_vxHeader_framerate.textChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_framerate = QtWidgets.QVBoxLayout()
        self.layout_vxHeader_framerate.addWidget(self.label_vxHeader_framerate)
        self.layout_vxHeader_framerate.addWidget(self.field_vxHeader_framerate)

        self.label_vxHeader_frameSizeMax = QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_frameSizeMax.setText("Maximal frame data size: ")
        self.label_vxHeader_frameSizeMax.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.field_vxHeader_frameSizeMax = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_vxHeader_frameSizeMax.setFont(self.font_caps)
        self.field_vxHeader_frameSizeMax.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_frameSizeMax.numfill = 8
        self.field_vxHeader_frameSizeMax.isInt = True
        self.field_vxHeader_frameSizeMax.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_frameSizeMax = QtWidgets.QVBoxLayout()
        self.layout_vxHeader_frameSizeMax.addWidget(self.label_vxHeader_frameSizeMax)
        self.layout_vxHeader_frameSizeMax.addWidget(self.field_vxHeader_frameSizeMax)

        self.layout_vx_framesHeader = QtWidgets.QHBoxLayout()
        self.layout_vx_framesHeader.addItem(self.layout_vxHeader_length)
        self.layout_vx_framesHeader.addItem(self.layout_vxHeader_framerate)
        self.layout_vx_framesHeader.addItem(self.layout_vxHeader_frameSizeMax)

        self.label_vxHeader_streamCount = QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_streamCount.setText("Audio stream count: ")
        self.label_vxHeader_streamCount.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.field_vxHeader_streamCount = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_vxHeader_streamCount.setFont(self.font_caps)
        self.field_vxHeader_streamCount.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_streamCount.numfill = 8
        self.field_vxHeader_streamCount.isInt = True
        self.field_vxHeader_streamCount.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_streamCount = QtWidgets.QVBoxLayout()
        self.layout_vxHeader_streamCount.addWidget(self.label_vxHeader_streamCount)
        self.layout_vxHeader_streamCount.addWidget(self.field_vxHeader_streamCount)

        self.label_vxHeader_sampleRate = QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_sampleRate.setText("Sound sample rate(Hz): ")
        self.label_vxHeader_sampleRate.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.field_vxHeader_sampleRate = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_vxHeader_sampleRate.setFont(self.font_caps)
        self.field_vxHeader_sampleRate.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_sampleRate.numfill = 8
        self.field_vxHeader_sampleRate.isInt = True
        self.field_vxHeader_sampleRate.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_sampleRate = QtWidgets.QVBoxLayout()
        self.layout_vxHeader_sampleRate.addWidget(self.label_vxHeader_sampleRate)
        self.layout_vxHeader_sampleRate.addWidget(self.field_vxHeader_sampleRate)

        self.label_vxHeader_audioExtraDataOffset = QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_audioExtraDataOffset.setText("Extra audio data offset: ")
        self.label_vxHeader_audioExtraDataOffset.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.field_vxHeader_audioExtraDataOffset = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_vxHeader_audioExtraDataOffset.setFont(self.font_caps)
        self.field_vxHeader_audioExtraDataOffset.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_audioExtraDataOffset.numfill = 8
        self.field_vxHeader_audioExtraDataOffset.isInt = True
        self.field_vxHeader_audioExtraDataOffset.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_audioExtraDataOffset = QtWidgets.QVBoxLayout()
        self.layout_vxHeader_audioExtraDataOffset.addWidget(self.label_vxHeader_audioExtraDataOffset)
        self.layout_vxHeader_audioExtraDataOffset.addWidget(self.field_vxHeader_audioExtraDataOffset)

        self.layout_vx_soundHeader = QtWidgets.QHBoxLayout()
        self.layout_vx_soundHeader.addItem(self.layout_vxHeader_streamCount)
        self.layout_vx_soundHeader.addItem(self.layout_vxHeader_sampleRate)
        self.layout_vx_soundHeader.addItem(self.layout_vxHeader_audioExtraDataOffset)

        self.label_vxHeader_width = QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_width.setText("Frame width(pixels): ")
        self.label_vxHeader_width.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.field_vxHeader_width = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_vxHeader_width.setFont(self.font_caps)
        self.field_vxHeader_width.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_width.numfill = 8
        self.field_vxHeader_width.isInt = True
        self.field_vxHeader_width.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_width = QtWidgets.QVBoxLayout()
        self.layout_vxHeader_width.addWidget(self.label_vxHeader_width)
        self.layout_vxHeader_width.addWidget(self.field_vxHeader_width)

        self.label_vxHeader_height = QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_height.setText("Frame height(pixels): ")
        self.label_vxHeader_height.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.field_vxHeader_height = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_vxHeader_height.setFont(self.font_caps)
        self.field_vxHeader_height.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_height.numfill = 8
        self.field_vxHeader_height.isInt = True
        self.field_vxHeader_height.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_height = QtWidgets.QVBoxLayout()
        self.layout_vxHeader_height.addWidget(self.label_vxHeader_height)
        self.layout_vxHeader_height.addWidget(self.field_vxHeader_height)

        self.layout_vx_frameSize = QtWidgets.QHBoxLayout()
        self.layout_vx_frameSize.addItem(self.layout_vxHeader_width)
        self.layout_vx_frameSize.addItem(self.layout_vxHeader_height)

        self.label_vxHeader_quantiser = QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_quantiser.setText("Quantiser: ")
        self.label_vxHeader_quantiser.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.field_vxHeader_quantizer = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_vxHeader_quantizer.setFont(self.font_caps)
        self.field_vxHeader_quantizer.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_quantizer.numfill = 8
        self.field_vxHeader_quantizer.isInt = True
        self.field_vxHeader_quantizer.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_quantiser = QtWidgets.QVBoxLayout()
        self.layout_vxHeader_quantiser.addWidget(self.label_vxHeader_quantiser)
        self.layout_vxHeader_quantiser.addWidget(self.field_vxHeader_quantizer)

        self.label_vxHeader_seekTableOffset = QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_seekTableOffset.setText("Seek table offset: ")
        self.label_vxHeader_seekTableOffset.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.field_vxHeader_seekTableOffset = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_vxHeader_seekTableOffset.setFont(self.font_caps)
        self.field_vxHeader_seekTableOffset.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_seekTableOffset.numfill = 8
        self.field_vxHeader_seekTableOffset.isInt = True
        self.field_vxHeader_seekTableOffset.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_seekTableOffset = QtWidgets.QVBoxLayout()
        self.layout_vxHeader_seekTableOffset.addWidget(self.label_vxHeader_seekTableOffset)
        self.layout_vxHeader_seekTableOffset.addWidget(self.field_vxHeader_seekTableOffset)

        self.label_vxHeader_seekTableEntryCount = QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_seekTableEntryCount.setText("Seek table entry count: ")
        self.label_vxHeader_seekTableEntryCount.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.field_vxHeader_seekTableEntryCount = lib.widget.BetterSpinBox(self.page_explorer)
        self.field_vxHeader_seekTableEntryCount.setFont(self.font_caps)
        self.field_vxHeader_seekTableEntryCount.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_seekTableEntryCount.numfill = 8
        self.field_vxHeader_seekTableEntryCount.isInt = True
        self.field_vxHeader_seekTableEntryCount.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_seekTableEntryCount = QtWidgets.QVBoxLayout()
        self.layout_vxHeader_seekTableEntryCount.addWidget(self.label_vxHeader_seekTableEntryCount)
        self.layout_vxHeader_seekTableEntryCount.addWidget(self.field_vxHeader_seekTableEntryCount)

        self.layout_vx_seekTable = QtWidgets.QHBoxLayout()
        self.layout_vx_seekTable.addItem(self.layout_vxHeader_seekTableOffset)
        self.layout_vx_seekTable.addItem(self.layout_vxHeader_seekTableEntryCount)

        self.file_content.addItem(self.layout_vx_framesHeader)
        self.file_content.addItem(self.layout_vx_soundHeader)
        self.file_content.addItem(self.layout_vx_frameSize)
        self.file_content.addItem(self.layout_vxHeader_quantiser)
        self.file_content.addItem(self.layout_vx_seekTable)

        # File callers
        self.FILEOPEN_WIDGETS: list[QtWidgets.QWidget] = [self.tree, self.viewAdaptAction, self.viewEndialogAction, self.viewGraphicAction, self.displayRawAction]
        # Contents of widget sets
        self.WIDGETS_EMPTY: list[QtWidgets.QWidget] = [self.file_content_text]
        self.WIDGETS_HEX: list[QtWidgets.QWidget] = [self.file_content_text, self.checkbox_textoverwite]
        self.WIDGETS_TEXT: list[QtWidgets.QWidget] = [self.file_content_text, self.checkbox_textoverwite, self.dropdown_textindex]
        self.WIDGETS_GRAPHIC: list[QtWidgets.QWidget] = [
            self.file_content_gfx,
            self.checkbox_depthUpdate,
            self.label_depthUpdate,
            self.dropdown_gfx_depth,
            self.dropdown_gfx_index,
            self.dropdown_gfx_subindex,
            self.dropdown_gfx_palette,
            self.field_tile_width,
            self.label_tile_width,
            self.field_tile_height,
            self.label_tile_height,
            self.field_tiles_per_row,
            self.label_tiles_per_row,
            self.field_tiles_per_column,
            self.label_tiles_per_column,
            self.widget_colorpick
            ]
        self.WIDGETS_OAM: list[QtWidgets.QWidget] = [
            self.file_content_oam,
            self.tabs_oam,
            self.dropdown_oam_entry
            ]
        self.WIDGETS_PANM: list[QtWidgets.QWidget] = [
            self.dropdown_panm_entry,
            self.dropdown_panm_frame,
            self.field_panm_frameId,
            self.field_panm_frameDuration,
            self.checkbox_panm_loop,
            self.field_panm_loopStart,
            self.label_panm_colorSlots,
            self.field_panm_colorSlot0,
            self.field_panm_colorSlot1,
            self.widget_colorpick
        ]
        self.WIDGETS_FONT: list[QtWidgets.QWidget] = [
            self.file_content_gfx,
            self.field_tiles_per_row,
            self.label_tiles_per_row,
            self.field_tiles_per_column,
            self.label_tiles_per_column,
            self.field_font_size,
            self.label_font_size,
            self.field_font_width,
            self.label_font_width,
            self.field_font_height,
            self.label_font_height,
            self.label_font_indexingSpace,
            self.label_font_charCount,
            self.label_font_unusedStr,
            self.widget_colorpick
            ]
        self.WIDGETS_SOUND: list[QtWidgets.QWidget] = [
            ]
        self.WIDGETS_VX: list[QtWidgets.QWidget] = [
            self.field_vxHeader_length,
            self.label_vxHeader_length,
            self.field_vxHeader_width,
            self.label_vxHeader_width,
            self.field_vxHeader_height,
            self.label_vxHeader_height,
            self.field_vxHeader_streamCount,
            self.label_vxHeader_streamCount,
            self.field_vxHeader_framerate,
            self.label_vxHeader_framerate,
            self.field_vxHeader_sampleRate,
            self.label_vxHeader_sampleRate,
            self.field_vxHeader_quantizer,
            self.label_vxHeader_quantiser,
            self.field_vxHeader_frameSizeMax,
            self.label_vxHeader_frameSizeMax,
            self.field_vxHeader_audioExtraDataOffset,
            self.label_vxHeader_audioExtraDataOffset,
            self.field_vxHeader_seekTableOffset,
            self.label_vxHeader_seekTableOffset,
            self.field_vxHeader_seekTableEntryCount,
            self.label_vxHeader_seekTableEntryCount
            ]
        self.file_editor_show("Empty")

        # Level Editor(WIP)
        self.layout_level_editpannel = QtWidgets.QVBoxLayout()

        self.button_level_save = QtWidgets.QPushButton("Save level", self.page_leveleditor)
        self.button_level_save.setMaximumWidth(100)
        self.button_level_save.setToolTip("save this level's changes")
        self.button_level_save.pressed.connect(self.save_level)
        self.button_level_save.setDisabled(True)

        self.dropdown_level_area = QtWidgets.QComboBox(self.page_leveleditor)
        self.dropdown_level_area.setToolTip("Choose an area to modify")
        self.dropdown_level_area.currentIndexChanged.connect(self.loadLevel)
        self.dropdown_level_area.setDisabled(True)

        self.dropdown_level_type = QtWidgets.QComboBox(self.page_leveleditor)
        self.dropdown_level_type.setToolTip("Choose between normal level and scanner map (if applicable)")
        self.dropdown_level_type.currentIndexChanged.connect(self.loadLevel)
        self.dropdown_level_type.setDisabled(True)

        self.radio_radar_LX = QtWidgets.QRadioButton(self.page_leveleditor)
        self.radio_radar_LX.setText("Model LX")
        self.radio_radar_PX = QtWidgets.QRadioButton(self.page_leveleditor)
        self.radio_radar_PX.setText("Model PX")
        self.buttonGroup_radar_tilesetType = QtWidgets.QButtonGroup()
        self.buttonGroup_radar_tilesetType.addButton(self.radio_radar_LX, 2) # rindex to getData
        self.buttonGroup_radar_tilesetType.addButton(self.radio_radar_PX, 1)
        self.buttonGroup_radar_tilesetType.idReleased.connect(self.loadLevel)
        self.group_radar_tilesetType = QtWidgets.QGroupBox(self.page_leveleditor)
        self.group_radar_tilesetType.setTitle("Radar mode")
        self.group_radar_tilesetType.setLayout(QtWidgets.QVBoxLayout())
        self.group_radar_tilesetType.layout().addWidget(self.radio_radar_LX)
        self.group_radar_tilesetType.layout().addWidget(self.radio_radar_PX)
        self.group_radar_tilesetType.setDisabled(True)

        self.dropdown_metaTile_collisionShape = QtWidgets.QComboBox(self.page_leveleditor)
        self.dropdown_metaTile_collisionShape.setToolTip("Choose collision geometry to apply")
        self.dropdown_metaTile_collisionShape.addItems(["00 - Air",
                                                        "01 - Solid",
                                                        "02 - lower 2x1 slope /",
                                                        "03 - upper 2x1 slope /",
                                                        "04 - lower 4x1 slope /",
                                                        "05 - lower middle 4x1 slope /",
                                                        "06 - upper middle 4x1 slope /",
                                                        "07 - upper 4x1 slope /",
                                                        "08 - upper 2x1 slope \\",
                                                        "09 - lower 2x1 slope \\",
                                                        "0A - upper 4x1 slope \\",
                                                        "0B - upper middle 4x1 slope \\",
                                                        "0C - lower middle 4x1 slope \\",
                                                        "0D - lower 4x1 slope \\",
                                                        "0E - ladder end",
                                                        "0F - ladder"])
        self.dropdown_metaTile_collisionShape.currentIndexChanged.connect(self.changeTileShape)
        self.dropdown_metaTile_collisionShape.setDisabled(True)

        self.dropdown_metaTile_collisionMaterial = QtWidgets.QComboBox(self.page_leveleditor)
        self.dropdown_metaTile_collisionMaterial.setToolTip("Choose collision material (?) to apply")
        self.dropdown_metaTile_collisionMaterial.addItems(["00 - Normal",
                                                        "01 - ???",
                                                        "02 - ???",
                                                        "03 - ???",
                                                        "04 - ???",
                                                        "05 - ???",
                                                        "06 - ???",
                                                        "07 - ???",
                                                        "08 - metal?",
                                                        "09 - ???",
                                                        "0A - ???",
                                                        "0B - ???",
                                                        "0C - ???",
                                                        "0D - ???",
                                                        "0E - ???",
                                                        "0F - swamp?"])
        self.dropdown_metaTile_collisionMaterial.currentIndexChanged.connect(self.changeTileMaterial)
        self.dropdown_metaTile_collisionMaterial.setDisabled(True)

        self.group_metaTile_gfx = QtWidgets.QGroupBox(self.page_leveleditor)
        self.group_metaTile_gfx.setTitle("Meta Tile Graphics")
        self.group_metaTile_gfx.setLayout(QtWidgets.QGridLayout())
        self.group_metaTile_gfx.setDisabled(True)

        self.field_metaTile_topLeft_id = lib.widget.BetterSpinBox(self.page_leveleditor)
        self.field_metaTile_topLeft_id.setToolTip("Tile ID")
        self.field_metaTile_topLeft_id.isInt = True
        self.field_metaTile_topLeft_id.numbase = self.displayBase
        self.field_metaTile_topLeft_id.numfill = 3
        self.field_metaTile_topLeft_id.setRange(0x0000, 0xFFFF)
        self.field_metaTile_topLeft_id.valueChanged.connect(lambda: self.changeTileGfx(0, 0xFFFF-0x03FF, self.field_metaTile_topLeft_id.value()))
        self.checkbox_metaTile_topLeft_flipH = QtWidgets.QCheckBox(self.page_leveleditor)
        self.checkbox_metaTile_topLeft_flipH.setText("H")
        self.checkbox_metaTile_topLeft_flipH.checkStateChanged.connect(lambda: self.changeTileGfx(0, 0xFFFF-0x0400, self.checkbox_metaTile_topLeft_flipH.isChecked()))
        self.field_metaTile_topLeft_attr = lib.widget.BetterSpinBox(self.page_leveleditor)
        self.field_metaTile_topLeft_attr.setToolTip("Palette ID")
        self.field_metaTile_topLeft_attr.isInt = True
        self.field_metaTile_topLeft_attr.numbase = self.displayBase
        self.field_metaTile_topLeft_attr.setRange(0x0000, 0xFFFF)
        self.field_metaTile_topLeft_attr.valueChanged.connect(lambda: self.changeTileGfx(0, 0xFFFF-0xF000, self.field_metaTile_topLeft_attr.value()))
        self.checkbox_metaTile_topLeft_flipV = QtWidgets.QCheckBox(self.page_leveleditor)
        self.checkbox_metaTile_topLeft_flipV.setText("V")
        self.checkbox_metaTile_topLeft_flipV.checkStateChanged.connect(lambda: self.changeTileGfx(0, 0xFFFF-0x0800, self.checkbox_metaTile_topLeft_flipV.isChecked()))

        self.field_metaTile_topRight_id = lib.widget.BetterSpinBox(self.page_leveleditor)
        self.field_metaTile_topRight_id.setToolTip("Tile ID")
        self.field_metaTile_topRight_id.isInt = True
        self.field_metaTile_topRight_id.numbase = self.displayBase
        self.field_metaTile_topRight_id.numfill = 3
        self.field_metaTile_topRight_id.setRange(0x0000, 0xFFFF)
        self.field_metaTile_topRight_id.valueChanged.connect(lambda: self.changeTileGfx(1, 0xFFFF-0x03FF, self.field_metaTile_topRight_id.value()))
        self.checkbox_metaTile_topRight_flipH = QtWidgets.QCheckBox(self.page_leveleditor)
        self.checkbox_metaTile_topRight_flipH.setText("H")
        self.checkbox_metaTile_topRight_flipH.checkStateChanged.connect(lambda: self.changeTileGfx(1, 0xFFFF-0x0400, self.checkbox_metaTile_topRight_flipH.isChecked()))
        self.field_metaTile_topRight_attr = lib.widget.BetterSpinBox(self.page_leveleditor)
        self.field_metaTile_topRight_attr.setToolTip("Palette ID")
        self.field_metaTile_topRight_attr.isInt = True
        self.field_metaTile_topRight_attr.numbase = self.displayBase
        self.field_metaTile_topRight_attr.setRange(0x0000, 0xFFFF)
        self.field_metaTile_topRight_attr.valueChanged.connect(lambda: self.changeTileGfx(1, 0xFFFF-0xF000, self.field_metaTile_topRight_attr.value()))
        self.checkbox_metaTile_topRight_flipV = QtWidgets.QCheckBox(self.page_leveleditor)
        self.checkbox_metaTile_topRight_flipV.setText("V")
        self.checkbox_metaTile_topRight_flipV.checkStateChanged.connect(lambda: self.changeTileGfx(1, 0xFFFF-0x0800, self.checkbox_metaTile_topRight_flipV.isChecked()))

        self.field_metaTile_bottomLeft_id = lib.widget.BetterSpinBox(self.page_leveleditor)
        self.field_metaTile_bottomLeft_id.setToolTip("Tile ID")
        self.field_metaTile_bottomLeft_id.isInt = True
        self.field_metaTile_bottomLeft_id.numbase = self.displayBase
        self.field_metaTile_bottomLeft_id.numfill = 3
        self.field_metaTile_bottomLeft_id.setRange(0x0000, 0xFFFF)
        self.field_metaTile_bottomLeft_id.valueChanged.connect(lambda: self.changeTileGfx(2, 0xFFFF-0x03FF, self.field_metaTile_bottomLeft_id.value()))
        self.checkbox_metaTile_bottomLeft_flipH = QtWidgets.QCheckBox(self.page_leveleditor)
        self.checkbox_metaTile_bottomLeft_flipH.setText("H")
        self.checkbox_metaTile_bottomLeft_flipH.checkStateChanged.connect(lambda: self.changeTileGfx(2, 0xFFFF-0x0400, self.checkbox_metaTile_bottomLeft_flipH.isChecked()))
        self.field_metaTile_bottomLeft_attr = lib.widget.BetterSpinBox(self.page_leveleditor)
        self.field_metaTile_bottomLeft_attr.setToolTip("Palette ID")
        self.field_metaTile_bottomLeft_attr.isInt = True
        self.field_metaTile_bottomLeft_attr.numbase = self.displayBase
        self.field_metaTile_bottomLeft_attr.setRange(0x0000, 0xFFFF)
        self.field_metaTile_bottomLeft_attr.valueChanged.connect(lambda: self.changeTileGfx(2, 0xFFFF-0xF000, self.field_metaTile_bottomLeft_attr.value()))
        self.checkbox_metaTile_bottomLeft_flipV = QtWidgets.QCheckBox(self.page_leveleditor)
        self.checkbox_metaTile_bottomLeft_flipV.setText("V")
        self.checkbox_metaTile_bottomLeft_flipV.checkStateChanged.connect(lambda: self.changeTileGfx(2, 0xFFFF-0x0800, self.checkbox_metaTile_bottomLeft_flipV.isChecked()))

        self.field_metaTile_bottomRight_id = lib.widget.BetterSpinBox(self.page_leveleditor)
        self.field_metaTile_bottomRight_id.setToolTip("Tile ID")
        self.field_metaTile_bottomRight_id.isInt = True
        self.field_metaTile_bottomRight_id.numbase = self.displayBase
        self.field_metaTile_bottomRight_id.numfill = 3
        self.field_metaTile_bottomRight_id.setRange(0x0000, 0xFFFF)
        self.field_metaTile_bottomRight_id.valueChanged.connect(lambda: self.changeTileGfx(3, 0xFFFF-0x03FF, self.field_metaTile_bottomRight_id.value()))
        self.checkbox_metaTile_bottomRight_flipH = QtWidgets.QCheckBox(self.page_leveleditor)
        self.checkbox_metaTile_bottomRight_flipH.setText("H")
        self.checkbox_metaTile_bottomRight_flipH.checkStateChanged.connect(lambda: self.changeTileGfx(3, 0xFFFF-0x0400, self.checkbox_metaTile_bottomRight_flipH.isChecked()))
        self.field_metaTile_bottomRight_attr = lib.widget.BetterSpinBox(self.page_leveleditor)
        self.field_metaTile_bottomRight_attr.setToolTip("Palette ID")
        self.field_metaTile_bottomRight_attr.isInt = True
        self.field_metaTile_bottomRight_attr.numbase = self.displayBase
        self.field_metaTile_bottomRight_attr.setRange(0x0000, 0xFFFF)
        self.field_metaTile_bottomRight_attr.valueChanged.connect(lambda: self.changeTileGfx(3, 0xFFFF-0xF000, self.field_metaTile_bottomRight_attr.value()))
        self.checkbox_metaTile_bottomRight_flipV = QtWidgets.QCheckBox(self.page_leveleditor)
        self.checkbox_metaTile_bottomRight_flipV.setText("V")
        self.checkbox_metaTile_bottomRight_flipV.checkStateChanged.connect(lambda: self.changeTileGfx(3, 0xFFFF-0x0800, self.checkbox_metaTile_bottomRight_flipV.isChecked()))

        self.group_metaTile_gfx.layout().addWidget(self.field_metaTile_topLeft_id, 0, 0)
        self.group_metaTile_gfx.layout().addWidget(self.checkbox_metaTile_topLeft_flipH, 0, 1)
        self.group_metaTile_gfx.layout().addWidget(self.field_metaTile_topLeft_attr, 1, 0)
        self.group_metaTile_gfx.layout().addWidget(self.checkbox_metaTile_topLeft_flipV, 1, 1)
        self.group_metaTile_gfx.layout().addWidget(self.field_metaTile_topRight_id, 0, 2)
        self.group_metaTile_gfx.layout().addWidget(self.checkbox_metaTile_topRight_flipH, 0, 3)
        self.group_metaTile_gfx.layout().addWidget(self.field_metaTile_topRight_attr, 1, 2)
        self.group_metaTile_gfx.layout().addWidget(self.checkbox_metaTile_topRight_flipV, 1, 3)
        self.group_metaTile_gfx.layout().addWidget(QtWidgets.QLabel(), 2, 0, 1, 3)
        self.group_metaTile_gfx.layout().addWidget(self.field_metaTile_bottomLeft_id, 3, 0)
        self.group_metaTile_gfx.layout().addWidget(self.checkbox_metaTile_bottomLeft_flipH, 3, 1)
        self.group_metaTile_gfx.layout().addWidget(self.field_metaTile_bottomLeft_attr, 4, 0)
        self.group_metaTile_gfx.layout().addWidget(self.checkbox_metaTile_bottomLeft_flipV, 4, 1)
        self.group_metaTile_gfx.layout().addWidget(self.field_metaTile_bottomRight_id, 3, 2)
        self.group_metaTile_gfx.layout().addWidget(self.checkbox_metaTile_bottomRight_flipH, 3, 3)
        self.group_metaTile_gfx.layout().addWidget(self.field_metaTile_bottomRight_attr, 4, 2)
        self.group_metaTile_gfx.layout().addWidget(self.checkbox_metaTile_bottomRight_flipV, 4, 3)

        self.checkbox_metaTile_attrSpike = QtWidgets.QCheckBox(self.page_leveleditor)
        self.checkbox_metaTile_attrSpike.setText("Spike")
        self.checkbox_metaTile_attrSpike.checkStateChanged.connect(lambda: self.changeTileAttr(0b11111110, self.checkbox_metaTile_attrSpike.isChecked()))
        self.checkbox_metaTile_attrSpike.setDisabled(True)
        self.checkbox_metaTile_attrWater = QtWidgets.QCheckBox(self.page_leveleditor)
        self.checkbox_metaTile_attrWater.setText("Underwater")
        self.checkbox_metaTile_attrWater.checkStateChanged.connect(lambda: self.changeTileAttr(0b11111101, self.checkbox_metaTile_attrWater.isChecked()))
        self.checkbox_metaTile_attrWater.setDisabled(True)
        self.checkbox_metaTile_attrNoCeilHang = QtWidgets.QCheckBox(self.page_leveleditor)
        self.checkbox_metaTile_attrNoCeilHang.setText("No ceiling hang")
        self.checkbox_metaTile_attrNoCeilHang.checkStateChanged.connect(lambda: self.changeTileAttr(0b11111011, self.checkbox_metaTile_attrNoCeilHang.isChecked()))
        self.checkbox_metaTile_attrNoCeilHang.setDisabled(True)
        self.checkbox_metaTile_attrNoWalljump = QtWidgets.QCheckBox(self.page_leveleditor)
        self.checkbox_metaTile_attrNoWalljump.setText("No walljump")
        self.checkbox_metaTile_attrNoWalljump.checkStateChanged.connect(lambda: self.changeTileAttr(0b11110111, self.checkbox_metaTile_attrNoWalljump.isChecked()))
        self.checkbox_metaTile_attrNoWalljump.setDisabled(True)
        self.checkbox_metaTile_attrSand = QtWidgets.QCheckBox(self.page_leveleditor)
        self.checkbox_metaTile_attrSand.setText("Quicksand")
        self.checkbox_metaTile_attrSand.checkStateChanged.connect(lambda: self.changeTileAttr(0b11101111, self.checkbox_metaTile_attrSand.isChecked()))
        self.checkbox_metaTile_attrSand.setDisabled(True)
        self.radio_metaTile_attrNone = QtWidgets.QRadioButton(self.page_leveleditor)
        self.radio_metaTile_attrNone.setText("Normal")
        self.radio_metaTile_attrConveyR = QtWidgets.QRadioButton(self.page_leveleditor)
        self.radio_metaTile_attrConveyR.setText("Conveyor >>")
        self.radio_metaTile_attrConveyL = QtWidgets.QRadioButton(self.page_leveleditor)
        self.radio_metaTile_attrConveyL.setText("Conveyor <<")
        self.radio_metaTile_attrIce = QtWidgets.QRadioButton(self.page_leveleditor)
        self.radio_metaTile_attrIce.setText("Ice")
        self.buttonGroup_metaTile_attrConvey = QtWidgets.QButtonGroup(self.page_leveleditor)
        self.buttonGroup_metaTile_attrConvey.addButton(self.radio_metaTile_attrNone, 0)
        self.buttonGroup_metaTile_attrConvey.addButton(self.radio_metaTile_attrConveyR, 1)
        self.buttonGroup_metaTile_attrConvey.addButton(self.radio_metaTile_attrConveyL, 2)
        self.buttonGroup_metaTile_attrConvey.addButton(self.radio_metaTile_attrIce, 3)
        self.buttonGroup_metaTile_attrConvey.idReleased.connect(lambda: self.changeTileAttr(0b10011111, self.buttonGroup_metaTile_attrConvey.checkedId()))
        self.group_metaTile_attrConvey = QtWidgets.QGroupBox(self.page_leveleditor)
        self.group_metaTile_attrConvey.setTitle("Grounded movement")
        self.group_metaTile_attrConvey.setLayout(QtWidgets.QVBoxLayout())
        self.group_metaTile_attrConvey.layout().addWidget(self.radio_metaTile_attrNone)
        self.group_metaTile_attrConvey.layout().addWidget(self.radio_metaTile_attrConveyR)
        self.group_metaTile_attrConvey.layout().addWidget(self.radio_metaTile_attrConveyL)
        self.group_metaTile_attrConvey.layout().addWidget(self.radio_metaTile_attrIce)
        self.group_metaTile_attrConvey.setDisabled(True)
        self.checkbox_metaTile_attrPlat = QtWidgets.QCheckBox(self.page_leveleditor)
        self.checkbox_metaTile_attrPlat.setText("Platform (top collision only)")
        self.checkbox_metaTile_attrPlat.checkStateChanged.connect(lambda: self.changeTileAttr(0b01111111, self.checkbox_metaTile_attrPlat.isChecked()))
        self.checkbox_metaTile_attrPlat.setDisabled(True)

        self.layout_metaTile_shape = QtWidgets.QVBoxLayout()
        self.layout_metaTile_shape.addWidget(self.dropdown_metaTile_collisionShape)
        self.layout_metaTile_shape.addWidget(self.dropdown_metaTile_collisionMaterial)
        self.layout_metaTile_shape.addWidget(self.group_metaTile_gfx)

        self.layout_metaTile_attr = QtWidgets.QGridLayout()
        self.layout_metaTile_attr.setContentsMargins(10, 10, 0, 10)
        self.layout_metaTile_attr.addWidget(self.checkbox_metaTile_attrSpike, 0, 0)
        self.layout_metaTile_attr.addWidget(self.checkbox_metaTile_attrWater, 1, 0)
        self.layout_metaTile_attr.addWidget(self.checkbox_metaTile_attrNoCeilHang, 2, 0)
        self.layout_metaTile_attr.addWidget(self.checkbox_metaTile_attrNoWalljump, 3, 0)
        self.layout_metaTile_attr.addWidget(self.checkbox_metaTile_attrSand, 4, 0)
        self.layout_metaTile_attr.addWidget(self.group_metaTile_attrConvey, 0, 1, 6, 1)
        self.layout_metaTile_attr.addWidget(self.checkbox_metaTile_attrPlat, 5, 0)

        self.layout_level_area = QtWidgets.QHBoxLayout()
        self.layout_level_area.addWidget(self.dropdown_level_area)
        self.layout_level_area.addWidget(self.dropdown_level_type)
        self.layout_level_area.addWidget(self.group_radar_tilesetType)

        self.layout_metaTile_properties = QtWidgets.QHBoxLayout()
        self.layout_metaTile_properties.addItem(self.layout_metaTile_shape)
        self.layout_metaTile_properties.addItem(self.layout_metaTile_attr)

        self.gfx_scene_level = lib.widget.LevelView(self.page_leveleditor)
        self.gfx_scene_tileset = lib.widget.TilesetView(self.page_leveleditor)
        self.gfx_scene_tileset.scene().selectionChanged.connect(self.loadTileProperties)

        self.page_leveleditor.layout().addItem(self.layout_level_editpannel)
        self.layout_level_editpannel.addWidget(self.button_level_save)
        self.layout_level_editpannel.addItem(self.layout_level_area)
        self.layout_level_editpannel.addItem(self.layout_metaTile_properties)
        self.layout_level_editpannel.addWidget(self.gfx_scene_tileset)

        self.page_leveleditor.layout().addWidget(self.gfx_scene_level)

        # Tweaks(Coming Soon™)
        self.tabs_tweaks = QtWidgets.QTabWidget(self.page_tweaks)

        self.dropdown_tweak_target = QtWidgets.QComboBox(self.page_tweaks)
        #self.dropdown_tweak_target.setGeometry(125, 75, 125, 25)
        self.dropdown_tweak_target.setToolTip("Choose a target to appy tweaks to")
        self.dropdown_tweak_target.addItems(["Other", "Player", "Player(Hu)", "Player(X)", "Player(Zx)", "Player(Fx)", "Player(Hx)", "Player(Lx)", "Player(Px)", "Player(Ox)"])
        #self.dropdown_tweak_target.currentTextChanged.connect(self.tweakTargetCall)
        self.dropdown_tweak_target.hide()
        self.page_tweaks.layout().addWidget(self.dropdown_tweak_target)
        self.page_tweaks.layout().addWidget(self.tabs_tweaks)

        self.page_tweaks_stats = QtWidgets.QWidget(self.tabs_tweaks)
        self.page_tweaks_stats.setLayout(QtWidgets.QGridLayout())

        self.page_tweaks_physics = QtWidgets.QWidget(self.tabs_tweaks)
        self.page_tweaks_physics.setLayout(QtWidgets.QGridLayout())

        self.page_tweaks_behaviour = QtWidgets.QWidget(self.tabs_tweaks)
        self.page_tweaks_behaviour.setLayout(QtWidgets.QGridLayout())

        self.page_tweaks_misc = QtWidgets.QWidget(self.tabs_tweaks)
        self.page_tweaks_misc.setLayout(QtWidgets.QGridLayout())

        self.tabs_tweaks.addTab(self.page_tweaks_stats, "Stats")


        self.tabs_tweaks.addTab(self.page_tweaks_physics, "Physics")


        self.tabs_tweaks.addTab(self.page_tweaks_behaviour, "Behaviour")

        self.checkbox_paralyzed = QtWidgets.QCheckBox(self.page_tweaks_behaviour)
        self.page_tweaks_behaviour.layout().addWidget(self.checkbox_paralyzed)


        self.tabs_tweaks.addTab(self.page_tweaks_misc, "Misc.")


        # Patches
        self.tree_patches = lib.widget.EditorTree(self.page_patches)
        self.page_patches.layout().addWidget(self.tree_patches)
        self.tree_patches.setColumnCount(4)
        self.tree_patches.setHeaderLabels(["Enabed", "Address", "Name", "Type", "Size"])
        self.tree_patches.itemChanged.connect(self.patch_game)
        self.tree_patches_checkboxes = [] # stores the state of checkboxes for complex checkbox logic

        # Shortcuts
        #QtWidgets.QKeySequenceEdit()

        self.setStatusBar(QtWidgets.QStatusBar(self))

    def progressShow(self):
        self.window_progress.move(self.pos().x() + (self.width() - self.window_progress.width())//2, self.pos().y() + self.height()//2) # center progress bar
        self.progress.setValue(0)
        self.label_progress.setText("")
        self.window_progress.show()

    def progressUpdate(self, percent: int, status: str=""):
        self.progress.setValue(percent)
        self.label_progress.setText(status)
        app.processEvents()

    def progressHide(self):
        self.progress.setValue(0)
        self.label_progress.setText("")
        self.window_progress.close()

    """
    def runTasks(self, runnableInfo_list: list[list[QtCore.QRunnable, list[QtCore.Q_ARG], QtCore.pyqtSignal, lambda _: _]]):
        pool = QtCore.QThreadPool.globalInstance()
        for runnableInfo in runnableInfo_list:
            # 2. Instantiate the subclass of QRunnable
            runnable_inst = runnableInfo[0](*runnableInfo[1])
            app.processEvents()
            getattr(runnable_inst.signals, runnableInfo[2]).connect(runnableInfo[3])
            # 3. Call start()
            pool.start(runnable_inst)
            self.setWindowTitle(self.windowTitle() + " (Running " + str(pool.activeThreadCount()) + " Threads)")

    def clearTasks(self):
        pool = QtCore.QThreadPool.globalInstance()
        pool.clear()
        self.setWindowTitle(self.windowTitle().split(" (Running ")[0])
    """

    def file_fromItem(self, item: QtWidgets.QTreeWidgetItem):
        tree = item.treeWidget()
        name = ""
        data = bytes()
        obj = self.rom.files
        obj2 = None
        if tree == self.tree:
            name = item.text(1) + "." + item.text(2)
            data = obj[int(item.text(0))]
        else:
            if tree.ContextNameType == "[Filenames]":
                name = item.text(1) + ("." + item.text(2)).replace(".Folder", " and contents")
            else:
                name = tree.ContextNameType + item.text(0)
            if tree == self.tree_arm9: # 02000000 - 00004000 = 01FFC000
                obj = self.rom.arm9
                if item.text(2) == "True":
                    try: # convert dynamically according to base (also arm9 window should update on base change)
                        item_next = tree.itemBelow(item)
                        data = self.rom.arm9[lib.datconv.strToNum(item.text(0), self.displayBase) - 0x01FFC000 - 0x00004000:lib.datconv.strToNum(item.text(0), self.displayBase) - 0x01FFC000 - 0x00004000 + (lib.datconv.strToNum(item_next.text(0), self.displayBase) - lib.datconv.strToNum(item.text(0), self.displayBase))]
                    except Exception:
                        data = self.rom.arm9[lib.datconv.strToNum(item.text(0), self.displayBase) - 0x01FFC000 - 0x00004000:]
                else:
                    print("Explicit ARM9 code-sections are not (yet) supported")
                    return [b'', "", None, None]
                    #data = ndspy.codeCompression._compress(self.rom.loadArm9().sections[int(tree.indexFromItem(item).row())].data) #compressed
                name += ".bin"
            if tree == self.tree_arm7: # 02380000 - 0014E000 = 02232000
                self.rom.arm7EntryAddress
                obj = self.rom.arm7
                if item.text(2) == "True":
                    try:
                        item_next = tree.itemBelow(item)
                        data = self.rom.arm7[lib.datconv.strToNum(item.text(0), self.displayBase) - 0x02232000 - 0x0014E000:lib.datconv.strToNum(item.text(0), self.displayBase) - 0x02232000 - 0x0014E000 + (lib.datconv.strToNum(item_next.text(0), self.displayBase) - lib.datconv.strToNum(item.text(0), self.displayBase))]
                    except Exception:
                        data = self.rom.arm7[lib.datconv.strToNum(item.text(0), self.displayBase) - 0x02232000 - 0x0014E000]
                else:
                    print("Explicit ARM7 code-sections are not (yet) supported")
                    return [b'', "", None, None]
                    #ndspy.codeCompression.compress(self.rom.loadArm7().sections[int(tree.indexFromItem(item).row())].data)
                name += ".bin"
            if tree == self.tree_arm9Ovltable:
                data = self.rom.files[int(item.text(0))] #self.rom.arm9OverlayTable
                name += ".bin"
            if tree == self.tree_arm7Ovltable:
                data = self.rom.files[int(item.text(0))] #.loadArm7Overlays()[int(item.text(0))].data
                name += ".bin"
            if tree == self.tree_sdat:
                obj2 = self.sdat
                data_list = [
                self.sdat.sequences,
                self.sdat.sequenceArchives,
                self.sdat.banks,
                self.sdat.waveArchives,
                self.sdat.sequencePlayers,
                self.sdat.streams,
                self.sdat.streamPlayers,
                self.sdat.groups
                ]
                for category in data_list:
                    for file in category:
                        if file[0] == item.text(1):
                            obj2 = category
                            data = file#[1].save()
                            #print(data)
                            #if isinstance(data, tuple):
                            #    data = data[0]
                        elif item.parent() != None and file[0] == item.parent().text(1):
                            if item.text(2) == "SWAV":
                                data = file[1].waves[int(item.text(0))]
                            else:
                                data = file
        return [data, name, obj, obj2]
    
    def patches_reload(self):
        #print("call")
        self.tree_patches.blockSignals(True)
        #self.progress.show()
        self.tree_patches.clear()
        if self.rom.name.decode().replace(" ", "_") in lib.patchdat.GameEnum.__members__:
            patches = []
            for patch in lib.patchdat.GameEnum[self.rom.name.decode().replace(" ", "_")].value[1]:
                #self.progress.setValue(self.progress.value()+12)
                #QtWidgets.QTreeWidgetItem(None, ["", "<address>", "<patch name>", "<patch type>", "<size>"])
                if isinstance(patch[2], list): # if patch contains patches
                    patch_item = QtWidgets.QTreeWidgetItem(None, ["", "N/A", patch[0], patch[1], "0"])
                    patches.append(patch_item)
                    patch_size = 0
                    subPatchMatches = 0
                    for subPatch in patch:
                        if isinstance(subPatch, list):
                            subPatch_item = QtWidgets.QTreeWidgetItem(None, ["", str(lib.datconv.numToStr(subPatch[0], self.displayBase, self.displayAlphanumeric).zfill(8)), subPatch[1], "Patch Segment", str(lib.datconv.numToStr(len(subPatch[3].replace("-", "")), self.displayBase, self.displayAlphanumeric).zfill(1))])
                            subPatch_item.setToolTip(0, subPatch[3])
                            subPatch_item.setFlags(patch_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                            patch_item.addChild(subPatch_item)
                            patch_size += len(subPatch[3].replace("-", ""))
                            if self.rom.save()[subPatch[0]:subPatch[0]+len(subPatch[3])] == subPatch[3]:
                                subPatchMatches += 1
                                subPatch_item.setCheckState(0, QtCore.Qt.CheckState.Checked)
                            else:
                                subPatch_item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
                            self.tree_patches_checkboxes.append(subPatch_item.checkState(0))
                    patch_item.setText(4, f"{lib.datconv.numToStr(patch_size, self.displayBase, self.displayAlphanumeric).zfill(1)}")
                    patch_item.setFlags(patch_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                    if subPatchMatches == patch_item.childCount(): # Check for already applied patches
                        patch_item.setCheckState(0, QtCore.Qt.CheckState.Checked)
                    elif subPatchMatches > 0:
                        patch_item.setCheckState(0, QtCore.Qt.CheckState.PartiallyChecked)
                    else:
                        patch_item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
                    self.tree_patches_checkboxes.append(patch_item.checkState(0))
                else:
                    patch_item = QtWidgets.QTreeWidgetItem(None, ["", str(lib.datconv.numToStr(patch[0], self.displayBase, self.displayAlphanumeric).zfill(8)), patch[1], patch[2], str(lib.datconv.numToStr(len(patch[4].replace("-", "")), self.displayBase, self.displayAlphanumeric).zfill(1))])
                    patch_item.setToolTip(0, str(patch[4]))
                    patches.append(patch_item)
                    patch_item.setFlags(patch_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                    if self.rom.save()[patch[0]:patch[0]+len(patch[4])] == patch[4]: # Check for already applied patches
                        patch_item.setCheckState(0, QtCore.Qt.CheckState.Checked)
                    else:
                        patch_item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
                    self.tree_patches_checkboxes.append(patch_item.checkState(0))
            self.tree_patches.addTopLevelItems(patches)
        self.tree_patches.blockSignals(False)
        #self.progress.setValue(100)
        #self.progress.close()

    def openCall(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "NDS Files (*.nds *.srl);; All Files (*)",
            options=QtWidgets.QFileDialog.Option.DontUseNativeDialog,
        )
        if not filename == ("", ""):
            self.loadROM(filename[0])

    def loadFat(self): # ndspy already does this to load the ROM properly, but does not store any of the info on the fat in the final rom object
        self.rom_fat.clear()
        rom = self.rom.save()
        fat_offset = int.from_bytes(rom[0x48:0x4C], "little") # read from nds header
        fat_size = int.from_bytes(rom[0x4C:0x50], "little")
        for i in range(fat_size//8): # 8 bytes for start and end address of each file, so this is like range(fileCount)
            self.rom_fat.append(int.from_bytes(rom[fat_offset+i*8:fat_offset+i*8+4], "little"))

    def loadROM(self, fname: str):
        # reset stuff to prevent conflicts
        self.tree.setCurrentItem(None)
        self.field_address.setRange(0,0) # set address to 0 for consistency with the fact that no file is selected
        self.rom = None
        self.sdat = None
        self.treeUpdate()
        self.tree_patches.clear()
        self.disable_editing_ui()

        if fname == "" or not os.path.exists(fname): return

        self.progressShow() # progress bar
        self.progressUpdate(0, "Loading ROM")
        #self.runTasks([[RunnableDisplayProgress, [], "valueChanged", self.progress.setValue]])
        pathSep = "/"
        if not "/" in fname:
            pathSep = "\\"
        nameParts = fname.split(pathSep)[len(fname.split(pathSep)) - 1].rsplit(".", 1)
        self.romToEdit_name = nameParts[0]
        self.romToEdit_ext = "." + nameParts[-1]
        self.setWindowTitle("Mega Man ZX Editor" + " \"" + self.romToEdit_name + self.romToEdit_ext + "\"")
        try:
            self.rom = ndspy.rom.NintendoDSRom.fromFile(fname)
            # create a file attribute table that can be read rapidly because ndspy does not provide any
            self.loadFat()
        except Exception as e:
            self.progressHide()
            print(e)
            QtWidgets.QMessageBox.critical(
            self,
            "Failed to load ROM",
            str(e)
            )
            self.setWindowTitle("Mega Man ZX Editor")
            return
        try:
            fileID = str(self.rom.filenames).rpartition(".sdat")[0].split()[-2]
            self.sdat = ndspy.soundArchive.SDAT(self.rom.files[int(fileID)])# manually search for sdat file because getFileByName does not find it when it is in a folder
            self.sdat.fileID = int(fileID)
            print("SDAT at " + fileID)
            #self.sdat.fatLengthsIncludePadding = True
            self.action_sdat.setEnabled(True)
        except Exception as e:
            print(e)
            self.window_progress.hide()
            self.sdat = None
            dialog = QtWidgets.QMessageBox(self)
            dialog.setWindowTitle("No SDAT")
            dialog.setWindowIcon(QtGui.QIcon("icons\\exclamation"))
            dialog.setText("Sound data archive was not found. \n This means that sound data may not be there or may not be in a recognizable format.")
            dialog.exec()
            self.progressShow()
        self.progressUpdate(10, "Loading ARM9")
        self.treeArm9Update()
        self.progressUpdate(20, "Loading ARM7")
        self.treeArm7Update()
        self.progressUpdate(30, "Loading SDAT")
        self.treeSdatUpdate()
        #print(self.rom.filenames)
        self.progressUpdate(50, "Loading Patches")
        self.patches_reload()
        self.progressUpdate(80, "Finishing load")
        self.temp_path = f"{os.path.curdir}\\temp\\{self.romToEdit_name+self.romToEdit_ext}"
        self.setWindowTitle("Mega Man ZX Editor" + " <" + self.rom.name.decode() + ", Serial ID " + ''.join(char for char in self.rom.idCode.decode("utf-8") if char.isalnum())  + ", Rev." + str(self.rom.version) + ", Region " + str(self.rom.region) + ">" + " \"" + self.romToEdit_name + self.romToEdit_ext + "\"")
        if not self.rom.name.decode().replace(" ", "_") in lib.patchdat.GameEnum.__members__:
            print("ROM is NOT supported! Continue at your own risk!")
            self.window_progress.hide()
            dialog = QtWidgets.QMessageBox(self)
            dialog.setWindowTitle("Warning!")
            dialog.setWindowIcon(QtGui.QIcon("icons\\exclamation"))
            dialog.setText("Game \"" + self.rom.name.decode() + "\" is NOT supported! Continue at your own risk!")
            dialog.exec()
            self.window_progress.show()

        self.treeUpdate()
        self.progressUpdate(100, "Finishing load")
        self.enable_editing_ui()
        self.file_content_text.setDisabled(True)
        self.progressHide()
        

    def enable_editing_ui(self):
        #self.button_codeedit.setDisabled(False)
        self.importSubmenu.setDisabled(False)
        self.button_file_save.show()
        self.action_save.setDisabled(False)
        self.action_arm9.setDisabled(False)
        self.action_arm7.setDisabled(False)
        self.button_playtest.setDisabled(False)
        self.dropdown_tweak_target.show()
        self.field_address.show()
        self.label_file_size.show()
        self.dropdown_level_area.blockSignals(True)
        # only levels are named like this except r01 is actually the minimap?
        self.dropdown_level_area.addItems([item.text(1) for item in self.tree.findItems("^[a-z][0-9][0-9]", QtCore.Qt.MatchFlag.MatchRegularExpression, 1)])
        for i in range(self.layout_level_area.count()):
            self.layout_level_area.itemAt(i).widget().setEnabled(True)
        for w in self.findChildren(QtWidgets.QWidget):
            w.blockSignals(False)

    def disable_editing_ui(self):
        #self.button_codeedit.setDisabled(False)
        self.importSubmenu.setDisabled(True)
        self.button_file_save.hide()
        self.action_save.setDisabled(True)
        self.action_arm9.setDisabled(True)
        self.action_arm7.setDisabled(True)
        self.button_playtest.setDisabled(True)
        self.dropdown_tweak_target.hide()
        self.field_address.hide()
        self.label_file_size.hide()
        for i in range(self.layout_level_area.count()):
            self.layout_level_area.itemAt(i).widget().setEnabled(False)
        for w in self.findChildren(QtWidgets.QWidget):
            w.blockSignals(True)
        self.gfx_scene_level.scene().clear()
        self.gfx_scene_tileset.scene().clear()
        self.dropdown_level_area.clear()
        self.dropdown_level_type.clear()

    def exportCall(self, item: QtWidgets.QTreeWidgetItem):
        dialog = QtWidgets.QFileDialog(
                self,
                "Export File",
                "",
                "Supported Export Formats (*.bin *.txt *.vx);;All Files (*)",
                options=QtWidgets.QFileDialog.Option.DontUseNativeDialog,
                )
        dialog.setAcceptMode(dialog.AcceptMode.AcceptSave)
        dialog.setFileMode(dialog.FileMode.AnyFile)
        dialog.setLabelText(QtWidgets.QFileDialog.DialogLabel.Accept, "Export")
        dialog.setLabelText(QtWidgets.QFileDialog.DialogLabel.FileName, "Output Destination:")
        if dialog.exec(): # if you saved a file
            dialog2 = QtWidgets.QMessageBox()
            dialog2.setWindowTitle("Export Status")
            dialog2.setWindowIcon(QtGui.QIcon('icons\\information.png'))
            dialog2.setText("File export failed!")
            selectedFiles = dialog.selectedFiles()
            path = selectedFiles[0][:selectedFiles[0].rfind("/")]
            name = selectedFiles[0].split("/")[-1]
            print(path, name)
            dialog_formatselect = QtWidgets.QDialog(self)
            dialog_formatselect.setWindowTitle("Choose format and compression")
            dropdown_formatselect = QtWidgets.QComboBox(dialog_formatselect)
            dropdown_formatselect.addItems(["Raw", "English dialogue", "VX"])
            dropdown_compressselect = QtWidgets.QComboBox(dialog_formatselect)
            dropdown_compressselect.addItems(["No compression change", "LZ10 compression", "LZ10 decompression"])
            button_OK = QtWidgets.QPushButton("OK", dialog_formatselect)
            button_OK.pressed.connect(lambda: dialog_formatselect.close())
            button_OK.pressed.connect(lambda: dialog_formatselect.setResult(1))
            dialog_formatselect.setLayout(QtWidgets.QGridLayout())
            dialog_formatselect.layout().addWidget(dropdown_formatselect)
            dialog_formatselect.layout().addWidget(dropdown_compressselect)
            dialog_formatselect.layout().addWidget(button_OK)
            dialog_formatselect.resize(250, 200)
            dialog_formatselect.exec()
            if dialog_formatselect.result():
                print("Selected: " + dropdown_formatselect.currentText() + ", " + dropdown_compressselect.currentText())
                print("Item: " + item.text(0))
                if item != None:
                    fileInfo = self.file_fromItem(item)
                    if fileInfo == [b'', "", None, None]:
                        print("could not fetch data from tree item")
                        dialog2.setText("no file could be exported!\nmake sure to select a file before trying to export.")
                        dialog2.exec()
                        return
                    elif not isinstance(fileInfo[0], (bytes, bytearray)): # both bytes and bytearray are essentially the same, but need to be checked for separately
                        if type(fileInfo[0]) == tuple:
                            fileData = fileInfo[0][1].save()
                        else:
                            fileData = fileInfo[0].save()
                        print(fileData)
                        if isinstance(fileData, tuple):
                            fileData = fileData[0]
                    else:
                        fileData = fileInfo[0] # fileInfo[0] is already the expected data
                    if not "Folder" in item.text(2): # if file
                        extract(fileData, name=name, path=path, format=dropdown_formatselect.currentText(), compress=dropdown_compressselect.currentIndex())
                        dialog2.setText(f"file \"{item.text(1)}\" exported!")
                    else: # if folder
                        folder_path = os.path.join(selectedFiles[0]) # here, "file name" specifies folder name instead
                        if os.path.exists(folder_path) == False:
                            print("Folder " + folder_path  + " will be created")
                            os.makedirs(folder_path)
                        else:
                            print("Folder " + folder_path  + " will be used")
                        print(item.childCount() - 1)
                        for i in range(item.childCount()):
                            print(item.child(i).text(0))
                            # file_fromItem gets the name automatically
                            extract(*self.file_fromItem(item.child(i))[:2], path=folder_path, format=dropdown_formatselect.currentText(), compress=dropdown_compressselect.currentIndex())#, w.fileToEdit_name.replace(".Folder", "/")
                            #str(w.tree.currentItem().child(i).text(1) + "." + w.tree.currentItem().child(i).text(2)), 
                        dialog2.setText(f"folder \"{item.text(1)}\" exported!")
                    dialog2.exec()

    def replacebynameCall(self):
        if hasattr(w.rom, "name"):
            dialog = QtWidgets.QFileDialog(
                self,
                "Import File",
                "",
                "All Files (*)",
                options=QtWidgets.QFileDialog.Option.DontUseNativeDialog,
                )
            dialog.setLabelText(QtWidgets.QFileDialog.DialogLabel.Accept, "Import")
            dialog.setLabelText(QtWidgets.QFileDialog.DialogLabel.FileName, "ROM file:")
            if dialog.exec():
                selectedFiles = dialog.selectedFiles()
                dialog2 = QtWidgets.QMessageBox()
                dialog2.setWindowTitle("Import Status")
                dialog2.setWindowIcon(QtGui.QIcon('icons\\information.png'))
                dialog2.setText("File \"" + str(selectedFiles[0]).split("/")[-1] + "\" imported!")
                if str(selectedFiles[0]).split("/")[-1].removesuffix("']") in str(self.rom.filenames): # if file you're trying to replace is in ROM
                    with open(*selectedFiles, 'rb') as f:
                        fileEdited = f.read()
                        w.rom.setFileByName(str(f.name).split("/")[-1], bytearray(fileEdited))
                    dialog2.exec()
                elif str(selectedFiles[0]).split("/")[-1].split(".")[0] in [filename[filename.rfind(" ")+1:filename.find(".")] for filename in str(self.rom.filenames).split("\n")]: # if filename of file(without extension) you're trying to replace is in ROM
                    with open(*selectedFiles, 'rb') as f:
                        fileEdited = f.read()
                        if str(f.name).split("/")[-1].split(".")[1] == "txt":
                            #print(w.rom.filenames.idOf(str(selectedFiles).split("/")[-1].removesuffix("']").replace(".txt", ".bin")))
                            w.rom.files[w.rom.filenames.idOf(str(f.name).split("/")[-1].replace(".txt", ".bin"))] = bytearray(lib.dialogue.DialogueFile.textToBin(fileEdited.decode("utf-8")))
                            dialog2.exec()
                        else:
                            QtWidgets.QMessageBox.critical(
                            self,
                            "Format not recognized",
                            "Please select a file that is supported by the editor."
                            )
                else:
                    QtWidgets.QMessageBox.critical(
                    self,
                    "File \"" + str(selectedFiles[0]).split("/")[-1].removesuffix("']") + "\" not found in game files",
                    "Please select a file that has the same name as an existing ROM file."
                    )
                self.treeCall()

    def switch_dialogMode(self, dialog: QtWidgets.QFileDialog):
        nameFilters = dialog.nameFilters()
        index = nameFilters.index(dialog.selectedNameFilter())
        dialog.setFileMode([QtWidgets.QFileDialog.FileMode.ExistingFiles, QtWidgets.QFileDialog.FileMode.Directory][index])
        dialog.setNameFilters([nameFilters[0], nameFilters[1]]) # setting to directory removes non-directory filters, so fix that
        dialog.selectNameFilter(dialog.nameFilters()[index]) # resetting filters resets selection, so re-select desired option

    def replaceCall(self, item: QtWidgets.QTreeWidgetItem):
        if hasattr(w.rom, "name"):
            dialog = QtWidgets.QFileDialog(
                self,
                "Import File",
                "",
                "All Files (*);;Directories",
                options=QtWidgets.QFileDialog.Option.DontUseNativeDialog,
                )
            dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles) # allow more than one file to be selected
            dialog.filterSelected.connect(lambda: self.switch_dialogMode(dialog))
            dialog.setLabelText(QtWidgets.QFileDialog.DialogLabel.Accept, "Import")
            dialog.setLabelText(QtWidgets.QFileDialog.DialogLabel.FileName, "Source:")
            if dialog.exec(): # if file you're trying to replace is in ROM
                    isFolder = dialog.selectedNameFilter() == "Directories"
                    selectedFiles = dialog.selectedFiles()
                    dialog2 = QtWidgets.QMessageBox()
                    dialog2.setWindowTitle("Import Status")
                    dialog2.setWindowIcon(QtGui.QIcon('icons\\information.png'))
                    dialog2.setText("File import failed!")
                    fileInfo = self.file_fromItem(item)
                    if not isFolder and str(selectedFiles[0]).split("/")[-1].split(".")[1] == "txt" and re.search(r".*(_\d+)$", str(selectedFiles[0]).split("/")[-1].split(".")[0]): # fileExt and fileName
                        dialogue = lib.dialogue.DialogueFile(fileInfo[2][fileInfo[2].index(fileInfo[0])]) # object created before loop to improve performance
                    for file in selectedFiles:
                        try:
                            fileName = str(file).split("/")[-1].split(".")[0]
                            fileExt = str(file).split("/")[-1].split(".")[1]
                        except IndexError:
                            fileName = ""
                            fileExt = ""
                        if not isFolder:
                            with open(file, 'rb') as f:
                                fileEdited = f.read()
                                #print(fileExt)
                                # find a way to get attr and replace data at correct index.. maybe it's better to just save ROM and patch
                                #self.rom.files[self.rom.files.index(self.file_fromItem(item)[0])]
                                supported_list = ["txt", "swar", "sbnk", "ssar", "sseq", "cmp", "dec", "bin", ""]
                                #print(selectedFiles)
                                print(f.name)
                                #print(fileName + "." + fileExt)
                                if not any(supported == fileExt.lower() for supported in supported_list): # unknown
                                    dialog2.exec()
                                    return
                                elif not isinstance(fileInfo[2], type(None)):
                                    if fileExt == "txt": # english text file
                                        if "en" in fileName:
                                            if re.search(r".*(_\d+)$", fileName) and dialogue: # match the indicator that the file is a chunk of the original file
                                                dialogue.text_list[int(fileName.split("_")[-1])] = fileEdited.decode("utf-8") # add file text to object
                                                if selectedFiles.index(file) == len(selectedFiles)-1: # if at last selected file
                                                    data = dialogue.toBytes() # generate final binary to import (done only once to improve performance)
                                            else:
                                                data = bytearray(lib.dialogue.DialogueFile.textToBin(fileEdited.decode("utf-8")))
                                        else:
                                            pass # jp
                                    elif fileExt == "cmp":
                                        try:
                                            data = bytearray(ndspy.lz10.decompress(fileEdited))
                                        except TypeError as e:
                                            print(e)
                                            QtWidgets.QMessageBox.critical(
                                            self,
                                            "Decompression Failed",
                                            str(e + "\nConsider trying again without the .cmp file extension.")
                                            )
                                            print("Aborted file replacement.")
                                            return
                                    elif fileExt == "dec":
                                        data = bytearray(ndspy.lz10.compress(fileEdited))
                                    else: # raw data
                                        data = bytearray(fileEdited)
                                else:
                                    dialog2.exec()
                                    return
                        else:
                            print("folder import")
                            if fileExt == "vx":
                                print("is vx")
                                self.progressShow()
                                self.progressUpdate(0, "Loading folder")
                                act = lib.act.ActImagine()
                                try:
                                    import_vxfolder_iter = act.import_vxfolder(file)
                                except:
                                    print("This folder is not formatted properly!")
                                    return
                                self.progressUpdate(0, "Preparing encoding")
                                for i, _ in enumerate(import_vxfolder_iter):
                                    self.progressUpdate(50, f"Preparing encoding (processing frame {i+1}/???)")
                                self.progressUpdate(100, "Preparing encoding")
                                vframe_strategy = lib.actEncStrats.KeyframeOnlySimple()
                                for i, avframe in enumerate(act.avframes):
                                    avframe.encode(avframe.vframe.plane_buffers, vframe_strategy)
                                    self.progressUpdate(int(((i+1)/act.frames_qty)*100), "Encoding VX folder")
                                data = act.save_vx()
                                self.progressHide()
                            else:
                                print("not a special folder")
                                return

                    if isinstance(fileInfo[2], bytearray): # other
                            fileInfo[2][fileInfo[2].index(fileInfo[0]):fileInfo[2].index(fileInfo[0])+len(fileInfo[0])] = data
                            print(data[:0x15].hex())
                    elif fileInfo[3] == None: # rom files
                        fileInfo[2][fileInfo[2].index(fileInfo[0])] = data
                        print(data[:0x15].hex())
                    elif any(x for x in self.sdat.__dict__.values() if x == fileInfo[3]):
                        newName = fileName
                        if type(fileInfo[0]) == tuple: # object listed within object in one of the sdat sections
                            oldObject = fileInfo[0][1]
                        else:
                            oldObject = fileInfo[0]
                        try:
                            newObject = type(oldObject).fromFile(f.name)
                        except:
                            dialog2.exec()
                            return
                        if isinstance(oldObject, ndspy.soundSequenceArchive.soundSequence.SSEQ): # bankID fix (defaults to 0)
                            newObject.bankID = oldObject.bankID
                            newObject.volume = oldObject.volume
                            newObject.channelPressure = oldObject.channelPressure
                            newObject.polyphonicPressure = oldObject.polyphonicPressure
                            newObject.playerID = oldObject.playerID
                            #for sseq in fileInfo[3]:
                            #    if sseq[0] == fileName:
                            #        newObject.bankID = sseq[1].bankID
                            #        newName = fileInfo[0][0]
                        print(oldObject)
                        print(newObject)
                        if type(fileInfo[0]) == tuple:
                            fileInfo[3][fileInfo[3].index(fileInfo[0])] = (newName, newObject) 
                        else: # sub-object
                            if hasattr(fileInfo[3], "waves"):
                                fileInfo[3].waves[fileInfo[3].waves.index(fileInfo[0])] = (newObject) 
                            elif hasattr(fileInfo[3], "sequences"):
                                fileInfo[3].sequences[fileInfo[3].sequences.index(fileInfo[0])] = (newObject) 
                            else:
                                print("unhandled case")
                        fileInfo[2][self.sdat.fileID] = self.sdat.save() # save sdat to its parent object
                        self.treeSdatUpdate() # refresh tree to avoid interactions with files that are not in the new state
                    else: # subfile
                        for file in fileInfo[2]:
                            if fileInfo[0] in file:
                                fileInfo[2][fileInfo[2].index(file)][file.index(fileInfo[0]):file.index(fileInfo[0])+len(fileInfo[0])] = data
                            
                    dialog2.setText("File \"" + str(selectedFiles[0]).split("/")[-1] + "\" imported!")
                    dialog2.exec()
                    self.treeCall()
    
    def switch_theme(self, isupdate=False):
        if isupdate == False:
            self.theme_index = self.dropdown_theme.currentIndex()
            lib.ini_rw.write(self)
        else:
            self.dropdown_theme.setCurrentIndex(self.theme_index) # Update dropdown with current option

        app: QtWidgets.QMainWindow = QtCore.QCoreApplication.instance()
        #print(app.style().metaObject().className())
        app.setStyle(QtWidgets.QCommonStyle())
        app.setStyleSheet("")
        if self.theme_index < len(QtWidgets.QStyleFactory.keys()):
            app.setStyle(self.dropdown_theme.itemText(self.theme_index))
        else:
            if os.path.exists('theme\\custom_theme.qss'):
                app.setStyleSheet(open('theme\\custom_theme.qss').read())
            else:
                os.mkdir("theme")
                open('theme\\custom_theme.qss', "w")
                dialog = QtWidgets.QMessageBox()
                dialog.setWindowTitle("No custom stylesheet found")
                dialog.setWindowIcon(QtGui.QIcon("icons\\exclamation"))
                dialog.setText("No custom stylesheet was found in location \"theme\\custom_theme.qss\".\nAn empty file has been created there.\nPlease put the contents of your custom stylesheet in it.\nIf you wish to create one yourself but do not know how, refer to this page:\nhttps://doc.qt.io/qtforpython-6.5/overviews/stylesheet-examples.html")
                dialog.exec()
    
    def display_format_toggleCall(self):
        self.fileDisplayRaw = not self.fileDisplayRaw
        self.displayFormatSubmenu.setDisabled(self.displayFormatSubmenu.isEnabled())
        self.widgetIcon_update(self.displayRawAction, QtGui.QIcon('icons\\brain.png'), QtGui.QIcon('icons\\document-binary.png'))
        self.treeCall()

    def value_update_Call(self, var, val, istreecall=True):
        #print(f"{self.field_address.value():08X}" + " - " + f"{self.base_address:08X}")
        setattr(self, var, val)
        if istreecall:
            self.treeCall()

    def OAM_updateItemGFX(self, obj_index: int, item: lib.widget.OAMObjectItem | None=None): # creates and returns an item if none specified
        index_img = self.fileEdited_object.frame[2]
        gfxsec: lib.graphic.GraphicSection = self.fileEdited_object.gfxsec
        if len(gfxsec.graphics) <= 0:
            print("no graphics in section!")
            return
        depth = 4 # actual depth that will be used to render
        indexingFactor = 1 # I guess this is changed based on the size of assembled gfx
        # in 4bpp, oam tile id * indexingFactor = vram tile id
        # in 8bpp, oam tile id * indexingFactor // 2 = vram tile id
        if gfxsec.entry_size == 0x14:
            depth = gfxsec.graphics[0].depth//2
        obj: lib.oam.Object = self.fileEdited_object.objs[obj_index]
        if item != None:
            obj.tileId = self.field_objTileId.value()
            obj.tileId_add = self.field_objTileId.value() & 0x300
            obj.flip_h = self.checkbox_objFlipH.isChecked()
            obj.flip_v = self.checkbox_objFlipV.isChecked()
            obj.sizeIndex = self.slider_objSizeIndex.sl.value()
            obj.shape = self.buttonGroup_oam_objShape.checkedId()
            obj.x = self.field_objX.value()
            obj.y = self.field_objY.value()
        if index_img >= len(gfxsec.graphics):
            print(f"Graphic Section index {index_img} does not exist!")
            return
        if gfxsec.graphics[index_img].oam_tile_indexing == 0:
            indexingFactor = 1
        elif gfxsec.graphics[index_img].oam_tile_indexing == 0x18:
            indexingFactor = 4
        else:
            print(f"unhandled tile indexing mode: {gfxsec.graphics[index_img].oam_tile_indexing:02X}")
        if gfxsec.entry_size == 0x14:
            pal_off = gfxsec.graphics[index_img].offset_start + gfxsec.graphics[index_img].palette_offset+0xc
            pal = [0xffffffff]*(gfxsec.graphics[index_img].unk13 & 0xf0)
            pal.extend(lib.datconv.BGR15_to_ARGB32(self.fileEdited_object.auxfile.data[pal_off:pal_off+gfxsec.graphics[index_img].palette_size]))
        else:
            #print(int.from_bytes(self.fileEdited_object.oamsec.data[self.fileEdited_object.oamsec.paletteTable_offset:self.fileEdited_object.oamsec.paletteTable_offset+2]))
            pal = self.GFX_PALETTES[2]#self.fileEdited_object.oamsec.paletteTable[0] # placeholder
        tileId = gfxsec.graphics[index_img].oam_tile_offset + obj.tileId
        gfxOffset = gfxsec.graphics[index_img].offset_start + gfxsec.graphics[index_img].gfx_offset
        # multiply oam tile id by indexingFactor(relative to 4bpp) and 4bpp tile size to get vram tile id
        gfxOffset += int(tileId*indexingFactor*32) # 8*8pixels*4bpp/8bits = 32bytes
        #print(f"offset: {gfxOffset:04X}")
        #print(f"tile {tileId:02X}")
        depth_obj = lib.datconv.CompressionAlgorithmEnum.FOURBPP
        for member in lib.datconv.CompressionAlgorithmEnum:
            if member.depth == depth:
                depth_obj = member
        try: #gfxOffset+gfxsec.graphics[index_img].gfx_size
            obj_img = lib.datconv.binToQt(self.fileEdited_object.auxfile.data[gfxOffset:], pal,
                                                depth_obj,
                                                obj.getWidth(),
                                                obj.getHeight())
        except AssertionError:
            print("invalid object properties detected!")
            print(f"shape: {obj.shape}  size: {obj.sizeIndex}")
            return
        colorTable = obj_img.colorTable()
        if len(colorTable) <= 0:
            print("empty palette!")
            return
        colorTable[0] -= 0xff000000 # remove alpha from first color
        obj_img.setColorTable(colorTable)
        if item == None:
            obj_item = lib.widget.OAMObjectItem(QtGui.QPixmap.fromImage(obj_img), id=obj_index, editable=(self.tabs_oam.currentWidget()==self.page_oam_frames))
        else:
            obj_item = item
            obj_item.setPixmap(QtGui.QPixmap.fromImage(obj_img))
        obj_item.setPixmap(
            obj_item.pixmap().transformed(QtGui.QTransform().scale(-1 if obj.flip_h else 1,-1 if obj.flip_v else 1)))
        obj_item.setPos(obj.x, obj.y)
        obj_item.setZValue(-obj_item.obj_id)
        if item == None:
            return obj_item
        
    def OAM_playAnimFrame(self):
        if self.fileDisplayState != "OAM": # prevents crash when loading another file
            self.button_oam_animPlay.autoPause()
            return
        anim: lib.oam.Animation = self.fileEdited_object.oamsec_anim
        frame_index = self.dropdown_oam_animFrame.currentIndex()
        frame = anim.frames[frame_index]
        duration = frame[1]
        if frame_index > 0 and duration == 0:
            duration = 0xFF
        if self.button_oam_animPlay.counter >= duration:
            #print(f"{self.button_oam_animPlay.counter} vs {duration}")
            self.button_oam_animPlay.counter = 0
            if frame_index < self.dropdown_oam_animFrame.count()-1:
                self.dropdown_oam_animFrame.setCurrentIndex(frame_index+1)
            else:
                if self.checkbox_oam_animLoop.isChecked():
                    self.dropdown_oam_animFrame.setCurrentIndex(self.field_oam_animLoopStart.value())
                else: # pause anim
                    self.button_oam_animPlay.autoPause()

    def setPalette(self, palette: list[int]):
        #for i in range(self.dropdown_gfx_depth.count()): # re-enable depth options
        #    self.dropdown_gfx_depth.model().item(i).setEnabled(True)
        new_pal = palette.copy()
        if new_pal == []:
            print("empty palette!")
            if not self.gfx_palette in self.GFX_PALETTES:
                self.setPalette(self.GFX_PALETTES[0])
            return
        try:
            self.dropdown_gfx_palette.setCurrentIndex(self.GFX_PALETTES.index(palette)) # if setPalette wasn't called by the dropdown itself
        except ValueError:
            self.dropdown_gfx_palette.setCurrentIndex(-1) # dynamically generated palette
        self.gfx_palette = new_pal
        self.file_content_gfx.pen.setColor(0x00010101) # set to first color
        for i in range(256):
            button_palettepick: lib.widget.HoldButton = getattr(self, f"button_palettepick_{i}")
            if i < len(self.gfx_palette):
                button_palettepick.setStyleSheet(f"background-color: #{self.gfx_palette[i]:08x}; color: white;")
            else:
                button_palettepick.setStyleSheet(f"background-color: white; color: white;") # fill missing colors with white

    def colorpickCall(self, color_index: int, press=None, hold=None):
        #print(color_index)
        button: lib.widget.HoldButton = getattr(self, f"button_palettepick_{color_index}")
        depth = list(lib.datconv.CompressionAlgorithmEnum)[self.dropdown_gfx_depth.currentIndex()].depth
        if hold:
            dialog = QtWidgets.QColorDialog(self)
            dialog.setOptions(QtWidgets.QColorDialog.ColorDialogOption.DontUseNativeDialog)
            dialog.setCurrentColor(int(button.styleSheet()[button.styleSheet().find(":")+3:button.styleSheet().find(";")], 16))
            dialog.exec()
            if dialog.selectedColor().isValid():
                button.setStyleSheet(f"background-color: {dialog.selectedColor().name()}; color: white;")
                self.gfx_palette[color_index] = dialog.selectedColor().rgba()
                if self.dropdown_gfx_palette.currentIndex() == -1:
                    self.button_file_save.setEnabled(True)
                self.treeCall() # update gfx colors
        if press:
            #print(button.styleSheet())
            if color_index < 2**depth:
                self.file_content_gfx.pen.setColor(0xff000000 + color_index * 0x00010101)#int(button.styleSheet()[button.styleSheet().find(":")+3:button.styleSheet().find(";")], 16))
            elif color_index < len(self.gfx_palette): # outside of first subpalette range, but is an existing color in palette
                color_index2 = color_index//(2**depth)*(2**depth)
                new_pal = self.gfx_palette.copy() # copy to another var to facilitate color swap
                new_pal[:2**depth] = self.gfx_palette[color_index2:color_index2+(2**depth)] # switch up colors between selected subpalette and 1st subpalette
                new_pal[color_index2:color_index2+(2**depth)] = self.gfx_palette[:2**depth]
                self.gfx_palette = new_pal
                self.file_content_gfx.pen.setColor(0xff000000 + color_index%(2**depth) * 0x00010101) # set to first color
                for i in range(2**depth): # change affected buttons (primary)
                    button_palettepick: lib.widget.HoldButton = getattr(self, f"button_palettepick_{i}")
                    button_palettepick.setStyleSheet(f"background-color: #{self.gfx_palette[i]:08x}; color: white;")
                for i in range(color_index2, color_index2+2**depth): # change affected buttons (selected)
                    button_palettepick: lib.widget.HoldButton = getattr(self, f"button_palettepick_{i}")
                    button_palettepick.setStyleSheet(f"background-color: #{self.gfx_palette[i]:08x}; color: white;")
                self.treeCall()
                    
    
    def saveCall(self): #Save to external ROM
        dialog = QtWidgets.QFileDialog(
                self,
                "Save ROM",
                "",
                "NDS Files (*.nds *.srl);; All Files (*)",
                options=QtWidgets.QFileDialog.Option.DontUseNativeDialog,
                )
        dialog.setAcceptMode(dialog.AcceptMode.AcceptSave)
        dialog.setDefaultSuffix(self.romToEdit_ext)
        dialog.setLabelText(QtWidgets.QFileDialog.DialogLabel.Accept, "Save")
        dialog.setLabelText(QtWidgets.QFileDialog.DialogLabel.FileName, "Hack name:")
        if dialog.exec(): # if you saved a file
            romName = dialog.selectedFiles()[0]
            print(romName)
            self.rom.saveToFile(romName)
            print("ROM modifs saved!")
            # allow user to choose whether or not they want to reload fat
            reload_dialog = QtWidgets.QMessageBox()
            reload_dialog.setWindowTitle("Mega Man ZX Editor - Reload from saved ROM")
            reload_dialog.setWindowIcon(QtGui.QIcon('icons\\question.png'))
            reload_dialog.setText("Now that the ROM is saved, the FAT may have changed.\n Reload ROM from this file to fetch accurate file addresses?")
            reload_dialog.setStandardButtons(reload_dialog.StandardButton.Yes | reload_dialog.StandardButton.No)
            if reload_dialog.exec() == reload_dialog.StandardButton.Yes:
                self.loadROM(romName)

    def testCall(self, isQuick=True):
        #print("isQuick: " + str(isQuick))
        if isQuick == False:
            dialog_playtest = QtWidgets.QDialog(self)
            dialog_playtest.setWindowTitle("Playtest Options")
            dialog_playtest.resize(500, 500)
            dialog_playtest.setLayout(QtWidgets.QGridLayout())
            # Test options; arm 9 at 0x00004000; starting pos x=00A00D00 y=FF6F0400
            input_address = QtWidgets.QLineEdit(dialog_playtest)
            input_address.setPlaceholderText("insert test patch adress")
            input_value = QtWidgets.QLineEdit(dialog_playtest)
            input_value.setPlaceholderText("insert test patch data")

            button_play = QtWidgets.QPushButton("Play", dialog_playtest)
            button_play.move(dialog_playtest.width() - 100, dialog_playtest.height() - 50)
            button_play.pressed.connect(lambda: dialog_playtest.close())
            button_play.pressed.connect(lambda: dialog_playtest.setResult(1))
            dialog_playtest.layout().addWidget(input_address)
            dialog_playtest.layout().addWidget(input_value)
            dialog_playtest.layout().addWidget(button_play)
            dialog_playtest.exec()
        if not os.path.exists("temp"):
                os.mkdir("temp")
        self.rom.saveToFile(self.temp_path)# Create temporary ROM to playtest
        if 'dialog_playtest' in locals() and dialog_playtest.result():
            with open(self.temp_path, "r+b") as f:
                    if input_address.text() != "":
                        try:
                            address = lib.datconv.strToNum(input_address.text(), self.displayBase)
                            value = lib.datconv.strSetAlnum(input_value.text(), 16, True)
                            f.seek(address)# get to pos for message
                            value_og = lib.datconv.strSetAlnum(f.read(len(bytes.fromhex(value))).hex(), self.displayBase, self.displayAlphanumeric)
                            print(f"successfully wrote {value_og} => {input_value.text().upper()} to {input_address.text().zfill(8)}")
                            f.seek(address)# get to pos
                            f.write(bytes.fromhex(value))# write data
                        except ValueError as e:
                            QtWidgets.QMessageBox.critical(
                                self,
                                str(e),
                                f"Address input must be numeric and must not go over size {lib.datconv.numToStr(len(self.rom.save()), self.displayBase, self.displayAlphanumeric)}\nValue input must be numeric."
                                )
                            return
        if isQuick or dialog_playtest.result():
            os.startfile(self.temp_path)
            print("game will start in a few seconds")

    def arm9OpenCall(self):
        if hasattr(self, 'dialog_arm9'):
            self.dialog_arm9.show()
            self.dialog_arm9.setWindowState(QtCore.Qt.WindowState.WindowActive) # un-minimize window

    def arm7OpenCall(self):
        if hasattr(self, 'dialog_arm7'):
            self.dialog_arm7.show()
            self.dialog_arm7.setWindowState(QtCore.Qt.WindowState.WindowActive)

    def sdatOpenCall(self):
        if hasattr(self, 'dialog_sdat'):
            self.dialog_sdat.show()
            self.dialog_sdat.setWindowState(QtCore.Qt.WindowState.WindowActive)

    def sdatPlayCall(self):
        items = self.tree_sdat.selectedItems()
        if len(items) == 0: return
        if items[0].text(0) == "N/A": return
        snd_type = items[0].text(2)
        if snd_type == "SWAV": # WIP, need to use QAudioFormat probably
            self.mediaPlayer.stop()
            print("play SWAV")
            snd_data: ndspy.soundArchive.soundWaveArchive.soundWave.SWAV = self.file_fromItem(items[0])[0]
            self.mediaPlayer.setSourceDevice(None) # to prevent buffer corruption
            self.audioBuffer.close()
            self.audioBuffer.setData(lib.sdat.loadSWAV(snd_data))
            self.audioBuffer.open(QtCore.QBuffer.OpenModeFlag.ReadOnly)
            self.mediaPlayer.setSourceDevice(self.audioBuffer)
            self.mediaPlayer.play()
        elif snd_type == "SSEQ":
            print("play SSEQ")
            sseq: ndspy.soundArchive.soundSequence.SSEQ = self.file_fromItem(items[0])[0][1]
            lib.sdat.play(self.audioBuffer, sseq, self.sdat)


    #def codeeditCall(self):
        #self.tree.clearSelection()
        #self.arm9 = ndspy.code.MainCodeFile(w.rom.files[0], 0x00000000)
        #self.file_content_text.setPlainText(str(self.arm9))
        #print("code")

    def treeUpdate(self): # files from filename table (fnt.bin)
        tree_files: list[QtWidgets.QTreeWidgetItem] = []
        try: # convert NDS Py filenames to QTreeWidgetItems
            if self.rom.files != []:
                tree_folder: list[QtWidgets.QTreeWidgetItem] = []
                for f in str(self.rom.filenames).split("\n"):
                    if not "/" in f: # if file
                        if "    " in f: # if contents of folder
                            tree_folder[f.count("    ") - 1].addChild(QtWidgets.QTreeWidgetItem([f.split(" ")[0], f.split(" ")[-1].split(".")[0], f.split(".")[-1]]))
                        else:
                            tree_files.append(QtWidgets.QTreeWidgetItem([f.split(" ")[0], f.split(" ")[-1].split(".")[0], f.split(".")[-1]]))
                    else: # if folder
                        if f.count("    ") < len(tree_folder):
                            tree_folder[f.count("    ")] = QtWidgets.QTreeWidgetItem([f.split(" ")[0], f.split(" ")[-1].removesuffix("/"), "Folder"])
                        else:
                            tree_folder.append(QtWidgets.QTreeWidgetItem([f.split(" ")[0], f.split(" ")[-1].removesuffix("/"), "Folder"]))
                        if not "    " in f:
                            tree_files.append(tree_folder[f.count("    ")])
                        else:
                            tree_folder[f.count("    ") - 1].addChild(tree_folder[f.count("    ")])
        except Exception: # if failed, do nothing
            pass
        self.tree.clear()
        self.tree.addTopLevelItems(tree_files)

    def treeArm9Update(self):
        self.tree_arm9.clear()
        #print(self.rom.loadArm9Overlays())
        #item_mainCode = QtWidgets.QTreeWidgetItem([library.dataconverter.StrFromNumber(self.arm9.ramAddress, self.displayBase, self.displayAlphanumeric).zfill(8), "Main Code", "N/A"])

        for e in self.rom.loadArm9().sections:
            self.tree_arm9.addTopLevelItem(QtWidgets.QTreeWidgetItem([
                lib.datconv.strSetAlnum(str(e).split()[2].removeprefix("0x").removesuffix(":"), self.displayBase, self.displayAlphanumeric).zfill(8), 
                str(e).split()[0].removeprefix("<"), 
                str(e.implicit)
            ]))
        
        self.tree_arm9Ovltable.clear()
        arm9OvlDict = self.rom.loadArm9Overlays()
        for overlayID in arm9OvlDict:
                overlay = arm9OvlDict[overlayID]
                self.tree_arm9Ovltable.addTopLevelItem(QtWidgets.QTreeWidgetItem([
                    str(overlay.fileID).zfill(4), 
                    lib.datconv.numToStr(overlay.ramAddress, self.displayBase, self.displayAlphanumeric).zfill(8), 
                    str(overlay.compressed), 
                    lib.datconv.numToStr(overlay.compressedSize, self.displayBase, self.displayAlphanumeric), 
                    lib.datconv.numToStr(overlay.ramSize, self.displayBase, self.displayAlphanumeric), 
                    lib.datconv.numToStr(overlay.bssSize, self.displayBase, self.displayAlphanumeric), 
                    lib.datconv.numToStr(overlay.staticInitStart, self.displayBase, self.displayAlphanumeric).zfill(8), 
                    lib.datconv.numToStr(overlay.staticInitEnd, self.displayBase, self.displayAlphanumeric).zfill(8), 
                    lib.datconv.numToStr(overlay.flags, self.displayBase, self.displayAlphanumeric), 
                    str(overlay.verifyHash)
                ]))

        #self.tree_arm9.addTopLevelItem(item_mainCode)

    def treeArm7Update(self):
        self.tree_arm7.clear()
        #item_mainCode = QtWidgets.QTreeWidgetItem([library.dataconverter.StrFromNumber(self.arm7.ramAddress, self.displayBase, self.displayAlphanumeric).zfill(8), "Main Code", "N/A"])

        for e in self.rom.loadArm7().sections:
            self.tree_arm7.addTopLevelItem(QtWidgets.QTreeWidgetItem([
                lib.datconv.strSetAlnum(str(e).split()[2].removeprefix("0x").removesuffix(":"), self.displayBase, self.displayAlphanumeric).zfill(8), 
                str(e).split()[0].removeprefix("<"), 
                str(e.implicit)
            ]))

        self.tree_arm7Ovltable.clear()
        arm7OvlDict = self.rom.loadArm7Overlays()
        for overlayID in arm7OvlDict:
                overlay = arm7OvlDict[overlayID]
                self.tree_arm7Ovltable.addTopLevelItem(QtWidgets.QTreeWidgetItem([
                    str(overlay.fileID).zfill(4), 
                    lib.datconv.numToStr(overlay.ramAddress, self.displayBase, self.displayAlphanumeric).zfill(8), 
                    str(overlay.compressed), 
                    lib.datconv.numToStr(overlay.compressedSize, self.displayBase, self.displayAlphanumeric), 
                    lib.datconv.numToStr(overlay.ramSize, self.displayBase, self.displayAlphanumeric), 
                    lib.datconv.numToStr(overlay.bssSize, self.displayBase, self.displayAlphanumeric), 
                    lib.datconv.numToStr(overlay.staticInitStart, self.displayBase, self.displayAlphanumeric).zfill(8), 
                    lib.datconv.numToStr(overlay.staticInitEnd, self.displayBase, self.displayAlphanumeric).zfill(8), 
                    lib.datconv.numToStr(overlay.flags, self.displayBase, self.displayAlphanumeric), 
                    str(overlay.verifyHash)
                ]))
    
    def treeSdatUpdate(self):
        #print(str(self.sdat.groups)[:13000])
        #progress = QtWidgets.QProgressBar()
        #progress.setValue(0)
        #progress.show()
        self.tree_sdat.clear() 
        if self.sdat != None:
            # all sdat sections follow the [(Name, object(data)), ...] format except swar with [(Name, object([object(data), ...])), ...] and groups, which have [(Name, [object(data), ...]), ...]
            item_sseq = QtWidgets.QTreeWidgetItem(["N/A", "Sequenced Music", "SSEQ"]) #SSEQ
            item_ssar = QtWidgets.QTreeWidgetItem(["N/A", "Sequenced Sound Effects", "SSAR"]) #SSAR
            item_sbnk = QtWidgets.QTreeWidgetItem(["N/A", "Sound Banks", "SBNK"]) #SBNK
            item_swar = QtWidgets.QTreeWidgetItem(["N/A", "Sound Waves", "SWAR"]) #SWAR
            item_sseqplayer = QtWidgets.QTreeWidgetItem(["N/A", "Sequence Player", ""]) #plays SSEQ or SSAR
            item_strm = QtWidgets.QTreeWidgetItem(["N/A", "Multi-Channel Stream", "STRM"]) #STRM
            item_strmplayer = QtWidgets.QTreeWidgetItem(["N/A", "Stream Player", ""]) #plays STRM
            item_group = QtWidgets.QTreeWidgetItem(["N/A", "Group", ""])
            item_list = [
                item_sseq,
                item_ssar,
                item_sbnk,
                item_swar,
                item_sseqplayer,
                item_strm,
                item_strmplayer,
                item_group
            ]
            data_list = [
                self.sdat.sequences,
                self.sdat.sequenceArchives,
                self.sdat.banks,
                self.sdat.waveArchives,
                self.sdat.sequencePlayers,
                self.sdat.streams,
                self.sdat.streamPlayers,
                self.sdat.groups
            ]
            for category in item_list:
                for section in data_list[item_list.index(category)]:
                    child = QtWidgets.QTreeWidgetItem([str(data_list[item_list.index(category)].index(section)), section[0], category.text(2)])
                    if hasattr(section[1], "bankID"):
                        child.setToolTip(0, "bankID: " + str(section[1].bankID))
                    category.addChild(child)
                    if hasattr(section[1], "sequences"):
                        for sseq_i, sseq in enumerate(section[1].sequences): # actually a list with [name, SSARSequence]
                            subChild = QtWidgets.QTreeWidgetItem([str(sseq_i), sseq[0], "SSEQ"])
                            child.addChild(subChild)
                    if hasattr(section[1], "waves"):
                        for wave_i, wave in enumerate(section[1].waves):
                            subChild = QtWidgets.QTreeWidgetItem([str(wave_i), f"{child.text(1)} (Wave {wave_i})", "SWAV"])
                            child.addChild(subChild)
                #progress.setValue(progress.value()+ 100//len(item_list))

            self.tree_sdat.addTopLevelItems([*item_list])
            #progress.setValue(100)
            #progress.close()

    def treeCall(self, addr_reset=False, addr_disabled=False):
        #print("Tree")
        #self.clearTasks()
        sender = self.sender()
        #print(self.sender())
        if sender in self.FILEOPEN_WIDGETS:
            self.fileEdited_object = None # change this into a generic file object
        self.file_content_text.setReadOnly(False)
        self.field_address.setDisabled(addr_disabled)
        QtCore.qInstallMessageHandler(lambda a, b, c: None) # Silence Invalid base warnings from the following code
        for widget in self.findChildren(lib.widget.BetterSpinBox): # update all widgets of same type with current settings
            widget.alphanum = self.displayAlphanumeric
            widget.numbase = self.displayBase
            widget.repaint()
        QtCore.qInstallMessageHandler(None) # Revert to default message handler
        if self.dialog_settings.isVisible() and (self.field_address.numbase != self.displayBase): # handle error manually
            QtWidgets.QMessageBox.critical(
                                self,
                                "Numeric Base Warning!",
                                f"Base is not supported for inputting data in spinboxes.\n This means that all spinboxes will revert to base 10 until they are set to a supported base.\n Proceed at your own risk!"
                                )
        for widget in self.findChildren(QtWidgets.QWidget):
            if not isinstance(widget, QtWidgets.QButtonGroup):
                widget.blockSignals(True) # prevent treeCall from being executed twice in a row. Reduces lag
        self.treeSubCall(addr_reset)
        if sender in self.FILEOPEN_WIDGETS:
            self.file_editor_show(self.widget_set)
            self.button_file_save.setDisabled(True)
        for widget in self.findChildren(QtWidgets.QWidget):
            widget.blockSignals(False) # prevent treeCall from being executed twice in a row. Reduces lag

    def treeSubCall(self, addr_reset):
        sender = self.sender()
        current_item = self.tree.currentItem()
        if current_item != None:
            current_id = int(current_item.text(0))
            current_name = current_item.text(1)
            current_ext  = current_item.text(2)
            if addr_reset:
                self.relative_address = 0
            if sender in self.FILEOPEN_WIDGETS:
                self.fileToEdit_name = str(current_name + "." + current_ext)
                #self.base_address = self.rom.save().index(self.rom.files[current_id]) # find address based on file content. not entirely accurate.
                self.base_address = self.rom_fat[current_id] # load address from a list that already contains the required info to improve performance
                # set text to current ROM address
                #print(self.relative_address)
                self.field_address.setRange(self.base_address, self.base_address+len(self.rom.files[current_id]))
            self.field_address.setValue(self.base_address+self.relative_address)
            if not ".Folder" in self.fileToEdit_name:# if it's a file
                self.label_file_size.setText(f"Size: {lib.datconv.numToStr(len(self.rom.files[current_id]), self.displayBase, self.displayAlphanumeric).zfill(0)} bytes")
                if self.fileDisplayRaw == False:
                    if self.fileDisplayMode == "Adapt":
                            indicator_list_gfx = ["face", "obj_fnt", "title"]
                            if self.rom.name.decode() == "MEGAMANZX" or self.rom.name.decode() == "ROCKMANZX":
                                indicator_list_gfx.extend(["bbom", "dm23", "elf", "g_", "game_parm", "lmlevel", "miss", "repair", "sec_disk", "sub"])
                            elif self.rom.name.decode() == "MEGAMANZXA" or self.rom.name.decode() == "ROCKMANZXA":
                                indicator_list_gfx.extend(["cmm_frame_fnt", "cmm_mega_s", "cmm_rock_s", "ls_", "sub_db", "sub_oth"])
                            
                            self.fileDisplayState = "None"
                            if current_ext == "vx":
                                self.fileDisplayState = "VX"
                            elif current_ext == "sdat":
                                self.fileDisplayState = "Sound"
                            elif current_ext == "bin":
                                if "font" in current_name:
                                    self.fileDisplayState = "Font"
                                elif ("talk" in current_name or "m_" in current_name):
                                    if "en" in current_name:
                                        self.fileDisplayState = "English dialogue"
                                    elif "jp" in current_name:
                                        self.fileDisplayState = "Japanese dialogue"
                                elif any(indicator in current_name for indicator in indicator_list_gfx):
                                    self.fileDisplayState = "Graphics"
                                elif any(indicator.replace("fnt", "dat") in current_name for indicator in indicator_list_gfx):
                                    self.fileDisplayState = "OAM"
                                elif "panm" in current_name:
                                    self.fileDisplayState = "Palette Animation"
                                
                    else:
                        self.fileDisplayState = self.fileDisplayMode

                    if self.fileDisplayState == "English dialogue":
                        self.widget_set = "Text"
                        if sender in self.FILEOPEN_WIDGETS:
                            self.dropdown_textindex.setEnabled(True)
                            self.dropdown_textindex.clear()
                            try:
                                self.fileEdited_object = lib.dialogue.DialogueFile(self.rom.files[current_id])
                            except AssertionError: # forcing text view on non-text file = simple conversion mode
                                self.file_content_text.setEnabled(True)
                                self.dropdown_textindex.setDisabled(True)
                                self.fileEdited_object = lib.dialogue.DialogueFile.binToText(self.rom.files[current_id][self.relative_address:self.relative_address+0xFFFF])
                                self.file_content_text.setPlainText(self.fileEdited_object)
                                return
                            for i in range(len(self.fileEdited_object.text_list)):
                                self.dropdown_textindex.addItem(f"message {i}")
                            self.dropdown_textindex.previousIndex = self.dropdown_textindex.currentIndex()
                        elif self.dropdown_textindex.isEnabled(): # when text index changed
                            #print(f"index = {self.dropdown_textindex.currentIndex()} prev = {self.dropdown_textindex.previousIndex}")
                            if self.button_file_save.isEnabled(): # if content was modified
                                self.fileEdited_object.text_list[self.dropdown_textindex.previousIndex] = self.file_content_text.toPlainText() # keep changes to text on previous index
                                self.dropdown_textindex.previousIndex = self.dropdown_textindex.currentIndex()
                        else: # simple conversion mode during address change
                            self.fileEdited_object = lib.dialogue.DialogueFile.binToText(self.rom.files[current_id][self.relative_address:self.relative_address+0xFFFF])
                            self.file_content_text.setPlainText(self.fileEdited_object)
                            return
                        textIndex = self.dropdown_textindex.currentIndex()

                        if self.fileEdited_object.text_list != []:
                            self.relative_address = self.fileEdited_object.textAddress_list[textIndex]
                            self.field_address.setValue(self.base_address+self.relative_address)
                            self.field_address.setDisabled(True)
                            self.file_content_text.setPlainText(self.fileEdited_object.text_list[textIndex])
                        else:
                            self.file_content_text.setPlainText("")
                            self.file_content_text.setReadOnly(True)
                    elif self.fileDisplayState == "Graphics":
                        self.widget_set = "Graphics"
                        if sender in self.FILEOPEN_WIDGETS:
                            self.layout_colorpick.rearrange(16, 16)
                            # reset from viewing font
                            self.tile_width = self.field_tile_width.value()
                            self.tile_height = self.field_tile_height.value()
                            if current_name == "face": # for convenience
                                self.tiles_per_column = 7
                                self.tiles_per_row = 6
                                self.field_tiles_per_column.setValue(self.tiles_per_column)
                                self.field_tiles_per_row.setValue(self.tiles_per_row)
                            self.dropdown_gfx_index.clear()
                            self.dropdown_gfx_subindex.clear()
                            try: # obj_fnt.bin
                                self.fileEdited_object = lib.graphic.File(self.rom.files[current_id])
                                for i in range(len(self.fileEdited_object.address_list)):
                                    self.dropdown_gfx_index.addItem(f"entry {i}")
                                self.dropdown_gfx_index.setCurrentIndex(0)
                            except AssertionError:
                                try: # face.bin and some other files
                                    self.fileEdited_object = lib.graphic.GraphicSection(self.rom.files[current_id])
                                except AssertionError:
                                    print("failed to load graphic entry table!")
                                    self.fileEdited_object = None
                        if self.fileEdited_object != None:
                            if isinstance(self.fileEdited_object, lib.graphic.File):
                                try:
                                    gfxsec = lib.graphic.GraphicSection.fromParent(self.fileEdited_object, self.dropdown_gfx_index.currentIndex())
                                except AssertionError:
                                    print("failed to load graphic section!")
                                    self.dropdown_gfx_subindex.clear()
                                    self.file_content_gfx.resetScene()
                                    return
                            elif isinstance(self.fileEdited_object, lib.graphic.GraphicSection):
                                gfxsec = self.fileEdited_object
                            if sender == self.dropdown_gfx_index or sender in self.FILEOPEN_WIDGETS: # if graphic section changed, reload header list
                                self.dropdown_gfx_subindex.clear()
                                for i in range(gfxsec.entryCount):
                                    self.dropdown_gfx_subindex.addItem(f"image {i}")
                                self.dropdown_gfx_subindex.setCurrentIndex(0)
                            if self.dropdown_gfx_subindex.count() > 0:
                                if sender == self.dropdown_gfx_index or sender == self.dropdown_gfx_subindex or sender in self.FILEOPEN_WIDGETS or sender == self.checkbox_depthUpdate:
                                    header_index = self.dropdown_gfx_subindex.currentIndex()
                                    if self.checkbox_depthUpdate.isChecked() and gfxsec.entry_size == 0x14:
                                        if gfxsec.graphics[header_index].depth//2 == 4:
                                            self.dropdown_gfx_depth.setCurrentIndex(1)
                                        elif gfxsec.graphics[header_index].depth//2 == 8:
                                            self.dropdown_gfx_depth.setCurrentIndex(2)
                                        else: # this should now be impossible
                                            print(f"unrecognized depth {gfxsec.graphics[header_index].depth}")
                                            self.dropdown_gfx_depth.setCurrentIndex(1)
                                    gfxOffset = gfxsec.graphics[header_index].offset_start + gfxsec.graphics[header_index].gfx_offset
                                    gfxSize = gfxsec.graphics[header_index].gfx_size
                                    print(f"{gfxsec.entryCount} sub-entrie(s)")
                                    print(f"oam_tile_indexing: {gfxsec.graphics[header_index].oam_tile_indexing:02X}")
                                    print(f"oam tile offset: {gfxsec.graphics[header_index].oam_tile_offset:02X}")
                                    print(f"unk08: {gfxsec.graphics[header_index].unk08:02X}")
                                    print(f"unk09: {gfxsec.graphics[header_index].unk09:02X}")
                                    if gfxsec.entry_size == 0x14:
                                        pal_off = gfxsec.graphics[header_index].offset_start + gfxsec.graphics[header_index].palette_offset+0xc
                                        pal = [0xffffffff]*(gfxsec.graphics[header_index].unk13 & 0xf0)
                                        pal.extend(lib.datconv.BGR15_to_ARGB32(self.rom.files[current_id][pal_off:pal_off+gfxsec.graphics[header_index].palette_size]))
                                        print(f"unk13 & 0F: {gfxsec.graphics[header_index].unk13 & 0x0f:02X}")
                                    else:
                                        pal = [] # empty palette because idk where it is
                                    self.setPalette(pal)
                                    self.relative_address = gfxOffset
                                    self.field_address.setRange(self.base_address+gfxOffset, self.base_address + gfxOffset+gfxSize)
                                    self.field_address.setValue(self.base_address+self.relative_address)
                            else:
                                print(f"{gfxsec.entryCount} graphic sub-entries!")
                                #print(f"data: {gfxsec.data.hex()}")

                        #print(self.dropdown_gfx_depth.currentText()[:1] + " bpp graphics")
                        # since the pen is in grayscale, we can use r, g or b as color index
                        if self.file_content_gfx.pen.color().blue() >= 2**list(lib.datconv.CompressionAlgorithmEnum)[self.dropdown_gfx_depth.currentIndex()].depth: # if color out of range
                            self.file_content_gfx.pen.setColor(0x00010101) # set to first color
                        self.file_content_gfx.resetScene()
                        draw_tilesQImage_fromBytes(self.file_content_gfx,
                                                   self.rom.files[current_id][self.relative_address:],
                                                   algorithm=list(lib.datconv.CompressionAlgorithmEnum)[self.dropdown_gfx_depth.currentIndex()],
                                                   grid=True)
                    elif self.fileDisplayState == "OAM":
                        self.widget_set = "OAM"
                        if sender in self.FILEOPEN_WIDGETS:
                            self.field_address.setDisabled(True)
                            self.fileEdited_object = lib.oam.File(self.rom.files[current_id])
                            self.fileEdited_object.auxfile = lib.graphic.File(self.rom.getFileByName(current_name.replace("dat", "fnt")+".bin"))
                            self.fileEdited_object.objs = []
                            self.dropdown_oam_entry.clear()
                            for i in range(self.fileEdited_object.entryCount):
                                self.dropdown_oam_entry.addItem(f"entry {i}")
                            self.dropdown_oam_entry.setCurrentIndex(0)
                        #print(f"{:02X}")
                        #print(oamsec.data[oamsec.frameTable_offset:oamsec.frameTable_offset+0x04].hex())
                        if sender in [self.dropdown_oam_entry, *self.FILEOPEN_WIDGETS]:
                            self.fileEdited_object.oamsec = lib.oam.OAMSection(self.fileEdited_object,
                                                                               self.dropdown_oam_entry.currentIndex() if self.dropdown_oam_entry.currentIndex() != -1 else 0)
                            self.fileEdited_object.gfxsec = lib.graphic.GraphicSection.fromParent(self.fileEdited_object.auxfile, self.dropdown_oam_entry.currentIndex())
                            print(f"offset: {self.fileEdited_object.oamsec.offset_start}")
                            print(f"header items: {[f"{header_item:02X}" for header_item in self.fileEdited_object.oamsec.header_items]}")

                            self.dropdown_oam_anim.clear()
                            for i in range(len(self.fileEdited_object.oamsec.animTable)):
                                self.dropdown_oam_anim.addItem(f"animation {i}")
                            self.dropdown_oam_anim.setCurrentIndex(0)

                            self.dropdown_oam_objFrame.clear()
                            if len(self.fileEdited_object.oamsec.frameTable) > 0:
                                for i in range(len(self.fileEdited_object.oamsec.frameTable)):
                                    self.dropdown_oam_objFrame.addItem(f"frame {i}")
                                self.dropdown_oam_objFrame.setCurrentIndex(0)
                        if sender in [self.dropdown_oam_entry, self.dropdown_oam_anim, *self.FILEOPEN_WIDGETS]:
                            self.fileEdited_object.oamsec_anim = lib.oam.Animation.fromParent(self.fileEdited_object.oamsec, self.dropdown_oam_anim.currentIndex())
                            self.checkbox_oam_animLoop.setChecked(self.fileEdited_object.oamsec_anim.isLooping)
                            self.field_oam_animLoopStart.setEnabled(self.fileEdited_object.oamsec_anim.isLooping)
                            self.button_oam_animPlay.autoPause()
                            if self.fileEdited_object.oamsec_anim.isLooping:
                                self.field_oam_animLoopStart.setValue(self.fileEdited_object.oamsec_anim.loopStart)
                            else:
                                self.field_oam_animLoopStart.setValue(0)
                            self.dropdown_oam_animFrame.clear()
                            if len(self.fileEdited_object.oamsec_anim.frames) > 0:
                                for i in range(len(self.fileEdited_object.oamsec_anim.frames)-1):
                                    self.dropdown_oam_animFrame.addItem(f"frame {i}")
                                self.dropdown_oam_animFrame.previousIndex = 0
                                self.dropdown_oam_animFrame.setCurrentIndex(0)
                        
                        if sender == self.button_oam_animFrameAdd:
                            self.button_file_save.setEnabled(True)
                            self.fileEdited_object.oamsec_anim.frames.insert(self.dropdown_oam_animFrame.currentIndex()+1, [0,1])
                            self.dropdown_oam_animFrame.addItem(f"frame {self.dropdown_oam_animFrame.count()}")
                            self.dropdown_oam_animFrame.setCurrentIndex(self.dropdown_oam_animFrame.currentIndex()+1)

                        if sender == self.button_oam_animFrameRemove:
                            if self.dropdown_oam_animFrame.count() == 0: return
                            self.button_file_save.setEnabled(True)
                            self.fileEdited_object.oamsec_anim.frames.pop(self.dropdown_oam_animFrame.currentIndex())
                            self.dropdown_oam_animFrame.removeItem(self.dropdown_oam_animFrame.count()-1)

                        if sender in [self.button_oam_animFrameAdd, self.button_oam_animFrameRemove, self.dropdown_oam_animFrame, self.dropdown_oam_entry, self.dropdown_oam_anim, *self.FILEOPEN_WIDGETS]:
                            if sender is not self.button_oam_animFrameRemove and (self.dropdown_oam_animFrame.previousIndex != self.dropdown_oam_animFrame.currentIndex() and self.button_file_save.isEnabled()):
                                isDurationfix = self.dropdown_oam_animFrame.previousIndex > 0 and self.field_oam_animFrameDuration.value() >= 0xFE
                                if isDurationfix:
                                    if self.field_oam_animFrameDuration.value() == 0xFE:
                                        self.field_oam_animFrameId.setValue(self.dropdown_oam_animFrame.previousIndex)
                                    elif self.field_oam_animFrameDuration.value() == 0xFF:
                                        self.field_oam_animFrameDuration.setValue(0)
                                self.fileEdited_object.oamsec_anim.frames[self.dropdown_oam_animFrame.previousIndex] = [
                                    self.field_oam_animFrameId.value(),
                                    self.field_oam_animFrameDuration.value()]
                            self.field_oam_animFrameId.setValue(self.fileEdited_object.oamsec_anim.frames[self.dropdown_oam_animFrame.currentIndex()][0])
                            self.field_oam_animFrameDuration.setValue(self.fileEdited_object.oamsec_anim.frames[self.dropdown_oam_animFrame.currentIndex()][1])
                            self.dropdown_oam_animFrame.previousIndex = self.dropdown_oam_animFrame.currentIndex()
                        
                        if len(self.fileEdited_object.oamsec.frameTable) > 0:
                            try:
                                if self.tabs_oam.currentWidget() == self.page_oam_frames:
                                    self.fileEdited_object.frame = self.fileEdited_object.oamsec.frameTable[
                                            self.dropdown_oam_objFrame.currentIndex() if self.dropdown_oam_objFrame.currentIndex() != -1 else 0]
                                elif self.tabs_oam.currentWidget() == self.page_oam_anims:
                                    self.fileEdited_object.frame = self.fileEdited_object.oamsec.frameTable[
                                            self.field_oam_animFrameId.value() if self.field_oam_animFrameId.isEnabled() else 0]
                                #print(f"section id: {self.fileEdited_object.frame[2]}")
                            except IndexError:
                                print(f"invalid frame!\nanim: {self.dropdown_oam_anim.currentIndex()}\nframe:{self.dropdown_oam_objFrame.currentIndex()}")
                                self.fileEdited_object.frame = []
                        else:
                            self.fileEdited_object.frame = []
                        if self.fileEdited_object.frame != []:
                            if sender in [self.dropdown_oam_entry, self.dropdown_oam_anim, self.dropdown_oam_animFrame, self.field_oam_animFrameId,
                                          self.button_oam_animFrameAdd, self.button_oam_animFrameRemove, 
                                          self.dropdown_oam_objFrame, self.tabs_oam, self.button_reload, *self.FILEOPEN_WIDGETS]:
                                self.file_content_oam.scene().clear()
                                sceneRect = self.file_content_oam.sceneRect()
                                crosshairPen = QtGui.QPen()
                                crosshairPen.setWidthF(0.05) # extra thin line
                                self.file_content_oam.scene().addRect(sceneRect)
                                self.file_content_oam.scene().addLine(sceneRect.left(), 0, sceneRect.right(), 0, crosshairPen)
                                self.file_content_oam.scene().addLine(0, sceneRect.top(), 0, sceneRect.bottom(), crosshairPen)
                                if not isinstance(sender, lib.widget.BetterSpinBox) and sender not in [
                                    self.button_oam_animFrameAdd, self.button_oam_animFrameRemove, self.dropdown_oam_animFrame]:
                                    self.button_file_save.setDisabled(True)
                                self.fileEdited_object.objs.clear()
                                self.dropdown_oam_obj.clear()
                                #print("start")
                                for i in range(self.fileEdited_object.frame[1]):
                                    if i >= 128:
                                        print("Object limit reached! Proceed at your own risk!")
                                        break
                                    self.dropdown_oam_obj.addItem(f"object {i}")
                                    obj_offset = self.fileEdited_object.oamsec.frameTable_offset + self.fileEdited_object.frame[0] + i*0x04
                                    self.fileEdited_object.objs.append(lib.oam.Object(self.fileEdited_object.oamsec.data[obj_offset:obj_offset+0x04]))
                                    obj_item = self.OAM_updateItemGFX(i)
                                    if obj_item.obj_id == 0:
                                        self.file_content_oam.item_current = obj_item
                                    self.file_content_oam.scene().addItem(obj_item)

                                if sender == self.dropdown_oam_entry:
                                    self.file_content_oam.fitInView()
                                self.dropdown_oam_obj.previousIndex = 0
                                self.dropdown_oam_obj.setCurrentIndex(0)

                            if sender == self.button_oam_objAdd:
                                if self.dropdown_oam_obj.count() > 128: return
                                self.button_file_save.setEnabled(True)
                                self.fileEdited_object.objs.insert(self.dropdown_oam_obj.currentIndex()+1, lib.oam.Object())
                                for item in self.file_content_oam.scene().items():
                                    if isinstance(item, lib.widget.OAMObjectItem) and item.obj_id > self.dropdown_oam_obj.currentIndex():
                                        item.obj_id += 1
                                        item.setZValue(-item.obj_id) # update depth
                                self.file_content_oam.scene().addItem(self.OAM_updateItemGFX(self.dropdown_oam_obj.currentIndex()+1))
                                self.dropdown_oam_obj.addItem(f"object {self.dropdown_oam_obj.count()}")
                                self.dropdown_oam_obj.setCurrentIndex(self.dropdown_oam_obj.currentIndex()+1)
                                
                            if sender == self.button_oam_objRemove:
                                if self.dropdown_oam_obj.count() == 0: return
                                self.button_file_save.setEnabled(True)
                                self.fileEdited_object.objs.pop(self.dropdown_oam_obj.currentIndex())
                                for item in self.file_content_oam.scene().items():
                                    if isinstance(item, lib.widget.OAMObjectItem) and item.obj_id == self.dropdown_oam_obj.currentIndex():
                                        self.file_content_oam.scene().removeItem(item)
                                for item in self.file_content_oam.scene().items():
                                    if isinstance(item, lib.widget.OAMObjectItem) and item.obj_id > self.dropdown_oam_obj.currentIndex():
                                        item.obj_id -= 1
                                        item.setZValue(-item.obj_id) # update depth
                                self.dropdown_oam_obj.removeItem(self.dropdown_oam_obj.count()-1)

                            if sender in [self.button_oam_objAdd, self.button_oam_objRemove, self.dropdown_oam_obj, self.dropdown_oam_entry, self.dropdown_oam_objFrame, self.tabs_oam, self.file_content_oam.scene(), *self.FILEOPEN_WIDGETS]:
                                #print(f"{frame[0]:02X}")
                                #print(f"frame: {self.dropdown_oam_objFrame.currentIndex()}")
                                if self.tabs_oam.currentWidget()!=self.page_oam_frames:return
                                if self.dropdown_oam_obj.currentIndex() == -1: return
                                if sender is not self.button_oam_objRemove and self.dropdown_oam_obj.previousIndex != self.dropdown_oam_obj.currentIndex() and self.button_file_save.isEnabled(): # save state of previous object
                                    obj_prev = self.fileEdited_object.objs[self.dropdown_oam_obj.previousIndex]
                                    obj_prev.tileId = self.field_objTileId.value()
                                    obj_prev.flip_h = self.checkbox_objFlipH.isChecked()
                                    obj_prev.flip_v = self.checkbox_objFlipV.isChecked()
                                    obj_prev.sizeIndex = self.slider_objSizeIndex.sl.value()
                                    obj_prev.shape = self.buttonGroup_oam_objShape.checkedId()
                                    obj_prev.x = self.field_objX.value()
                                    obj_prev.y = self.field_objY.value()
                                offset = self.fileEdited_object.oamsec.frameTable_offset + self.fileEdited_object.frame[0] + self.dropdown_oam_obj.currentIndex()*0x04
                                self.relative_address = self.fileEdited_object.address_list[self.dropdown_oam_entry.currentIndex()][0] + offset
                                self.field_address.setValue(self.relative_address + self.base_address)
                                obj = self.fileEdited_object.objs[self.dropdown_oam_obj.currentIndex()]#lib.oam.Object(oamsec.data[offset:offset+0x04])
                                self.dropdown_oam_obj.previousIndex = self.dropdown_oam_obj.currentIndex()
                                self.field_objTileId.setValue(obj.tileId)
                                self.checkbox_objFlipH.setChecked(obj.flip_h)
                                self.checkbox_objFlipV.setChecked(obj.flip_v)
                                self.slider_objSizeIndex.sl.setValue(obj.sizeIndex)
                                self.group_oam_objShape.findChildren(QtWidgets.QRadioButton)[obj.shape].setChecked(True)
                                self.slider_objSizeIndex.setLabels(lib.oam.SPRITE_DIMENSIONS[self.buttonGroup_oam_objShape.checkedId()])
                                self.field_objX.setValue(obj.x)
                                self.field_objY.setValue(obj.y)
                            if sender in [self.button_oam_objAdd, self.button_oam_objRemove, self.dropdown_oam_obj, self.button_oam_objSelect]:
                                for item in self.file_content_oam.scene().items():
                                    if isinstance(item, lib.widget.OAMObjectItem):
                                        item.setSelected(item.obj_id == self.dropdown_oam_obj.currentIndex())
                        else:
                            print("empty frame!")
                    elif self.fileDisplayState == "Palette Animation":
                        self.widget_set = "PAnm"
                        if sender in self.FILEOPEN_WIDGETS:
                            self.fileEdited_object = lib.panim.File(self.rom.files[current_id])
                            self.dropdown_gfx_depth.setCurrentIndex(1)
                            self.dropdown_panm_entry.clear()
                            for i in range(self.fileEdited_object.animCount):
                                self.dropdown_panm_entry.addItem("palette animation "+str(i))
                            self.dropdown_panm_entry.setCurrentIndex(0)
                            self.dropdown_panm_entry.previousIndex = 0
                        anim_current = self.fileEdited_object.anims[self.dropdown_panm_entry.currentIndex()]
                        palette_current = self.fileEdited_object.palettes[self.dropdown_panm_entry.currentIndex()]
                        if sender in [self.dropdown_panm_entry, *self.FILEOPEN_WIDGETS]:
                            self.layout_colorpick.rearrange(2, len(palette_current.colorTable)) # rearrange palette button layout for this mode
                            if self.button_file_save.isEnabled():
                                self.fileEdited_object.anims[self.dropdown_panm_entry.previousIndex].isLooping = self.checkbox_panm_loop.isChecked()
                                self.fileEdited_object.anims[self.dropdown_panm_entry.previousIndex].loopStart = self.field_panm_loopStart.value()
                                self.fileEdited_object.palettes[self.dropdown_panm_entry.previousIndex].colorSlot0 = self.field_panm_colorSlot0.value()
                                self.fileEdited_object.palettes[self.dropdown_panm_entry.previousIndex].colorSlot1 = self.field_panm_colorSlot1.value()
                            self.dropdown_panm_frame.clear()
                            for i in range(len(self.fileEdited_object.anims[self.dropdown_panm_entry.currentIndex()].frames)-1):
                                self.dropdown_panm_frame.addItem("frame "+str(i))
                            self.dropdown_panm_frame.setCurrentIndex(0)
                            self.setPalette([color for group in self.fileEdited_object.palettes[self.dropdown_panm_entry.currentIndex()].colorTable for color in group])
                            self.checkbox_panm_loop.setChecked(anim_current.isLooping)
                            self.field_panm_loopStart.setValue(anim_current.loopStart)
                            self.field_panm_colorSlot0.setValue(palette_current.colorSlot0)
                            self.field_panm_colorSlot1.setValue(palette_current.colorSlot1)
                        if sender in [self.dropdown_panm_frame, self.dropdown_panm_entry, *self.FILEOPEN_WIDGETS]:
                            frame_current = anim_current.frames[self.dropdown_panm_frame.currentIndex()]
                            if self.button_file_save.isEnabled():
                                self.fileEdited_object.anims[self.dropdown_panm_entry.previousIndex].frames[self.dropdown_panm_frame.previousIndex]\
                                = [self.field_panm_frameId.value(), self.field_panm_frameDuration.value()]
                            self.field_panm_frameId.setValue(frame_current[0])
                            self.field_panm_frameDuration.setValue(frame_current[1])
                            # load some object
                            self.dropdown_panm_frame.previousIndex = self.dropdown_panm_frame.currentIndex()
                            if sender == self.dropdown_panm_entry:
                                self.dropdown_panm_entry.previousIndex = self.dropdown_panm_entry.currentIndex()
                    elif self.fileDisplayState == "Font":
                        self.widget_set = "Font"
                        if sender in self.FILEOPEN_WIDGETS:
                            self.layout_colorpick.rearrange(2, 1)
                            self.dropdown_gfx_depth.setCurrentIndex(0)
                            self.fileEdited_object = lib.font.Font(self.rom.files[current_id])
                            self.relative_address = self.fileEdited_object.CHR_ADDRESS
                            self.field_font_size.setValue(self.fileEdited_object.file_size)
                            self.field_font_width.setValue(self.fileEdited_object.char_width)
                            self.field_font_height.setValue(self.fileEdited_object.char_height)
                            self.label_font_indexingSpace.setText("indexing space: " + lib.datconv.numToStr(self.fileEdited_object.indexing_space, self.displayBase, self.displayAlphanumeric))
                            self.label_font_charCount.setText("char count: " + lib.datconv.numToStr(self.fileEdited_object.char_count, self.displayBase, self.displayAlphanumeric))
                            self.label_font_unusedStr.setText("unused string: " + self.fileEdited_object.unused_string)
                            self.setPalette(self.GFX_PALETTES[1])
                            self.field_address.setMinimum(self.base_address+self.fileEdited_object.CHR_ADDRESS)
                        self.file_content_gfx.resetScene()
                        self.tile_width = math.ceil(self.field_font_width.value()/8)*8
                        self.tile_height = self.field_font_height.value()
                        draw_tilesQImage_fromBytes(self.file_content_gfx,
                                                   self.rom.files[current_id][self.relative_address:self.relative_address+self.fileEdited_object.file_size],
                                                   algorithm=list(lib.datconv.CompressionAlgorithmEnum)[self.dropdown_gfx_depth.currentIndex()],
                                                   grid=True)
                    elif self.fileDisplayState == "Sound":
                        self.widget_set = "Empty" # placeholder
                        #self.widget_set = "Sound"
                        self.file_content_text.setReadOnly(True)
                        self.file_content_text.setPlainText("Sound editor is not yet implemented.\n Right click on this file > open Sound Archive\nor click on the sound icon in the toolbar to open sound archive viewer.")
                        self.field_address.setDisabled(True)
                    elif self.fileDisplayState == "VX":
                        self.widget_set = "VX"
                        if sender in self.FILEOPEN_WIDGETS:
                            self.field_address.setDisabled(True)
                            self.fileEdited_object = lib.act.ActImagine()
                            self.fileEdited_object.load_vx(self.rom.files[current_id])
                            #print(self.rom.files[current_id][5:6].hex()+self.rom.files[current_id][4:5].hex())
                            self.field_vxHeader_length.setValue(self.fileEdited_object.frames_qty)
                            self.field_vxHeader_width.setValue(self.fileEdited_object.frame_width)
                            self.field_vxHeader_height.setValue(self.fileEdited_object.frame_height)
                            self.field_vxHeader_framerate.setValue(self.fileEdited_object.frame_rate)
                            self.field_vxHeader_quantizer.setValue(self.fileEdited_object.quantizer)
                            self.field_vxHeader_sampleRate.setValue(self.fileEdited_object.audio_sample_rate)
                            self.field_vxHeader_streamCount.setValue(self.fileEdited_object.audio_streams_qty)
                            self.field_vxHeader_frameSizeMax.setValue(self.fileEdited_object.frame_data_size_max)
                            self.field_vxHeader_audioExtraDataOffset.setValue(self.fileEdited_object.audio_extradata_offset)
                            self.field_vxHeader_seekTableOffset.setValue(self.fileEdited_object.seek_table_offset)
                            self.field_vxHeader_seekTableEntryCount.setValue(self.fileEdited_object.seek_table_entries_qty)
                    else:
                        self.widget_set = "Empty"
                        self.field_address.setDisabled(True)
                        self.file_content_text.setReadOnly(True)
                        if self.fileDisplayState == "None":
                            file_knowledge = "unknown"
                        else:
                            file_knowledge = "not supported at the moment"
                        self.file_content_text.setPlainText(f"This file's format is {file_knowledge}.\n Go to [View > Converted formats] to disable file interpretation and view hex data.")
                else:# if in hex display mode
                    self.widget_set = "Hex"
                    self.file_content_text.setPlainText(self.rom.files[current_id][self.relative_address:self.relative_address+self.file_content_text.charcount_page()].hex())
                self.file_content_text.setDisabled(False)
            else:# if it's a folder
                self.widget_set = "Empty"
                self.label_file_size.setText(f"Size: N/A")
                self.field_address.setDisabled(True)
                self.file_content_text.setPlainText("")
                self.file_content_text.setDisabled(True)
            # code that applies to any item
            self.exportAction.setDisabled(False)
            self.replaceAction.setDisabled(False)
        else:# Nothing is selected, reset edit space
            self.widget_set = "Empty"
            self.field_address.setDisabled(True)
            self.label_file_size.setText("Size: N/A")
            self.file_content_text.clear()
            self.file_content_text.setDisabled(True)
            self.exportAction.setDisabled(True)
            self.replaceAction.setDisabled(True)

    def loadTileProperties(self):
        if not self.gfx_scene_tileset.scene().isActive(): return
        if len(self.gfx_scene_tileset.scene().selectedItems()) == 0:
            for i in range(self.layout_metaTile_properties.count()):
                layout = self.layout_metaTile_properties.itemAt(i)
                if isinstance(layout, QtWidgets.QLayout):
                    for j in range(layout.count()):
                        layout.itemAt(j).widget().setDisabled(True)
            return
        level = self.levelEdited_object.levels[self.dropdown_level_type.currentIndex()]
        for i in range(self.layout_metaTile_properties.count()):
            layout = self.layout_metaTile_properties.itemAt(i)
            if isinstance(layout, QtWidgets.QLayout):
                for j in range(layout.count()):
                    layout.itemAt(j).widget().blockSignals(True)
        for w in self.group_metaTile_gfx.children():
                w.blockSignals(True)

        if len(self.gfx_scene_tileset.scene().selectedItems()) == 1:
            metaTile_index = self.gfx_scene_tileset.metaTiles.index(*self.gfx_scene_tileset.scene().selectedItems())
            attr = level.collision[metaTile_index][1]
            self.dropdown_metaTile_collisionShape.setCurrentIndex(level.collision[metaTile_index][0] & 0x0F)
            self.dropdown_metaTile_collisionMaterial.setCurrentIndex((level.collision[metaTile_index][0] & 0xF0) >> 4)
            self.field_metaTile_topLeft_id.setValue(level.metaTiles[metaTile_index][0] & 0x03FF)
            self.checkbox_metaTile_topLeft_flipH.setChecked((level.metaTiles[metaTile_index][0] & 0x400) >> (8+2))
            self.field_metaTile_topLeft_attr.setValue((level.metaTiles[metaTile_index][0] & 0xF000) >> (8+4))
            self.checkbox_metaTile_topLeft_flipV.setChecked((level.metaTiles[metaTile_index][0] & 0x800) >> (8+3))
            self.field_metaTile_topRight_id.setValue(level.metaTiles[metaTile_index][1] & 0x03FF)
            self.checkbox_metaTile_topRight_flipH.setChecked((level.metaTiles[metaTile_index][1] & 0x400) >> (8+2))
            self.field_metaTile_topRight_attr.setValue((level.metaTiles[metaTile_index][1] & 0xF000) >> (8+4))
            self.checkbox_metaTile_topRight_flipV.setChecked((level.metaTiles[metaTile_index][1] & 0x800) >> (8+3))
            self.field_metaTile_bottomLeft_id.setValue(level.metaTiles[metaTile_index][2] & 0x03FF)
            self.checkbox_metaTile_bottomLeft_flipH.setChecked((level.metaTiles[metaTile_index][2] & 0x400) >> (8+2))
            self.field_metaTile_bottomLeft_attr.setValue((level.metaTiles[metaTile_index][2] & 0xF000) >> (8+4))
            self.checkbox_metaTile_bottomLeft_flipV.setChecked((level.metaTiles[metaTile_index][2] & 0x800) >> (8+3))
            self.field_metaTile_bottomRight_id.setValue(level.metaTiles[metaTile_index][3] & 0x03FF)
            self.checkbox_metaTile_bottomRight_flipH.setChecked((level.metaTiles[metaTile_index][3] & 0x400) >> (8+2))
            self.field_metaTile_bottomRight_attr.setValue((level.metaTiles[metaTile_index][3] & 0xF000) >> (8+4))
            self.checkbox_metaTile_bottomRight_flipV.setChecked((level.metaTiles[metaTile_index][3] & 0x800) >> (8+3))
        else:
            attr = 0x00
            self.dropdown_metaTile_collisionShape.setCurrentIndex(0)
            self.dropdown_metaTile_collisionMaterial.setCurrentIndex(0)
            self.field_metaTile_topLeft_id.setValue(0)
            self.field_metaTile_topRight_id.setValue(0)
            self.field_metaTile_bottomLeft_id.setValue(0)
            self.field_metaTile_bottomRight_id.setValue(0)
            self.field_metaTile_topLeft_id.setValue(0)
            self.checkbox_metaTile_topLeft_flipH.setChecked(False)
            self.field_metaTile_topLeft_attr.setValue(0)
            self.checkbox_metaTile_topLeft_flipV.setChecked(False)
            self.field_metaTile_topRight_id.setValue(0)
            self.checkbox_metaTile_topRight_flipH.setChecked(False)
            self.field_metaTile_topRight_attr.setValue(0)
            self.checkbox_metaTile_topRight_flipV.setChecked(False)
            self.field_metaTile_bottomLeft_id.setValue(0)
            self.checkbox_metaTile_bottomLeft_flipH.setChecked(False)
            self.field_metaTile_bottomLeft_attr.setValue(0)
            self.checkbox_metaTile_bottomLeft_flipV.setChecked(False)
            self.field_metaTile_bottomRight_id.setValue(0)
            self.checkbox_metaTile_bottomRight_flipH.setChecked(False)
            self.field_metaTile_bottomRight_attr.setValue(0)
            self.checkbox_metaTile_bottomRight_flipV.setChecked(False)

        self.checkbox_metaTile_attrSpike.setChecked((attr & 0b00000001))
        self.checkbox_metaTile_attrWater.setChecked((attr & 0b00000010) >> 1)
        self.checkbox_metaTile_attrNoCeilHang.setChecked((attr & 0b00000100) >> 2)
        self.checkbox_metaTile_attrNoWalljump.setChecked((attr & 0b00001000) >> 3)
        self.checkbox_metaTile_attrSand.setChecked((attr & 0b00010000) >> 4)
        self.group_metaTile_attrConvey.findChildren(QtWidgets.QRadioButton)[(attr & 0b01100000) >> 5].setChecked(True)
        self.checkbox_metaTile_attrPlat.setChecked((attr & 0b10000000) >> 7)

        for i in range(self.layout_metaTile_properties.count()):
            layout = self.layout_metaTile_properties.itemAt(i)
            if isinstance(layout, QtWidgets.QLayout):
                for j in range(layout.count()):
                    layout.itemAt(j).widget().blockSignals(False)
                    layout.itemAt(j).widget().setEnabled(True)
        for w in self.group_metaTile_gfx.children():
                w.blockSignals(False)

    def changeTileShape(self):
        if not self.gfx_scene_tileset.scene().isActive() or len(self.gfx_scene_tileset.scene().selectedItems()) == 0: return
        self.button_level_save.setEnabled(True)
        level = self.levelEdited_object.levels[self.dropdown_level_type.currentIndex()]
        for item in self.gfx_scene_tileset.scene().selectedItems():
            metaTile_index = self.gfx_scene_tileset.metaTiles.index(item)
            level.collision[metaTile_index][0] = \
                (level.collision[metaTile_index][0] & 0xF0) | self.dropdown_metaTile_collisionShape.currentIndex()

    def changeTileMaterial(self):
        if not self.gfx_scene_tileset.scene().isActive() or len(self.gfx_scene_tileset.scene().selectedItems()) == 0: return
        self.button_level_save.setEnabled(True)
        level = self.levelEdited_object.levels[self.dropdown_level_type.currentIndex()]
        for item in self.gfx_scene_tileset.scene().selectedItems():
            metaTile_index = self.gfx_scene_tileset.metaTiles.index(item)
            level.collision[metaTile_index][0] = \
                (level.collision[metaTile_index][0] & 0x0F) | (self.dropdown_metaTile_collisionMaterial.currentIndex() << 4)

    def changeTileAttr(self, bitmask: int, val: bool):
        if not self.gfx_scene_tileset.scene().isActive() or len(self.gfx_scene_tileset.scene().selectedItems()) == 0: return
        self.button_level_save.setEnabled(True)
        level = self.levelEdited_object.levels[self.dropdown_level_type.currentIndex()]
        for item in self.gfx_scene_tileset.scene().selectedItems():
            metaTile_index = self.gfx_scene_tileset.metaTiles.index(item)
            bitstring = bin(bitmask).removeprefix("0b").zfill(8)
            shiftL = len(bitstring)-1 - bitstring.rindex('0')
            level.collision[metaTile_index][1] = \
                (level.collision[metaTile_index][1] & bitmask) | (val << shiftL)
        
    def changeTileGfx(self, index:int, bitmask: int, val: bool):
        if not self.gfx_scene_tileset.scene().isActive() or len(self.gfx_scene_tileset.scene().selectedItems()) == 0: return
        self.button_level_save.setEnabled(True)
        level = self.levelEdited_object.levels[self.dropdown_level_type.currentIndex()]
        for item in self.gfx_scene_tileset.scene().selectedItems():
            metaTile_index = self.gfx_scene_tileset.metaTiles.index(item)
            bitstring = bin(bitmask).removeprefix("0b").zfill(16)
            print(bitmask, bitstring)
            shiftL = len(bitstring)-1 - bitstring.rindex('0')
            level.metaTiles[metaTile_index][index] = \
                (level.metaTiles[metaTile_index][index] & bitmask) | (val << shiftL)

    def loadTileset(self, gfx_table: lib.graphic.GraphicsTable, pal_sec: lib.level.PaletteSection, gfx_ptrs: list[int]|None=None):
        self.gfx_scene_tileset.scene().clear()
        gfx = lib.graphic.GraphicHeader(gfx_table.joinData()[0])
        self.gfx_scene_tileset.metaTiles = []
        pixmap = QtGui.QPixmap(16, 16)
        painter = QtGui.QPainter()
        painter.begin(pixmap)
        pal_list: list[dict] = []
        pl: dict = {}
        ref = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap.fromImage(lib.datconv.binToQt(gfx.data, self.GFX_PALETTES[3], lib.datconv.CompressionAlgorithmEnum.EIGHTBPP, 32, len(gfx.data)//64//32)))
        ref.setPos(-32*8-self.gfx_scene_tileset.item_spacing*2, 0)
        self.gfx_scene_tileset.scene().addItem(ref) # to see the gfx used to construct tileset
        for i in range(pal_sec.palHeaderCount):
            pl.clear()
            for j in range(pal_sec.paletteHeaders[i].palCount):
                #print(pal_sec.paletteHeaders[i].palettes[j][0])
                pl[pal_sec.paletteHeaders[i].palettes[j][0]] = (lib.datconv.BGR15_to_ARGB32(
                        pal_sec.data[pal_sec.paletteOffsets[i]+pal_sec.paletteHeaders[i].palettes[j][1]:
                                    pal_sec.paletteOffsets[i]+pal_sec.paletteHeaders[i].palettes[j][1]+0x200]))
            pal_list.append(pl.copy())
        ptr_index = 0
        for metaTile_index, metaTile in enumerate(self.levelEdited_object.levels[self.dropdown_level_type.currentIndex()].metaTiles):
            for tile_index, tile in enumerate(metaTile):
                flipH = (tile & 0x0400) >> (8+2)
                flipV = (tile & 0x0800) >> (8+3)
                tileId = (tile & 0x03FF)
                tile_pal = (tile & 0xF000) >> (8+4)
                # idk how to organize palettes and gfx chunks here
                if gfx_ptrs != None:
                    ptr_index = metaTile_index//(225)
                    pal_index = max(0, bisect.bisect_left(gfx_ptrs, (64*tileId)+1)-1)
                else:
                    ptr_index = 0
                    pal_index = 0
                #print(pal_index, tile_pal)
                try:
                    pal = pal_list[pal_index][tile_pal]
                except:
                    #print("palette error at", pal_index, tile_pal)
                    pal = list(pal_list[pal_index].values())[0]
                gfx_bin = gfx.data[gfx.gfx_offset:][64*tileId:]
                #gfx_bin = gfx.data[gfx.gfx_offset:][gfx_ptrs[ptr_index]+64*(tileId&0x3FF):]
                painter.drawImage(QtCore.QRectF(8*(tile_index%2), 8*(tile_index//2), 8, 8), lib.datconv.binToQt(gfx_bin, pal, lib.datconv.CompressionAlgorithmEnum.EIGHTBPP, 1, 1).mirrored(flipH, flipV))
            
            metaTileItem = lib.widget.TilesetItem(pixmap)
            metaTileItem.setPos((16+self.gfx_scene_tileset.item_spacing)*(metaTile_index%self.gfx_scene_tileset.item_columns), (16+self.gfx_scene_tileset.item_spacing)*(metaTile_index//self.gfx_scene_tileset.item_columns))
            self.gfx_scene_tileset.scene().addItem(metaTileItem)
            self.gfx_scene_tileset.metaTiles.append(metaTileItem)
        painter.end()
        self.gfx_scene_tileset.fitInView()

    def initScreens(self):
        self.gfx_scene_level.tileGroups = []
        level = self.levelEdited_object.levels[self.dropdown_level_type.currentIndex()]
        for screen_index in range(len(level.screens)):
            self.gfx_scene_level.tileGroups.append([])
            for metaTile_index in range(len(level.screens[screen_index])):
                self.gfx_scene_level.tileGroups[screen_index].append([])

    def loadScreen(self, screen_id: int, x: float=0, y: float=0):
        #print(f"screen {screen_id}")
        screen = self.levelEdited_object.levels[self.dropdown_level_type.currentIndex()].screens[screen_id]
        for metaTile_index, metaTile in enumerate(screen):
            item = lib.widget.LevelTileItem(index=metaTile_index, id=metaTile, screen=screen_id)
            item.setPixmap(self.gfx_scene_tileset.metaTiles[metaTile].pixmap())
            item.setPos(x + 16*(metaTile_index%16),y + 16*(metaTile_index//16))
            self.gfx_scene_level.scene().addItem(item)
            self.gfx_scene_level.tileGroups[screen_id][metaTile_index].append(item)
            item.tileGroup = self.gfx_scene_level.tileGroups[screen_id][metaTile_index]
            #print(item.pos())

    def loadLevel(self):
        self.button_level_save.setDisabled(True)
        fileID = self.rom.filenames.idOf(self.dropdown_level_area.currentText()+".bin")
        print("Load level")
        try :
            self.levelEdited_object = lib.level.File(self.rom.files[fileID])
        except TypeError:
            self.gfx_scene_level.scene().clear()
            self.gfx_scene_tileset.scene().clear()
            QtWidgets.QMessageBox.critical(
                self,
                "Load Failed",
                "This file or its pointers may be corrupted"
            )
            return
        file = self.levelEdited_object
        if self.sender() == self.dropdown_level_area:
            self.buttonGroup_radar_tilesetType.blockSignals(True)
            self.radio_radar_PX.setChecked(True)
            self.buttonGroup_radar_tilesetType.blockSignals(False)
            self.dropdown_level_type.blockSignals(True)
            self.dropdown_level_type.clear()
            self.dropdown_level_type.addItem("Normal Level")
            if len(file.levels) > 1:
                self.dropdown_level_type.addItem("Radar Level")
            self.dropdown_level_type.setCurrentIndex(0)
            self.dropdown_level_type.blockSignals(False)
        self.group_radar_tilesetType.setEnabled(self.dropdown_level_type.currentIndex() == 1)
        level = file.levels[self.dropdown_level_type.currentIndex()]
        print(f"level offset: {file.level_offset_rom:02X}")
        print(f"gfx offset: {file.gfx_offset_rom:02X}")
        print(f"pal offset: {file.pal_offset_rom:02X}")
        print(f"leveldata size: {len(file.data[file.level_offset_rom:file.gfx_offset_rom])}")
        gfx_ptrs = None
        if level == file.level:
            if file.gfx_offset_attr == 0x80: # if compressed
                gfx_data = ndspy.lz10.decompress(file.data[file.gfx_offset_rom:file.pal_offset_rom])
            else:
                gfx_data = file.data[file.gfx_offset_rom:file.pal_offset_rom]
            gfx_table = lib.graphic.GraphicsTable(gfx_data, start=file.gfx_offset_rom, end=file.pal_offset_rom)
            table_dat = gfx_table.joinData()
            gfx = lib.graphic.GraphicHeader(table_dat[0], start=file.gfx_offset_rom, end=file.pal_offset_rom)
            gfx_ptrs = table_dat[1]

            pal_sec = lib.level.PaletteSection(file.data[file.pal_offset_rom:], file.pal_offset_attr == 0x80)
            #pal = lib.datconv.BGR15_to_ARGB32(pal_sec.data[pal_sec.palettes_offset:pal_sec.palettes_offset+0x200])
        elif level == file.level_radar:
            if self.rom.filenames.idOf("elf_usa.bin") != None: # ZX
                file_radar = self.rom.files[self.rom.filenames.idOf("elf_usa.bin")]
                pointergfx = int.from_bytes(file_radar[0x04:0x08], 'little')
                pointerpal = int.from_bytes(file_radar[0x08:0x0C], 'little')
                gfx_table = lib.graphic.GraphicsTable(file_radar[pointergfx:], start=pointergfx, end=pointerpal)
                # compressed part has redundant tiles at the end
                gfx = lib.graphic.GraphicHeader(
                    ndspy.lz10.decompress(gfx_table.getData(0))[:-0x200]+gfx_table.getData(gfx_table.offsetCount-self.buttonGroup_radar_tilesetType.checkedId()),
                      start=gfx_table.getAddr(0), end=pointerpal)
            else: # ZXA
                file_radar = self.rom.files[self.rom.filenames.idOf("ls_map_def.bin")]
                pointergfx = int.from_bytes(file_radar[0x04:0x08], 'little')
                pointerpal = int.from_bytes(file_radar[0x08:0x0C], 'little')
                gfx_table = lib.graphic.GraphicsTable(file_radar[pointergfx:], start=pointergfx, end=pointerpal)
                gfx = lib.graphic.GraphicHeader(
                    gfx_table.getData(0)[:-0x480]+gfx_table.getData(gfx_table.offsetCount-self.buttonGroup_radar_tilesetType.checkedId())[0x240:],
                      start=gfx_table.getAddr(0), end=pointerpal)
                #gfx = lib.graphic.GraphicHeader(file_radar[pointergfx:], start=pointergfx, end=len(file_radar))
            pal_sec = lib.level.PaletteSection(file_radar[pointerpal:], False)
            #pal = lib.datconv.BGR15_to_ARGB32(pal_sec.data[pal_sec.palettes_offset:pal_sec.palettes_offset+0x200])
        else:
            print("invalid level type!")
            return
        #print(gfx.gfx_offset)
        #self.loadTileset(gfx_sec.data[gfx.offset_start+gfx.gfx_offset:], pal)
        #self.loadTileset(gfx.data[gfx.gfx_offset:], pal_sec, gfx_ptrs)
        self.loadTileset(gfx_table, pal_sec, gfx_ptrs)
        self.gfx_scene_level.scene().clear()
        self.initScreens()
        for i in range(len(level.screens)):
            self.loadScreen(i, i*16*16.25)
        if self.sender() != self.buttonGroup_radar_tilesetType:
            self.gfx_scene_level.fitInView()

    def treeBaseUpdate(self, tree: lib.widget.EditorTree):
        for e in tree.findItems("", QtCore.Qt.MatchFlag.MatchContains | QtCore.Qt.MatchFlag.MatchRecursive):
            for t in range(e.columnCount()):
                text = e.text(t)
                text_header = tree.headerItem().text(t).lower()
                if any(char.isdigit() for char in text) and text.replace("{", "").replace("}", "").isalnum():
                    if not "file id" in text_header:
                        value = lib.datconv.strToNum(text, self.displayBase_old)
                        newtext = lib.datconv.numToStr(value, self.displayBase, self.displayAlphanumeric)
                        zerofill = 8 if "address" in text_header else 0
                        e.setText(t, newtext.zfill(zerofill))

    def reloadCall(self, level: int=0): # Reload all reloadable content
        if hasattr(self.rom, "name"):
            #print("reloadlevel " + str(level))
            if level == 0: #reload only necessary
                self.treeCall() # update for betterspinboxes as well
                self.treeBaseUpdate(self.tree_arm9)
                self.treeBaseUpdate(self.tree_arm9Ovltable)
                self.treeBaseUpdate(self.tree_arm7)
                self.treeBaseUpdate(self.tree_arm7Ovltable)
                self.treeBaseUpdate(self.tree_patches)
            elif level == 1: #medium reload
                self.treeBaseUpdate(self.tree_arm9)
                self.treeBaseUpdate(self.tree_arm9Ovltable)
                self.treeBaseUpdate(self.tree_arm7)
                self.treeBaseUpdate(self.tree_arm7Ovltable)
                self.treeCall(addr_reset=True)
                self.patches_reload()
            else: #reload everything
                self.tree.setCurrentItem(None)
                self.field_address.setRange(0,0)
                self.treeArm9Update()
                self.treeArm7Update()
                self.treeSdatUpdate()
                self.treeUpdate()
                self.patches_reload()
            self.displayBase_old = self.displayBase

    def tabChangeCall(self):
        if self.rom == None: return
        if self.tabs.currentIndex() == self.tabs.indexOf(self.page_explorer):
            self.treeCall()

    def file_editor_show(self, mode: str): # UiComponents
        modes = ["Empty", "Hex", "Text", "Graphics", "OAM", "PAnm", "Font", "Sound", "VX"]
        # Associates each mode with a set of widgets to show or hide
        widget_sets = [self.WIDGETS_EMPTY, self.WIDGETS_HEX, self.WIDGETS_TEXT, self.WIDGETS_GRAPHIC, self.WIDGETS_OAM, self.WIDGETS_PANM, self.WIDGETS_FONT, self.WIDGETS_SOUND, self.WIDGETS_VX]

        mode_index = modes.index(mode)
        # Hide all widgets from other modes
        for s in widget_sets:
            if s != widget_sets[mode_index]:
                for w in s:
                    w.hide()
        # Show widgets specific to this mode
        for w in widget_sets[mode_index]:
            w.show()
        # case-specific code
        if mode == "Graphics" or "Font":
            # Reset Values
            #self.field_address.setValue(self.base_address)
            if self.file_content_gfx.sceneRect().width() != 0: # disallow zero div
                self.file_content_gfx.fitInView()
            #print(f"{len(self.rom.save()):08X}")
        elif mode == "Font":
            pass

    def save_filecontent(self): #Save to virtual ROM
        file_id = int(self.tree.currentItem().text(0))
        if self.fileDisplayRaw == False:
            if self.fileDisplayState == "English dialogue": # if english text
                if self.dropdown_textindex.isEnabled():
                    self.fileEdited_object.text_list[self.dropdown_textindex.currentIndex()] = self.file_content_text.toPlainText()
                    #dialog.text_id_list = 
                    self.rom.files[file_id] = self.fileEdited_object.toBytes()
                else:
                    self.rom.files[file_id][self.relative_address:self.relative_address+0xFFFF] = lib.dialogue.DialogueFile.textToBin(self.file_content_text.toPlainText())
            elif self.fileDisplayState == "Graphics":
                save_data = lib.datconv.qtToBin(self.file_content_gfx._graphic.pixmap().toImage(),
                                                algorithm=list(lib.datconv.CompressionAlgorithmEnum)[self.dropdown_gfx_depth.currentIndex()],
                                                tileWidth=self.tile_width, tileHeight=self.tile_height)
                w.rom.files[file_id][self.relative_address:self.relative_address+len(save_data)] = save_data
                if self.dropdown_gfx_palette.currentIndex() == -1: # if palette from ROM
                    header_index = self.dropdown_gfx_subindex.currentIndex()
                    if isinstance(self.fileEdited_object, lib.graphic.File):
                        section = lib.graphic.GraphicSection.fromParent(self.fileEdited_object, self.dropdown_gfx_index.currentIndex())
                    elif isinstance(self.fileEdited_object, lib.graphic.GraphicSection):
                        section = self.fileEdited_object
                    offset = section.graphics[header_index].offset_start+0xc+section.graphics[header_index].palette_offset
                    w.rom.files[file_id][offset:offset+section.graphics[header_index].palette_size] = lib.datconv.ARGB32_to_BGR15(self.gfx_palette[section.graphics[header_index].unk13 & 0xf0:]) # save to ROM
            elif self.fileDisplayState == "OAM":
                if self.tabs_oam.currentWidget()==self.page_oam_frames:
                    if -1 in [self.dropdown_oam_entry.currentIndex(),  self.dropdown_oam_objFrame.currentIndex(),
                              self.dropdown_oam_obj.currentIndex()]:
                        print("no valid object to save!")
                        return
                    section = self.fileEdited_object.oamsec
                    frame = self.fileEdited_object.frame
                    save_data = bytearray()
                    for obj_index in range(len(self.fileEdited_object.objs)):
                        offset = section.frameTable_offset + frame[0] + obj_index*0x04
                        obj = lib.oam.Object(section.data[offset:offset+0x04])
                        if obj_index == self.dropdown_oam_obj.currentIndex(): # current changes
                            obj.tileId = self.field_objTileId.value()
                            obj.tileId_add = self.field_objTileId.value() & 0x300
                            obj.flip_h = self.checkbox_objFlipH.isChecked()
                            obj.flip_v = self.checkbox_objFlipV.isChecked()
                            obj.sizeIndex = self.slider_objSizeIndex.sl.value()
                            obj.shape = self.buttonGroup_oam_objShape.checkedId()
                            obj.x = self.field_objX.value()
                            obj.y = self.field_objY.value()
                        else: # cached changes
                            obj = self.fileEdited_object.objs[obj_index]
                        save_data += obj.toBytes()
                    offset2 = section.offset_start + section.frameTable_offset + frame[0]
                    offset2_end = offset2+frame[1]*0x04
                    w.rom.files[file_id][offset2:offset2_end] = save_data
                    objCountDelta = len(self.fileEdited_object.objs) - frame[1]
                    if objCountDelta != 0:
                        offset3 = section.offset_start + section.frameTable_offset + self.dropdown_oam_objFrame.currentIndex()*0x04
                        w.rom.files[file_id][offset3+0x02:offset3+0x03] = int.to_bytes(len(self.fileEdited_object.objs), 1, 'little') # update header obj count
                        for i in range(offset3+0x04, section.offset_start + section.frameTable_offset + section.frameTable_size, 0x04):
                            #print(objCountDelta*0x04, w.rom.files[file_id][i:i+0x02].hex())
                            w.rom.files[file_id][i:i+0x02] = int.to_bytes(int.from_bytes(w.rom.files[file_id][i:i+0x02], 'little')+objCountDelta*0x04, 2, 'little') # update header obj offset
                        for i in range(1, len(section.header_items)): # section pointers from anim
                                section.header_items[i] += objCountDelta*0x04
                        w.rom.files[file_id][section.offset_start:section.offset_start+section.header_size] = section.headerToBytes() # update section header pointers
                        for i in range(self.dropdown_oam_entry.currentIndex()+1, len(self.fileEdited_object.address_list)): # file
                            self.fileEdited_object.address_list[i][0] += objCountDelta*0x04
                        self.fileEdited_object.fileSize += objCountDelta*0x04
                        w.rom.files[file_id][:self.fileEdited_object.header_size] = self.fileEdited_object.headerToBytes() # update file header pointers
                elif self.tabs_oam.currentWidget()==self.page_oam_anims:
                    if -1 in [self.dropdown_oam_entry.currentIndex(), self.dropdown_oam_anim.currentIndex(),
                            self.dropdown_oam_animFrame.currentIndex()]:
                        print("no valid animation data to save!")
                        return
                    section = self.fileEdited_object.oamsec
                    anim = self.fileEdited_object.oamsec_anim
                    isDurationfix = self.dropdown_oam_animFrame.currentIndex() > 0 and self.field_oam_animFrameDuration.value() >= 0xFE
                    if isDurationfix:
                        if self.field_oam_animFrameDuration.value() == 0xFE:
                            self.field_oam_animFrameId.setValue(self.dropdown_oam_animFrame.currentIndex())
                        elif self.field_oam_animFrameDuration.value() == 0xFF:
                            self.field_oam_animFrameDuration.setValue(0)
                    anim.isLooping = self.checkbox_oam_animLoop.isChecked()
                    anim.loopStart = self.field_oam_animLoopStart.value()
                    anim.frames[self.dropdown_oam_animFrame.currentIndex()] = [
                        self.field_oam_animFrameId.value(),
                        self.field_oam_animFrameDuration.value()
                    ]
                    if isDurationfix:
                        print(f"while saving, special duration was found in frame {self.dropdown_oam_animFrame.currentIndex()} of animation and frame was modified to match expected duration")
                    save_data = anim.toBytes()
                    save_offset =  self.fileEdited_object.oamsec.offset_start+self.fileEdited_object.oamsec.animTable_offset+anim.frames_offset
                    save_offset_end = save_offset+anim.oldFrameCount*0x02
                    print(save_data.hex(), w.rom.files[file_id][save_offset:save_offset_end].hex())
                    w.rom.files[file_id][save_offset:save_offset_end] = save_data
                    frameCountDelta = len(anim.frames) - anim.oldFrameCount
                    if frameCountDelta != 0:
                        offset = section.offset_start + section.animTable_offset + self.dropdown_oam_anim.currentIndex()*0x02
                        for i in range(offset+0x02, section.offset_start + section.animTable_offset + section.animTable_size, 0x02):
                            #print(frameCountDelta*0x02, w.rom.files[file_id][i:i+0x02].hex())
                            w.rom.files[file_id][i:i+0x02] = int.to_bytes(int.from_bytes(w.rom.files[file_id][i:i+0x02], 'little')+frameCountDelta*0x02, 2, 'little') # update header obj offset
                        for i in range(2, len(section.header_items)): # section pointers from palette
                                section.header_items[i] += frameCountDelta*0x02
                        w.rom.files[file_id][section.offset_start:section.offset_start+section.header_size] = section.headerToBytes() # update section header pointers
                        for i in range(self.dropdown_oam_entry.currentIndex()+1, len(self.fileEdited_object.address_list)): # file
                            self.fileEdited_object.address_list[i][0] += frameCountDelta*0x02
                        self.fileEdited_object.fileSize += frameCountDelta*0x02
                        w.rom.files[file_id][:self.fileEdited_object.header_size] = self.fileEdited_object.headerToBytes() # update file header pointers
                    anim.oldFrameCount = len(anim.frames)
                # update data of oamsec
                self.fileEdited_object.oamsec = lib.oam.OAMSection(self.fileEdited_object, self.dropdown_oam_entry.currentIndex())
            elif self.fileDisplayState == "Palette Animation":
                self.fileEdited_object.anims[self.dropdown_panm_entry.currentIndex()].frames[self.dropdown_panm_frame.currentIndex()]\
                                = [self.field_panm_frameId.value(), self.field_panm_frameDuration.value()]
                self.fileEdited_object.anims[self.dropdown_panm_entry.currentIndex()].isLooping = self.checkbox_panm_loop.isChecked()
                self.fileEdited_object.anims[self.dropdown_panm_entry.currentIndex()].loopStart = self.field_panm_loopStart.value()
                self.fileEdited_object.palettes[self.dropdown_panm_entry.currentIndex()].colorSlot0 = self.field_panm_colorSlot0.value()
                self.fileEdited_object.palettes[self.dropdown_panm_entry.currentIndex()].colorSlot1 = self.field_panm_colorSlot1.value()

                for colorset_index in range(len(self.fileEdited_object.palettes[self.dropdown_panm_entry.currentIndex()].colorTable)):
                    self.fileEdited_object.palettes[self.dropdown_panm_entry.currentIndex()].colorTable[colorset_index] = \
                        self.gfx_palette[colorset_index*2:colorset_index*2+2]
                save_data = self.fileEdited_object.toBytes()
                #print(w.rom.files[file_id] == save_data)
                w.rom.files[file_id][:] = save_data

            elif self.fileDisplayState == "Font":
                save_data = lib.datconv.qtToBin(self.file_content_gfx._graphic.pixmap().toImage(),
                                                algorithm=lib.datconv.CompressionAlgorithmEnum.ONEBPP,
                                                tileWidth=self.tile_width, tileHeight=self.tile_height)
                w.rom.files[file_id][self.relative_address:self.relative_address+len(save_data)] = save_data
                w.rom.files[file_id][0x00:0x02] = bytearray(int.to_bytes(int(self.field_font_width.value()), 2, "little"))
                w.rom.files[file_id][0x02:0x04] = bytearray(int.to_bytes(int(self.field_font_height.value()), 2, "little"))
                i_space = self.field_font_width.value()*self.field_font_height.value()/8
                w.rom.files[file_id][0x04:0x08] = bytearray(int.to_bytes(int(i_space), 4, "little"))
                if i_space:
                    w.rom.files[file_id][0x08:0x0C] = bytearray(int.to_bytes(int(self.field_font_size.value()/self.field_font_width.value()*self.field_font_height.value()/8), 4, "little"))
                else:
                    w.rom.files[file_id][0x08:0x0C] = bytearray(int.to_bytes(int(0), 4, "little"))
                w.rom.files[file_id][0x0C:0x10] = bytearray(int.to_bytes(int(self.field_font_size.value()), 4, "little"))
            elif self.fileDisplayState == "VX":
                w.rom.files[file_id][0x04:0x08] = bytearray(int.to_bytes(int(self.field_vxHeader_length.value()), 4, "little"))
                w.rom.files[file_id][0x08:0x0C] = bytearray(int.to_bytes(int(self.field_vxHeader_width.value()), 4, "little"))
                w.rom.files[file_id][0x0C:0x10] = bytearray(int.to_bytes(int(self.field_vxHeader_height.value()), 4, "little"))
                w.rom.files[file_id][0x10:0x14] = bytearray(int.to_bytes(int(self.field_vxHeader_framerate.value()*0x10000), 4, "little")) #convert float to 16.16
                w.rom.files[file_id][0x14:0x18] = bytearray(int.to_bytes(int(self.field_vxHeader_quantizer.value()), 4, "little"))
                w.rom.files[file_id][0x18:0x1C] = bytearray(int.to_bytes(int(self.field_vxHeader_sampleRate.value()), 4, "little"))
                w.rom.files[file_id][0x1C:0x20] = bytearray(int.to_bytes(int(self.field_vxHeader_streamCount.value()), 4, "little"))
                w.rom.files[file_id][0x20:0x24] = bytearray(int.to_bytes(int(self.field_vxHeader_frameSizeMax.value()), 4, "little"))
                w.rom.files[file_id][0x24:0x28] = bytearray(int.to_bytes(int(self.field_vxHeader_audioExtraDataOffset.value()), 4, "little"))
                w.rom.files[file_id][0x28:0x2C] = bytearray(int.to_bytes(int(self.field_vxHeader_seekTableOffset.value()), 4, "little"))
                w.rom.files[file_id][0x2C:0x30] = bytearray(int.to_bytes(int(self.field_vxHeader_seekTableEntryCount.value()), 4, "little"))
            elif self.fileDisplayState == "Sound":
                return
        else:
            save_data = bytearray.fromhex(lib.datconv.strSetAlnum(self.file_content_text.toPlainText(), 16, True)) # force to alphanumeric for bytearray conversion
            w.rom.files[file_id][self.relative_address:self.relative_address+len(save_data)] = save_data
        #print(type(w.rom.files[file_id]))
        print("file changes saved")
        # fat is only recalculated when entire rom is saved, so it keeps outdated values
        self.button_file_save.setDisabled(True)
    
    def save_level(self):
        self.button_level_save.setDisabled(True)
        
        # find level file in rom
        fileID = self.rom.filenames.idOf(self.dropdown_level_area.currentText()+".bin")
        if hasattr(self.levelEdited_object, "level"):
            level_bin = bytearray(self.levelEdited_object.level.toBytes())
        else:
            level_bin = self.levelEdited_object.data[self.levelEdited_object.level_offset_rom:self.levelEdited_object.gfx_offset_rom]
        level_bin += bytearray((-len(level_bin)) & 3) # 4-byte padding
        gfx_bin = self.levelEdited_object.data[self.levelEdited_object.gfx_offset_rom:self.levelEdited_object.pal_offset_rom]
        gfx_bin += bytearray((-len(gfx_bin)) & 3)
        if self.levelEdited_object.entryCount == 7:
            pal_bin = self.levelEdited_object.data[self.levelEdited_object.pal_offset_rom:self.levelEdited_object.address_list[3][0]]
            pal_bin += bytearray((-len(pal_bin)) & 3)
            bin_03 = self.levelEdited_object.data[self.levelEdited_object.address_list[3][0]:self.levelEdited_object.address_list[4][0]]
            #bin_03 = ndspy.lz10.compress(bytearray(4))
            bin_03 += bytearray((-len(bin_03)) & 3)
            bin_04 = self.levelEdited_object.data[self.levelEdited_object.address_list[4][0]:self.levelEdited_object.address_list[5][0]]
            bin_04 += bytearray((-len(bin_04)) & 3)
            bin_05 = self.levelEdited_object.data[self.levelEdited_object.address_list[5][0]:self.levelEdited_object.address_list[6][0]]
            bin_05 += bytearray((-len(bin_05)) & 3)
            if hasattr(self.levelEdited_object, "level_radar"):
                bin_06 = bytearray(self.levelEdited_object.level_radar.toBytes())
            else:
                bin_06 = self.levelEdited_object.data[self.levelEdited_object.address_list[6][0]:]
            bin_06 += bytearray((-len(bin_06)) & 3)

        if self.levelEdited_object.entryCount == 7:
            self.rom.files[fileID][self.levelEdited_object.address_list[6][0]:] = bin_06
            self.rom.files[fileID][self.levelEdited_object.address_list[5][0]:self.levelEdited_object.address_list[6][0]] = bin_05
            self.rom.files[fileID][self.levelEdited_object.address_list[4][0]:self.levelEdited_object.address_list[5][0]] = bin_04
            self.rom.files[fileID][self.levelEdited_object.address_list[3][0]:self.levelEdited_object.address_list[4][0]] = bin_03
            self.rom.files[fileID][self.levelEdited_object.pal_offset_rom:self.levelEdited_object.address_list[3][0]] = pal_bin
        self.rom.files[fileID][self.levelEdited_object.gfx_offset_rom:self.levelEdited_object.pal_offset_rom] = gfx_bin
        self.rom.files[fileID][self.levelEdited_object.level_offset_rom:self.levelEdited_object.gfx_offset_rom] = level_bin

        self.levelEdited_object.gfx_offset_rom = self.levelEdited_object.level_offset_rom + len(level_bin)
        self.levelEdited_object.pal_offset_rom = self.levelEdited_object.gfx_offset_rom + len(gfx_bin)
        if self.levelEdited_object.entryCount == 7:
            self.levelEdited_object.address_list[3][0] = self.levelEdited_object.pal_offset_rom + len(pal_bin)
            self.levelEdited_object.address_list[4][0] = self.levelEdited_object.address_list[3][0] + len(bin_03)
            self.levelEdited_object.address_list[5][0] = self.levelEdited_object.address_list[4][0] + len(bin_04)
            self.levelEdited_object.address_list[6][0] = self.levelEdited_object.address_list[5][0] + len(bin_05)
        self.levelEdited_object.fileSize = len(self.rom.files[fileID])
        self.rom.files[fileID][:self.levelEdited_object.level_offset_rom] = self.levelEdited_object.headerToBytes()
        print(f"Level data {self.dropdown_level_area.currentText()} has been saved!")
        self.levelEdited_object = lib.level.File(self.rom.files[fileID]) # update data
        #print(f"{len(self.rom.files[fileID][self.levelEdited_object.level_offset_rom:self.levelEdited_object.gfx_offset_rom])} {self.levelEdited_object.level_offset_rom}")
        #print(f"{len(self.rom.files[fileID][self.levelEdited_object.gfx_offset_rom:self.levelEdited_object.pal_offset_rom])} {self.levelEdited_object.gfx_offset_rom}")
        #print(f"{len(self.rom.files[fileID][self.levelEdited_object.pal_offset_rom:])} {self.levelEdited_object.pal_offset_rom}")

    def patch_game(self):# Currently a workaround to having no easy way of writing directly to any address in the ndspy rom object
        #print("call")
        self.tree_patches.blockSignals(True)
        rom_patched = bytearray(self.rom.save()) # Create temporary ROM to write patch to
        patch_list = []
        for patch in lib.patchdat.GameEnum[self.rom.name.decode().replace(" ", "_")].value[1]: # create a patch list with a consistent format
            if isinstance(patch[2], list):
                patch_list.append(['N/A', patch[0], patch[1], 'N/A', 'N/A'])
                for subPatch in patch:
                    if isinstance(subPatch, list):
                        patch_list.append([subPatch[0], subPatch[1], "Patch Segment", subPatch[2], subPatch[3]])
            else:
                patch_list.append(patch)

        tree_list = self.tree_patches.findItems("", QtCore.Qt.MatchFlag.MatchContains | QtCore.Qt.MatchFlag.MatchRecursive)

        for item_i, item in enumerate(tree_list):# Iterate through patch groups
            if item.childCount() != 0:
                if item.checkState(0) != self.tree_patches_checkboxes[item_i]: # if checkstate changed
                    for child_i in range(item.childCount()): # update children
                        item.child(child_i).setCheckState(0, item.checkState(0))
                else: # update according to children
                    subPatchMatches = 0
                    for child_i in range(item.childCount()):
                        if item.child(child_i).checkState(0) == QtCore.Qt.CheckState.Checked:
                            subPatchMatches += 1
                    if subPatchMatches == item.childCount(): # Check for already applied patches
                            item.setCheckState(0, QtCore.Qt.CheckState.Checked)
                    elif subPatchMatches > 0:
                        item.setCheckState(0, QtCore.Qt.CheckState.PartiallyChecked)
                    else:
                        item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)

        for item_i, item in enumerate(tree_list):# Go through unchecked ones first
            if (item.checkState(0) == QtCore.Qt.CheckState.Unchecked):
                # Revert patch
                if item.childCount() == 0: # if not a patch group
                    newData = bytes.fromhex(patch_list[item_i][3])
                    rom_patched[patch_list[item_i][0]:patch_list[item_i][0]+len(newData)] = newData # write og data
                        
        for item_i, item in enumerate(tree_list):# Then through active patches
            if (item.checkState(0) == QtCore.Qt.CheckState.Checked):
                # Apply patch
                if item.childCount() == 0: # if not a patch group\
                    newData = patch_list[item_i][4]
                    for s in range(len(patch_list[item_i][4])):
                        if newData[s] == "-":
                            newData = newData[:s] + patch_list[item_i][3][s] + newData[s+1:] # replace '-' with og data
                    newData = bytes.fromhex(newData)
                    rom_patched[patch_list[item_i][0]:patch_list[item_i][0]+len(newData)] = newData # write patch data

        for item_i, item in enumerate(tree_list):# Iterate through all patches
            self.tree_patches_checkboxes[item_i] = item.checkState(0) #and update checkbox state list

        self.rom = ndspy.rom.NintendoDSRom(rom_patched)# update the editor with patched ROM
        self.tree_patches.blockSignals(False)

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()

# Draw contents of tile viewer
def draw_tilesQImage_fromBytes(view: lib.widget.GFXView, data: bytearray, algorithm=lib.datconv.CompressionAlgorithmEnum.ONEBPP,  grid: bool=True):
    #print("draw")
    tile_size = int((w.tile_width*w.tile_height)*algorithm.depth/8) # size in bytes
    gfx = lib.datconv.binToQt(data[:tile_size*w.tiles_per_row*w.tiles_per_column],
                              palette=w.gfx_palette, algorithm=algorithm,
                              tilesPerRow=w.tiles_per_row, tilesPerColumn=w.tiles_per_column,
                              tileWidth=w.tile_width, tileHeight=w.tile_height)
    view._graphic.setPixmap(QtGui.QPixmap.fromImage(gfx, QtCore.Qt.ImageConversionFlag.NoFormatConversion)) # overwrite current canvas with new one
    if grid:
        view.createGrid(w.tile_width, w.tile_height)

def extract(data: bytes, name="", path="", format="", compress=0):
    ext = ""
    if name == "":
        print("Error, tried to extract nameless file!")
        return
    if compress == 2:
        try:
            data = ndspy.lz10.decompress(data)
        except TypeError as e:
            print(e)
            QtWidgets.QMessageBox.critical(
            w,
            "Decompression Failed",
            str(e)
            )
            print("Aborted file extraction.")
            return

    print("file " + name + ": " + format)
    print(data[0x65:0xc5])

    # create a copy of the file outside ROM
    if format == "" or format == "Raw":
        ext = ".bin"
    else:
        if format == "English dialogue":
            ext = ".txt"
            try: # create multiple text files
                text_list = lib.dialogue.DialogueFile(data).text_list
                data = [""]*len(text_list)
                for text_i, text in enumerate(text_list):
                    data[text_i] = bytes(text, "utf-8")
            except AssertionError: # not a real dialogue file
                data = bytes(lib.dialogue.DialogueFile.binToText(data), "utf-8")
        elif format == "VX":
            ext = ".vx" # even if it is a folder, use extension to know what it contains when importing
            act = lib.act.ActImagine()
            load_vx_iter = act.load_vx(data)
            w.progressShow()
            for i, _ in enumerate(load_vx_iter):
                w.progressUpdate(int(((i+1)/act.frames_qty)*100), "Loading VX file")
            export_vx_iter = act.export_vxfolder(os.path.join(path + "/" + name + ext))
            for i, _ in enumerate(export_vx_iter):
                w.progressUpdate(int(((i+1)/act.frames_qty)*100), "Exporting VX folder")
            w.progressHide()
            return
        else:
            print("could not find method for converting to specified format.")
            return
    if compress == 1:
        data = ndspy.lz10.compress(data)

    print(os.path.join(path + "/" + name.split(".")[0] + ext))
    if isinstance(data, (bytes, bytearray)): # one file
        with open(os.path.join(path + "/" + name.split(".")[0] + ext), 'wb') as f:
            f.write(data)
    else: # list of bytes
        for subdata_i, subdata in enumerate(data):
            with open(os.path.join(path + "/" + name.split(".")[0] + "_" + str(subdata_i) + ext), 'wb') as f:
                f.write(subdata)
    print("File extracted!")
#run the app
app.exec()
# After execution
w.firstLaunch = False
lib.ini_rw.write(w)
if os.path.exists(w.temp_path) and w.romToEdit_name != "":
    try:
        os.remove(w.temp_path) # delete temporary ROM
    except OSError as error:
        print(error)