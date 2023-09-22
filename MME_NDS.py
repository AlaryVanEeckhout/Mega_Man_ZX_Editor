import PyQt6
import PyQt6.QtGui, PyQt6.QtWidgets, PyQt6.QtCore
import sys, os
import ndspy
import ndspy.rom
import dataconverter

class MainWindow(PyQt6.QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.window_width = 1024
        self.window_height = 720
        self.setWindowIcon(PyQt6.QtGui.QIcon('icon_biometals-creation.png'))
        self.setWindowTitle("Mega Man ZX Editor")
        self.rom = ndspy.rom.NintendoDSRom
        self.romToEdit_name = ''
        self.romToEdit_ext = ''
        self.fileToEdit_name = ''
        self.fileDisplayRaw = False # Display file in 'raw'(bin) format. Else, diplayed in readable format
        self.fileDisplayMode = "Adapt" # Modes: Adapt, Binary, English dialogue, Japanese dialogue, Sound, Movie, Code
        self.resize(self.window_width, self.window_height)
        self.UiComponents()
        self.show()

    def toggle_widget_icon(self, widget, checkedicon, uncheckedicon):
        if widget.isChecked():
            widget.setIcon(checkedicon)
        else:
            widget.setIcon(uncheckedicon)
    
    def UiComponents(self):
        # Menus
        self.openAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_folder-horizontal-open.png'), '&Open', self)        
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.setStatusTip('Open ROM')
        self.openAction.triggered.connect(self.openCall)

        self.exportAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_blueprint--arrow.png'), '&Export...', self)        
        self.exportAction.setShortcut('Ctrl+E')
        self.exportAction.setStatusTip('Export file in binary or converted format')
        self.exportAction.triggered.connect(self.exportCall)
        self.exportAction.setDisabled(True)

        self.replaceAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_blue-document-import.png'), '&Replace', self)        
        self.replaceAction.setShortcut('Ctrl+I')
        self.replaceAction.setStatusTip('replace file in binary or converted format')
        self.replaceAction.triggered.connect(self.replaceCall)

        self.insertfileAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_blue-document-import.png'), '&Insert', self)        
        self.insertfileAction.setShortcut('Ctrl+I')
        self.insertfileAction.setStatusTip('insert file in binary or converted format')
        self.insertfileAction.triggered.connect(self.insertfileCall)

        self.settingsAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_gear.png'), '&Settings', self)
        self.settingsAction.setStatusTip('Settings')
        self.settingsAction.triggered.connect(self.settingsCall)

        self.exitAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_door.png'), '&Exit', self)
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.exitCall)

        self.menu_bar = self.menuBar()
        self.fileMenu = self.menu_bar.addMenu('&File')
        self.fileMenu.addActions([self.openAction, self.exportAction])
        self.importSubmenu = self.fileMenu.addMenu('&Import...')
        self.importSubmenu.setIcon(PyQt6.QtGui.QIcon('icon_blue-document-import.png'))
        self.importSubmenu.addActions([self.replaceAction, self.insertfileAction])
        self.importSubmenu.setDisabled(True)
        self.fileMenu.addActions([self.settingsAction, self.exitAction])

        self.displayRawAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_brain.png'), '&Converted formats', self)
        self.displayRawAction.setStatusTip('Displays files in a readable format instead of raw format.')
        self.displayRawAction.setCheckable(True)
        self.displayRawAction.setChecked(True)
        self.displayRawAction.triggered.connect(self.display_format_toggleCall)

        self.viewAdaptAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_document-node.png'), '&Adapt', self)
        self.viewAdaptAction.setStatusTip('Files will be decrypted on a case per case basis.')
        self.viewAdaptAction.setCheckable(True)
        self.viewAdaptAction.setChecked(True)
        self.viewAdaptAction.triggered.connect(self.display_format_adapt_Call)

        self.viewEntextAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_document-text.png'), '&English Text', self)
        self.viewEntextAction.setStatusTip('Files will be decrypted as english dialogues.')
        self.viewEntextAction.setCheckable(True)
        self.viewEntextAction.triggered.connect(self.display_format_endialog_Call)

        self.viewFormatsGroup = PyQt6.QtGui.QActionGroup(self) #group for mutually exclusive togglable items
        self.viewFormatsGroup.addAction(self.viewAdaptAction)
        self.viewFormatsGroup.addAction(self.viewEntextAction)

        self.viewMenu = self.menu_bar.addMenu('&View')
        self.viewMenu.addAction(self.displayRawAction)
        self.displayFormatSubmenu = self.viewMenu.addMenu(PyQt6.QtGui.QIcon('icon_document-convert.png'), '&Set edit mode...')
        self.displayFormatSubmenu.addActions([self.viewAdaptAction, self.viewEntextAction])

        #Toolbar
        self.toolbar = PyQt6.QtWidgets.QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)

        self.button_save = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_disk.png'), "Save to ROM", self)
        self.button_save.setStatusTip("Save changes to the ROM")
        self.button_save.triggered.connect(self.saveCall)
        self.toolbar.addAction(self.button_save)

        #ROM-related
        self.tree = PyQt6.QtWidgets.QTreeWidget(self)
        self.tree.move(0, self.menu_bar.rect().bottom() + 45)
        self.tree.resize(450, 625)
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["File ID", "Name", "Type"])
        self.treeUpdate()
        self.tree.itemSelectionChanged.connect(self.treeCall)

        self.file_content = PyQt6.QtWidgets.QTextEdit(self)
        self.file_content.setGeometry(475, self.menu_bar.rect().bottom() + 100, 500, 500)
        #button = PyQt6.QtWidgets.QPushButton("My simple app.\n nl\n nl", self)
        #button.setToolTip("tooltip")
        #button.setGeometry(650, 100, 100, 50)
        #button.pressed.connect(self.close)

        self.setStatusBar(PyQt6.QtWidgets.QStatusBar(self))

    def set_dialog_button_name(self, dialog, oldtext, newtext):
        for btn in dialog.findChildren(PyQt6.QtWidgets.QPushButton):
            if btn.text() == self.tr(oldtext):
                PyQt6.QtCore.QTimer.singleShot(0, lambda btn=btn: btn.setText(newtext))
    
    def openCall(self):
        fname = PyQt6.QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "NDS Files (*.nds *.srl);; All Files (*)",
        )
        if not fname == ("", ""): # if file you're trying to open is not none
            w.romToEdit_name = fname[0].split("/")[len(fname[0].split("/")) - 1].split(".")[0]
            w.romToEdit_ext = "." + fname[0].split("/")[len(fname[0].split("/")) - 1].split(".")[1]
            w.rom = ndspy.rom.NintendoDSRom.fromFile(w.romToEdit_name + w.romToEdit_ext)
            w.setWindowTitle("Mega Man ZX Editor" + " (" + w.romToEdit_name + w.romToEdit_ext + ")")
            print(w.rom.filenames)
            w.importSubmenu.setDisabled(False)
            w.treeUpdate()

    def exportCall(self):
        if self.fileToEdit_name != '':
            if self.fileToEdit_name.find(".Folder") == -1: # if file
                extract(int(w.tree.currentItem().text(0)), fileToEdit_name=str(w.tree.currentItem().text(1) + "." + w.tree.currentItem().text(2)))
            else: # if folder
                if os.path.exists(w.fileToEdit_name.removesuffix(".Folder")) == False:
                    os.makedirs(w.fileToEdit_name.removesuffix(".Folder"))
                print(w.tree.currentItem().childCount() - 1)
                for i in range(w.tree.currentItem().childCount()):
                    print(w.tree.currentItem().child(i).text(0))
                    extract(int(w.tree.currentItem().child(i).text(0)))#, w.fileToEdit_name.replace(".Folder", "/")
                    #str(w.tree.currentItem().child(i).text(1) + "." + w.tree.currentItem().child(i).text(2)), 
        else:
            print("no file to extract!")

    def replaceCall(self):
        if hasattr(w.rom, "name"):
            import_dialog = PyQt6.QtWidgets.QFileDialog(
                self,
                "Import File",
                "",
                "All Files (*)",
                options=PyQt6.QtWidgets.QFileDialog.Option.DontUseNativeDialog,
                )
            self.set_dialog_button_name(import_dialog, "&Open", "Import")
            import_dialog.findChild(PyQt6.QtWidgets.QTreeView).selectionModel().currentChanged.connect(
            lambda: self.set_dialog_button_name(import_dialog, "&Open", "Import")
            )
            #import_dialog.setAcceptMode(PyQt6.QtWidgets.QFileDialog.AcceptMode.AcceptSave)
            fname = import_dialog.exec()
            if not fname == ("", ""): # if file you're trying to open is not none
                print("file imported")

    def insertfileCall(self):
        if hasattr(w.rom, "name"):
            import_dialog = PyQt6.QtWidgets.QFileDialog(
                self,
                "Import File",
                "",
                "All Files (*)",
                options=PyQt6.QtWidgets.QFileDialog.Option.DontUseNativeDialog,
                )
            self.set_dialog_button_name(import_dialog, "&Open", "Import")
            import_dialog.findChild(PyQt6.QtWidgets.QTreeView).selectionModel().currentChanged.connect(
            lambda: self.set_dialog_button_name(import_dialog, "&Open", "Import")
            )
            fname = import_dialog.exec()
            if not fname == ("", ""): # if file you're trying to open is not none
                print("file imported")

    def settingsCall(self):
        print("settings")
    
    def exitCall(self):
        self.close()
    
    def display_format_toggleCall(self):
        if self.fileDisplayRaw == False:
            self.fileDisplayRaw = True
            self.displayFormatSubmenu.setDisabled(True)
        else:
            self.fileDisplayRaw = False
            self.displayFormatSubmenu.setDisabled(False)
        self.toggle_widget_icon(self.displayRawAction, PyQt6.QtGui.QIcon('icon_brain.png'), PyQt6.QtGui.QIcon('icon_document-binary.png'))

    def display_format_adapt_Call(self):
        self.fileDisplayMode = "Adapt"

    def display_format_endialog_Call(self):
        self.fileDisplayMode = "English dialogue"
    
    def saveCall(self):
        print("save")

    def treeUpdate(self):
        tree_files = []
        try: # convert NDS Py filenames to QTreeWidgetItems
            tree_folder = []
            for f in str(self.rom.filenames).split("\n"):
                if f.find("/") == -1: # if file
                    if f.find("    ") != -1: # if contents of folder
                        tree_folder[f.count("    ") - 1].addChild(PyQt6.QtWidgets.QTreeWidgetItem([f.split(" ")[0], f.split(" ")[-1].split(".")[0], f.split(".")[-1]]))
                    else:
                        tree_files.append(PyQt6.QtWidgets.QTreeWidgetItem([f.split(" ")[0], f.split(" ")[-1].split(".")[0], f.split(".")[-1]]))
                else: # if folder
                    if f.count("    ") < len(tree_folder):
                        tree_folder[f.count("    ")] = PyQt6.QtWidgets.QTreeWidgetItem([f.split(" ")[0], f.split(" ")[-1].removesuffix("/"), "Folder"])
                    else:
                        tree_folder.append(PyQt6.QtWidgets.QTreeWidgetItem([f.split(" ")[0], f.split(" ")[-1].removesuffix("/"), "Folder"]))
                    if f.find("    ") == -1:
                        tree_files.append(tree_folder[f.count("    ")])
                    else:
                        tree_folder[f.count("    ") - 1].addChild(tree_folder[f.count("    ")])
        except Exception as e: # if failed, empty list
            tree_files = []
        self.tree.addTopLevelItems(tree_files)

    def treeCall(self):
        self.fileToEdit_name = str(self.tree.currentItem().text(1) + "." + self.tree.currentItem().text(2))
        if self.fileToEdit_name.find(".Folder") == -1:
            if self.fileDisplayRaw == False:
                if (self.fileDisplayMode == "English dialogue") or (self.fileDisplayMode == "Adapt" and self.tree.currentItem().text(1).find("talk") != -1 and self.tree.currentItem().text(1).find("en") != -1): # if english text
                    self.file_content.setText(dataconverter.convertdata_bin_to_text(self.rom.files[int(self.tree.currentItem().text(0))]))
                else:
                    self.file_content.setText(str(self.rom.files[int(self.tree.currentItem().text(0))]))
            else:
                self.file_content.setText(self.rom.files[int(self.tree.currentItem().text(0))].hex())
        else:
            self.file_content.setText("")
        self.exportAction.setDisabled(False)

app = PyQt6.QtWidgets.QApplication(sys.argv)
w = MainWindow()
def extract(fileToEdit_id, folder="", fileToEdit_name=""):
    fileToEdit = w.rom.files[fileToEdit_id]
    if fileToEdit_name == "":
        fileToEdit_name = w.rom.filenames[fileToEdit_id]
    print("file " + str(fileToEdit_id) + ": " + fileToEdit_name)
    print(fileToEdit[0x65:0xc5])

    # create a copy of the file
    with open(os.path.join(folder + fileToEdit_name), 'wb') as f:
        f.write(fileToEdit)
        print(os.path.join(folder + fileToEdit_name))
        print("File extracted!")
def savetorom(fileToEdit_name):
    with open(fileToEdit_name, 'rb') as f:
        fileEdited = f.read()

    w.rom.setFileByName(fileToEdit_name, fileEdited)
    w.rom.saveToFile(w.romToEdit_name + ' edited' + w.romToEdit_ext)
    print("ROM modifs saved!")
#run the app
app.exec()