import PyQt6
import PyQt6.QtGui, PyQt6.QtWidgets
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
        self.displayConvertedFile = True # Whether or not fileToEdit should be shown in raw bin format or in readable format
        self.resize(self.window_width, self.window_height)
        self.UiComponents()
        self.show()
    
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

        self.importAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_blue-document-import.png'), '&Import...', self)        
        self.importAction.setShortcut('Ctrl+I')
        self.importAction.setStatusTip('import file in binary or converted format')
        self.importAction.triggered.connect(self.importCall)
        self.importAction.setDisabled(True)

        self.settingsAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_gear.png'), '&Settings', self)
        self.settingsAction.setStatusTip('Settings')
        self.settingsAction.triggered.connect(self.settingsCall)

        self.exitAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_door.png'), '&Exit', self)
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.exitCall)

        self.menu_bar = self.menuBar()
        self.fileMenu = self.menu_bar.addMenu('&File')
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.exportAction)
        self.fileMenu.addAction(self.importAction)
        self.fileMenu.addAction(self.settingsAction)
        self.fileMenu.addAction(self.exitAction)

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
            w.importAction.setDisabled(False)
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

    def importCall(self):
        if hasattr(w.rom, "name"):
            fname = PyQt6.QtWidgets.QFileDialog.getOpenFileName(
                self,
                "Import File",
                "",
                "All Files (*)",
            )
            if not fname == ("", ""): # if file you're trying to open is not none
                print("file imported")

    def settingsCall(self):
        print("settings")
    
    def exitCall(self):
        self.close()
    
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
            if self.displayConvertedFile == True:
                if self.tree.currentItem().text(1).find("talk") != -1 and self.tree.currentItem().text(1).find("en") != -1: # if english text
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