import PyQt6
import PyQt6.QtGui, PyQt6.QtWidgets
import sys
import ndspy
import ndspy.rom

class MainWindow(PyQt6.QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.window_width = 1024
        self.window_height = 720
        self.setWindowIcon(PyQt6.QtGui.QIcon('icon_biometals-creation.png'))
        self.setWindowTitle("Mega Man ZX Editor")
        self.rom = None
        self.romToEdit_name = ''
        self.romToEdit_ext = ''
        self.resize(self.window_width, self.window_height)
        self.UiComponents()
        self.show()
    
    def UiComponents(self):
        # Menus
        openAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_folder-horizontal-open.png'), '&Open', self)        
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open ROM')
        openAction.triggered.connect(self.openCall)

        exportAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_blueprint--arrow.png'), '&Export...', self)        
        exportAction.setShortcut('Ctrl+E')
        exportAction.setStatusTip('Export file in binary or converted format')
        exportAction.triggered.connect(self.exportCall)

        settingsAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_gear.png'), '&Settings', self)
        settingsAction.setStatusTip('Settings')
        settingsAction.triggered.connect(self.settingsCall)

        exitAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_door.png'), '&Exit', self)
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exportAction)
        fileMenu.addAction(settingsAction)
        fileMenu.addAction(exitAction)

        #Toolbar
        toolbar = PyQt6.QtWidgets.QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        button_save = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_disk.png'), "Save to ROM", self)
        button_save.setStatusTip("Save changes to the ROM")
        button_save.triggered.connect(self.saveCall)
        toolbar.addAction(button_save)

        #ROM-related
        tree = PyQt6.QtWidgets.QTreeWidget(self)
        tree.move(0, menuBar.rect().bottom() + 50)
        tree.resize(450, 625)
        tree.setColumnCount(2)
        tree.setHeaderLabels(["Name", "Type"])
        try:
            data = {"Project A": [w.rom.filenames]}
        except:
            data = {"Project A": ["file_a.py", "file_a.txt", "something.xls"],
            "Project B": ["file_b.csv", "photo.jpg"],
            "Project C": []}
        items = []
        for key, values in data.items():
            item = PyQt6.QtWidgets.QTreeWidgetItem([key])
            for value in values:
                ext = value.split(".")[-1].upper()
                child = PyQt6.QtWidgets.QTreeWidgetItem([value, ext])
                item.addChild(child)
            items.append(item)
        tree.insertTopLevelItems(0, items)

        button = PyQt6.QtWidgets.QPushButton("My simple app.\n nl\n nl", self)
        button.setToolTip("tooltip")
        button.setGeometry(650, 100, 100, 50)
        button.pressed.connect(self.close)

        self.setStatusBar(PyQt6.QtWidgets.QStatusBar(self))
    
    def openCall(self):
        fname = PyQt6.QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open File",
            "${HOME}",
            "NDS Files (*.nds *.srl);; All Files (*)",
        )
        print(fname)
        if not fname == ("", ""):
            openRom(fname)

    def exportCall(self):
        print("export")

    def settingsCall(self):
        print("settings")
    
    def exitCall(self):
        self.close()
    
    def saveCall(self):
        print("save")

app = PyQt6.QtWidgets.QApplication(sys.argv)
w = MainWindow()
# set game data as a variable
def openRom(name):
    w.romToEdit_name = name[0].split("/")[len(name[0].split("/")) - 1].split(".")[0]
    w.romToEdit_ext = "." + name[0].split("/")[len(name[0].split("/")) - 1].split(".")[1]
    w.rom = ndspy.rom.NintendoDSRom.fromFile(w.romToEdit_name + w.romToEdit_ext)
    w.setWindowTitle("Mega Man ZX Editor" + " (" + w.romToEdit_name + w.romToEdit_ext + ")")
    print(w.rom.filenames)
#fileToEdit_name = "talk_m01_en1.bin"
def extract(fileToEdit_name):
    fileToEdit = w.rom.getFileByName(fileToEdit_name)
    fileToEdit_id = w.rom.filenames[fileToEdit_name]
    print("file " + str(fileToEdit_id) + ": " + fileToEdit_name)
    print(fileToEdit[0x65:0xc5])

    # create a copy of the file
    with open(fileToEdit_name, 'wb') as f:
        f.write(fileToEdit)
        print("File extracted!")
def savetorom(fileToEdit_name):
    with open(fileToEdit_name, 'rb') as f:
        fileEdited = f.read()

    w.rom.setFileByName(fileToEdit_name, fileEdited)
    w.rom.saveToFile(w.romToEdit_name + ' edited' + w.romToEdit_ext)
    print("ROM modifs saved!")
#run the app
app.exec()