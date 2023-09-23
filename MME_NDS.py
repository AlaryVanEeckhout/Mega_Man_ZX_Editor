import PyQt6
import PyQt6.QtGui, PyQt6.QtWidgets, PyQt6.QtCore, PyQt6
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
        self.replaceAction.setShortcut('Ctrl+R')
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
        self.button_save.setDisabled(True)
        self.toolbar.addAction(self.button_save)

        #ROM-related
        self.tree = PyQt6.QtWidgets.QTreeWidget(self)
        self.tree.move(0, self.menu_bar.rect().bottom() + 45)
        self.tree.resize(450, 625)
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["File ID", "Name", "Type"])
        self.treeUpdate()
        self.tree.itemSelectionChanged.connect(self.treeCall)

        self.button_file_save = PyQt6.QtWidgets.QPushButton("Save file", self)
        self.button_file_save.setToolTip("save this file's changes")
        self.button_file_save.setGeometry(500, 70, 100, 50)
        self.button_file_save.pressed.connect(self.save_filetext)
        self.button_file_save.setDisabled(True)

        self.file_content = PyQt6.QtWidgets.QPlainTextEdit(self)
        self.file_content.setGeometry(475, self.menu_bar.rect().bottom() + 100, 500, 500)
        self.file_content.textChanged.connect(lambda: self.button_file_save.setDisabled(False))
        self.file_content.setDisabled(True)
        self.button_longfile = PyQt6.QtWidgets.QPushButton("Press this button to view file,\nbut be warned that this file is very big.\nTherefore if you choose to view it,\nit will take some time to load\nand the program will be unresponsive.\n\nAlternatively, you could export the file and open it in a hex editor", self)
        self.button_longfile.pressed.connect(lambda: self.button_longfile.hide())
        self.button_longfile.pressed.connect(lambda: print("will take a while"))
        self.button_longfile.pressed.connect(lambda: self.file_content.setDisabled(False))
        self.button_longfile.pressed.connect(lambda: self.file_content.setPlainText((self.rom.files[int(self.tree.currentItem().text(0))]).hex()))
        self.button_longfile.hide()

        self.setStatusBar(PyQt6.QtWidgets.QStatusBar(self))

    def set_dialog_button_name(self, dialog, oldtext, newtext):
        for btn in dialog.findChildren(PyQt6.QtWidgets.QPushButton):
            if btn.text() == self.tr(oldtext):
                PyQt6.QtCore.QTimer.singleShot(0, lambda btn=btn: btn.setText(newtext))
        dialog.findChild(PyQt6.QtWidgets.QTreeView).selectionModel().currentChanged.connect(
            lambda: self.set_dialog_button_name(dialog, "&Open", "Import")
            )
    
    def openCall(self):
        fname = PyQt6.QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "NDS Files (*.nds *.srl);; All Files (*)",
            options=PyQt6.QtWidgets.QFileDialog.Option.DontUseNativeDialog,
        )
        if not fname == ("", ""): # if file you're trying to open is not none
            self.romToEdit_name = fname[0].split("/")[len(fname[0].split("/")) - 1].split(".")[0]
            self.romToEdit_ext = "." + fname[0].split("/")[len(fname[0].split("/")) - 1].split(".")[1]
            self.rom = ndspy.rom.NintendoDSRom.fromFile(self.romToEdit_name + self.romToEdit_ext)
            self.setWindowTitle("Mega Man ZX Editor" + " (" + self.romToEdit_name + self.romToEdit_ext + ")")
            print(self.rom.filenames)
            self.importSubmenu.setDisabled(False)
            self.button_save.setDisabled(False)
            self.tree.setCurrentItem(None)
            self.treeUpdate()
            self.file_content.setDisabled(True)

    def exportCall(self):
        dialog = PyQt6.QtWidgets.QFileDialog(
                self,
                "Save ROM",
                "",
                "Folders Only",
                options=PyQt6.QtWidgets.QFileDialog.Option.DontUseNativeDialog,
                )
        dialog.setAcceptMode(dialog.AcceptMode.AcceptSave)
        dialog.setFileMode(dialog.FileMode.Directory)
        self.set_dialog_button_name(dialog, "&Open", "Save")
        if dialog.exec(): # if you saved a file
            print(dialog.selectedFiles()[0])
            dialog_formatselect = PyQt6.QtWidgets.QDialog(self)
            dialog_formatselect.setWindowTitle("Choose format")
            dropdown_formatselect = PyQt6.QtWidgets.QComboBox(dialog_formatselect)
            dropdown_formatselect.setGeometry(25, 75, 200, 25)
            dropdown_formatselect.addItems(["Raw", "English dialogue"])
            button_formatselectOK = PyQt6.QtWidgets.QPushButton("OK", dialog_formatselect)
            button_formatselectOK.setGeometry(175, 150, 50, 25)
            button_formatselectOK.pressed.connect(lambda: dialog_formatselect.close())
            button_formatselectOK.pressed.connect(lambda: dialog_formatselect.setResult(1))
            dialog_formatselect.resize(250, 200)
            dialog_formatselect.exec()
            if dialog_formatselect.result():
                print("Selected: " + dropdown_formatselect.currentText())
                if self.fileToEdit_name != '':
                    if self.fileToEdit_name.find(".Folder") == -1: # if file
                        extract(int(w.tree.currentItem().text(0)), fileToEdit_name=str(w.tree.currentItem().text(1) + "." + w.tree.currentItem().text(2)), path=dialog.selectedFiles()[0], format=dropdown_formatselect.currentText())
                    else: # if folder
                        print("Folder " + os.path.join(dialog.selectedFiles()[0] + "/" + w.fileToEdit_name.removesuffix(".Folder")) + " will be created")
                        if os.path.exists(os.path.join(dialog.selectedFiles()[0] + "/" + w.fileToEdit_name.removesuffix(".Folder"))) == False:
                            os.makedirs(os.path.join(dialog.selectedFiles()[0] + "/" + w.fileToEdit_name.removesuffix(".Folder")))
                        print(w.tree.currentItem().childCount() - 1)
                        for i in range(w.tree.currentItem().childCount()):
                            print(w.tree.currentItem().child(i).text(0))
                            extract(int(w.tree.currentItem().child(i).text(0)), path=dialog.selectedFiles()[0], format=dropdown_formatselect.currentText())#, w.fileToEdit_name.replace(".Folder", "/")
                            #str(w.tree.currentItem().child(i).text(1) + "." + w.tree.currentItem().child(i).text(2)), 

    def replaceCall(self):
        if hasattr(w.rom, "name"):
            dialog = PyQt6.QtWidgets.QFileDialog(
                self,
                "Import File",
                "",
                "All Files (*)",
                options=PyQt6.QtWidgets.QFileDialog.Option.DontUseNativeDialog,
                )
            self.set_dialog_button_name(dialog, "&Open", "Import")
            if dialog.exec():
                if str(dialog.selectedFiles()[0]).split("/")[-1].removesuffix("']") in str(self.rom.filenames): # if file you're trying to open is not none
                    with open(*dialog.selectedFiles(), 'rb') as f:
                        fileEdited = f.read()
                        w.rom.setFileByName(str(dialog.selectedFiles()).split("/")[-1].removesuffix("']"), fileEdited)
                    print(str(dialog.selectedFiles()).split("/")[-1].removesuffix("']") + " imported")
                else:
                    print("no " + str(dialog.selectedFiles()[0]).split("/")[-1].removesuffix("']") + " in ROM")

    def insertfileCall(self):
        if hasattr(w.rom, "name"):
            dialog = PyQt6.QtWidgets.QFileDialog(
                self,
                "Import File",
                "",
                "All Files (*)",
                options=PyQt6.QtWidgets.QFileDialog.Option.DontUseNativeDialog,
                )
            self.set_dialog_button_name(dialog, "&Open", "Import")
            if dialog.exec(): # if file you're trying to open is not none
                print(str(dialog.selectedFiles()).split("/")[-1][:-2] + " imported")

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
        self.treeCall()

    def display_format_adapt_Call(self):
        self.fileDisplayMode = "Adapt"
        self.treeCall()

    def display_format_endialog_Call(self):
        self.fileDisplayMode = "English dialogue"
        self.treeCall()
    
    def saveCall(self):
        dialog = PyQt6.QtWidgets.QFileDialog(
                self,
                "Save ROM",
                "",
                "All Files (*)",
                options=PyQt6.QtWidgets.QFileDialog.Option.DontUseNativeDialog,
                )
        dialog.setAcceptMode(dialog.AcceptMode.AcceptSave)
        self.set_dialog_button_name(dialog, "&Open", "Save")
        if dialog.exec(): # if you saved a file
            print(*dialog.selectedFiles())
            w.rom.saveToFile(*dialog.selectedFiles())
            print("ROM modifs saved!")

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
        self.tree.clear()
        self.tree.addTopLevelItems(tree_files)

    def treeCall(self):
        self.button_longfile.hide()
        self.file_content.setReadOnly(False)
        if self.tree.currentItem() != None:
            self.fileToEdit_name = str(self.tree.currentItem().text(1) + "." + self.tree.currentItem().text(2))
            if self.fileToEdit_name.find(".Folder") == -1:
                if self.fileDisplayRaw == False:
                    if (self.fileDisplayMode == "English dialogue") or (self.fileDisplayMode == "Adapt" and self.tree.currentItem().text(1).find("talk") != -1 and self.tree.currentItem().text(1).find("en") != -1): # if english text
                        self.file_content.setPlainText(dataconverter.convertdata_bin_to_text(self.rom.files[int(self.tree.currentItem().text(0))]))
                    else:
                        self.file_content.setReadOnly(True)
                        self.file_content.setPlainText("This file format is unknown/not supported at the moment.\n Go to View > Converted formats to disable file interpretation and view hex data.")
                else:
                    if len((self.rom.files[int(self.tree.currentItem().text(0))]).hex()) > 100000:
                        self.button_longfile.setGeometry(self.file_content.geometry())
                        self.button_longfile.show()
                        self.file_content.setPlainText("")
                        self.file_content.setDisabled(True)
                    else:
                        self.file_content.setPlainText((self.rom.files[int(self.tree.currentItem().text(0))]).hex())
            else:
                self.file_content.setPlainText("")
                self.file_content.setDisabled(True)
            self.exportAction.setDisabled(False)
            self.button_file_save.setDisabled(True)
            self.file_content.setDisabled(False)
        else:
            self.file_content.setPlainText("")
            self.button_file_save.setDisabled(True)

    def save_filetext(self):
        if self.fileDisplayRaw == False:
            if (self.fileDisplayMode == "English dialogue") or (self.fileDisplayMode == "Adapt" and self.tree.currentItem().text(1).find("talk") != -1 and self.tree.currentItem().text(1).find("en") != -1): # if english text
                w.rom.files[int(self.tree.currentItem().text(0))] = dataconverter.convertdata_text_to_bin(self.file_content.toPlainText())
        else:
            w.rom.files[int(self.tree.currentItem().text(0))] = bytearray.fromhex(self.file_content.toPlainText())
        print("file changes saved")
        self.button_file_save.setDisabled(True)

app = PyQt6.QtWidgets.QApplication(sys.argv)
w = MainWindow()
def extract(fileToEdit_id, folder="", fileToEdit_name="", path="", format=""):
    fileToEdit = w.rom.files[fileToEdit_id]
    if fileToEdit_name == "":
        fileToEdit_name = w.rom.filenames[fileToEdit_id]
    print("file " + str(fileToEdit_id) + ": " + fileToEdit_name)
    print(fileToEdit[0x65:0xc5])

    # create a copy of the file outside ROM
    if format == "" or format == "Raw":
        with open(os.path.join(path + "/" + folder + fileToEdit_name), 'wb') as f:
            f.write(fileToEdit)
            print(os.path.join(path + "/" + folder + fileToEdit_name))
            print("File extracted!")
    else:
        match format:
            case "English dialogue":
                with open(os.path.join(path + "/" + folder + fileToEdit_name.split(".")[0] + ".txt"), 'wb') as f:
                    f.write(bytes(dataconverter.convertdata_bin_to_text(fileToEdit), "utf-8"))
                    print(os.path.join(path + "/" + folder + fileToEdit_name.split(".")[0] + ".txt"))
                    print("File extracted!")
            case _:
                print("could not find method for converting to specified format.")
#run the app
app.exec()