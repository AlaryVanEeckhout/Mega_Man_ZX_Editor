import PyQt6
import PyQt6.QtGui, PyQt6.QtWidgets, PyQt6.QtCore
import sys, os
import ndspy
import ndspy.rom, ndspy.code
import dataconverter, init_readwrite

class GFXView(PyQt6.QtWidgets.QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._zoom = 0
        self._empty = True
        self._scene = PyQt6.QtWidgets.QGraphicsScene(self)
        self._graphic = PyQt6.QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._graphic)
        self.setScene(self._scene)
        self.setResizeAnchor(
            PyQt6.QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

        self.pen = PyQt6.QtGui.QPen()
        self.pen.setColor(PyQt6.QtCore.Qt.GlobalColor.black)
        self.start = PyQt6.QtCore.QPoint()
        self.end = PyQt6.QtCore.QPoint()
        self.end_previous = PyQt6.QtCore.QPoint()
        self.setMouseTracking(True)
        self.mousePressed = False
        self.draw_mode = "pixel"
        self.rect, self.line = None, None # used for drawing rectangles

    def resetScene(self):
        self._scene.clear()
        self._graphic = PyQt6.QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._graphic)

    def hasGraphic(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = PyQt6.QtCore.QRectF(self._graphic.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasGraphic():
                unity = self.transform().mapRect(PyQt6.QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setGraphic(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self._graphic.setPixmap(pixmap)
        else:
            self._empty = True
            self._graphic.setPixmap(PyQt6.QtGui.QPixmap())
        self.fitInView()


    def drawShape(self):
        match self.draw_mode:
            case "pixel":
                pixel_map = PyQt6.QtGui.QPixmap(1, 1)
                pixel_map.fill(self.pen.color())

                pixel_container = PyQt6.QtWidgets.QGraphicsPixmapItem()
                pixel_container.setPixmap(pixel_map)
                pixel_container.moveBy(int(self.end.x()),int(self.end.y()))
                self._scene.addItem(pixel_container)

                pixel_container = PyQt6.QtWidgets.QGraphicsPixmapItem()
                pixel_container.setPixmap(pixel_map)
                pixel_container.moveBy(int(self.end_previous.x()),int(self.end_previous.y()))
                self._scene.addItem(pixel_container)

                pixel_container = PyQt6.QtWidgets.QGraphicsPixmapItem()
                pixel_container.setPixmap(pixel_map)
                pixel_container.moveBy(int(self.end_previous.x()),int(self.end_previous.y()))
                pixel_container.moveBy(int(self.end_previous.x() - self.end.x()),int(self.end_previous.y() - self.end.y()))
                self._scene.addItem(pixel_container)
            case "rectangle":
                if self.start.isNull() or self.end.isNull():
                    return
                if self.start.x() == self.end.x() and self.start.y() == self.end.y():
                    return
                elif abs(self.end.x() - self.start.x()) < 1 or abs(self.end.y() - self.start.y()) < 1:
                    if self.rect != None:
                        self.scene().removeItem(self.rect)
                        self.rect = None
                    if abs(self.end.y() - self.start.y()) < 1:
                        # draw vertical line
                        if self.line != None:
                            self.line.setLine(self.start.x(), self.start.y(), self.end.x(), self.start.y())
                        else:
                            self.line = self.scene().addLine(self.start.x(), self.start.y(), self.end.x(), self.start.y(), self.pen)
                    else:
                        # draw horizontal line
                        if self.line != None:
                            self.line.setLine(self.start.x(), self.start.y(), self.start.x(), self.end.y())
                        else:
                            self.line = self.scene().addLine(self.start.x(), self.start.y(), self.start.x(), self.end.y(), self.pen)                    
                else:
                    if self.line != None:
                        self.scene().removeItem(self.line)
                        self.line = None

                    width = abs(self.start.x() - self.end.x())
                    height = abs(self.start.y() - self.end.y())
                    if self.rect == None:
                        self.rect = self.scene().addRect(min(self.start.x(), self.end.x()), min(self.start.y(), self.end.y()), width, height, self.pen)
                    else:
                        self.rect.setRect(min(self.start.x(), self.end.x()), min(self.start.y(), self.end.y()), width, height)

    def mousePressEvent(self, event):
        #print("QGraphicsView mousePress")
        self.draw_mode = "pixel"
        if event.button() == PyQt6.QtCore.Qt.MouseButton.LeftButton:
            self.mousePressed = True
            self.start = self.mapToScene(event.pos())
            self.drawShape()
        elif event.button() == PyQt6.QtCore.Qt.MouseButton.RightButton:
            self.draw_mode = "rectangle"
            self.mousePressed = True
            self.start = self.mapToScene(event.pos())

    def wheelEvent(self, event):
        if event.modifiers() == PyQt6.QtCore.Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.80
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
        if self._zoom <= 0:
            self.fitInView()
            # make zoom properly reset
            PyQt6.QtWidgets.QApplication.processEvents()
            self.fitInView()

    def mouseMoveEvent(self, event):
        #print("QGraphicsView mouseMove")
        if self.draw_mode == "rectangle":
            if event.buttons() and PyQt6.QtCore.Qt.MouseButton.LeftButton and self.mousePressed:
                self.end = self.mapToScene(event.pos())
                self.drawShape()
        else:
            self.end = self.mapToScene(event.pos())
            if event.buttons() and PyQt6.QtCore.Qt.MouseButton.LeftButton and self.mousePressed:
                self.drawShape()
            self.end_previous = self.end

    def mouseReleaseEvent(self, event):
        #print("QGraphicsView mouseRelease")
        if event.button() == PyQt6.QtCore.Qt.MouseButton.LeftButton and self.mousePressed:
            self.mousePressed = False
            self.drawShape()
            self.start, self.end = PyQt6.QtCore.QPoint(), PyQt6.QtCore.QPoint()
            self.rect, self.line = None, None

class EditorTree(PyQt6.QtWidgets.QTreeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def mousePressEvent(self, event):
        if event.type() == PyQt6.QtCore.QEvent.Type.MouseButtonPress:
            if event.button() == PyQt6.QtCore.Qt.MouseButton.RightButton: # execute different code if right click
                super(EditorTree, self).mousePressEvent(event)
                if w.tree.currentItem() != None:
                    w.treeContextMenu()
            else: # do normal code if not right click
                super(EditorTree, self).mousePressEvent(event)

class HoldButton(PyQt6.QtWidgets.QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = 0
        self.rate = 100
        self.allow_press = False
        self.timer = PyQt6.QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_timeout)
        self.pressed.connect(self.on_press)
        self.released.connect(self.on_release)
        self.timeout_func = None

    def on_timeout(self):
        self.counter += 1
        #print("hold " + str(self.counter))
        if self.timeout_func != None:
            for f in self.timeout_func:
                f()

    def on_press(self):
        #print("pressed")
        self.counter = 0
        if self.allow_press == True and self.timeout_func != None:
            for f in self.timeout_func:
                f()
        self.timer.start(self.rate)

    def on_release(self):
        #print("released")
        self.timer.stop()
        self.counter = -1

class MainWindow(PyQt6.QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.window_width = 1024
        self.window_height = 720
        self.setWindowIcon(PyQt6.QtGui.QIcon('icon_biometals-creation.png'))
        self.setWindowTitle("Mega Man ZX Editor")
        self.rom = ndspy.rom.NintendoDSRom
        self.arm9 = ndspy.code.MainCodeFile
        self.arm7 = ndspy.code.MainCodeFile
        self.base_address = 0x00000000
        self.romToEdit_name = ''
        self.romToEdit_ext = ''
        self.fileToEdit_name = ''
        self.fileDisplayRaw = False # Display file in 'raw'(bin) format. Else, diplayed in readable format
        self.fileDisplayMode = "Adapt" # Modes: Adapt, Binary, English dialogue, Japanese dialogue, Graphics, Sound, Movie, Code
        self.resize(self.window_width, self.window_height)
        self.theme_switch = False
        self.UiComponents()
        self.show()
        self.load_preferences()

    def load_preferences(self):
        #SETTINGS
        init_readwrite.load_preferences(self, "SETTINGS", struct="bool")
        self.checkbox_theme.setChecked(self.theme_switch)# Update checkbox with current option
        self.switch_theme(True)# Update theme with current option

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

        self.replaceAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_blue-document-import.png'), '&Replace...', self)
        self.replaceAction.setShortcut('Ctrl+R')
        self.replaceAction.setStatusTip('replace with file in binary or converted format')
        self.replaceAction.triggered.connect(self.replaceCall)

        self.replacebynameAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_blue-document-import.png'), '&Replace by name...', self)        
        self.replacebynameAction.setStatusTip('replace with file of same name in binary or converted format')
        self.replacebynameAction.triggered.connect(self.replacebynameCall)

        self.menu_bar = self.menuBar()
        self.fileMenu = self.menu_bar.addMenu('&File')
        self.fileMenu.addActions([self.openAction, self.exportAction])
        self.importSubmenu = self.fileMenu.addMenu('&Import...')
        self.importSubmenu.setIcon(PyQt6.QtGui.QIcon('icon_blue-document-import.png'))
        self.importSubmenu.addActions([self.replaceAction, self.replacebynameAction])
        self.importSubmenu.setDisabled(True)

        self.dialog_settings = PyQt6.QtWidgets.QDialog(self)
        self.dialog_settings.setWindowTitle("Settings")
        self.dialog_settings.resize(100, 25)
        self.checkbox_theme = PyQt6.QtWidgets.QCheckBox("Dark Theme", self.dialog_settings)
        self.checkbox_theme.move(15, 0)
        self.checkbox_theme.clicked.connect(lambda: self.switch_theme())

        self.settingsAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_gear.png'), '&Settings', self)
        self.settingsAction.setStatusTip('Settings')
        self.settingsAction.triggered.connect(lambda: self.dialog_settings.exec())

        self.exitAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_door.png'), '&Exit', self)
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.exitCall)

        self.appMenu = self.menu_bar.addMenu('&Application')
        self.appMenu.addActions([self.settingsAction, self.exitAction])

        self.displayRawAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_brain.png'), '&Converted formats', self)
        self.displayRawAction.setStatusTip('Displays files in a readable format instead of raw format.')
        self.displayRawAction.setCheckable(True)
        self.displayRawAction.setChecked(True)
        self.displayRawAction.triggered.connect(self.display_format_toggleCall)

        self.viewAdaptAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_document-node.png'), '&Adapt', self)
        self.viewAdaptAction.setStatusTip('Files will be decrypted on a case per case basis.')
        self.viewAdaptAction.setCheckable(True)
        self.viewAdaptAction.setChecked(True)
        self.viewAdaptAction.triggered.connect(lambda: self.value_update_Call("fileDisplayMode", "Adapt"))

        self.viewEndialogAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_document-text.png'), '&English Dialogue', self)
        self.viewEndialogAction.setStatusTip('Files will be decrypted as in-game english dialogues.')
        self.viewEndialogAction.setCheckable(True)
        self.viewEndialogAction.triggered.connect(lambda: self.value_update_Call("fileDisplayMode", "English dialogue"))

        self.viewGraphicAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_biometals-creation.png'), '&Graphics', self)
        self.viewGraphicAction.setStatusTip('Files will be decrypted as graphics.')
        self.viewGraphicAction.setCheckable(True)
        self.viewGraphicAction.triggered.connect(lambda: self.value_update_Call("fileDisplayMode", "Graphics"))

        self.viewFormatsGroup = PyQt6.QtGui.QActionGroup(self) #group for mutually exclusive togglable items
        self.viewFormatsGroup.addAction(self.viewAdaptAction)
        self.viewFormatsGroup.addAction(self.viewEndialogAction)
        self.viewFormatsGroup.addAction(self.viewGraphicAction)

        self.viewMenu = self.menu_bar.addMenu('&View')
        self.viewMenu.addAction(self.displayRawAction)
        self.displayFormatSubmenu = self.viewMenu.addMenu(PyQt6.QtGui.QIcon('icon_document-convert.png'), '&Set edit mode...')
        self.displayFormatSubmenu.addActions([self.viewAdaptAction, self.viewEndialogAction, self.viewGraphicAction])

        #Toolbar
        self.toolbar = PyQt6.QtWidgets.QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)

        self.button_save = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_disk.png'), "Save to ROM", self)
        self.button_save.setStatusTip("Save changes to the ROM")
        self.button_save.triggered.connect(self.saveCall)
        self.button_save.setDisabled(True)
        #self.button_codeedit = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icon_document-text.png'), "Open code", self)
        #self.button_codeedit.setStatusTip("Edit the ROM's code")
        #self.button_codeedit.triggered.connect(self.codeeditCall)
        #self.button_codeedit.setDisabled(True)
        self.toolbar.addActions([self.button_save])

        #ROM-related
        self.tree = EditorTree(self)
        self.tree.move(0, self.menu_bar.rect().bottom() + 45)
        self.tree.resize(450, 625)
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["File ID", "Name", "Type"])
        self.tree.setContextMenuPolicy(PyQt6.QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeUpdate()
        self.tree.itemSelectionChanged.connect(self.treeCall)

        self.button_file_save = PyQt6.QtWidgets.QPushButton("Save file", self)
        self.button_file_save.setToolTip("save this file's changes")
        self.button_file_save.setGeometry(500, 70, 100, 50)
        self.button_file_save.pressed.connect(self.save_filecontent)
        self.button_file_save.setDisabled(True)

        self.file_content = PyQt6.QtWidgets.QFrame(self)
        self.file_content.setGeometry(475, self.menu_bar.rect().bottom() + 100, 500, 500)
        self.file_content_text = PyQt6.QtWidgets.QPlainTextEdit(self.file_content)
        self.file_content_text.resize(self.file_content.size())
        font = PyQt6.QtGui.QFont("Monospace")
        font.setStyleHint(PyQt6.QtGui.QFont.StyleHint.TypeWriter)
        self.file_content_text.setFont(font)
        self.file_content_text.textChanged.connect(lambda: self.button_file_save.setDisabled(False))
        self.file_content_text.setDisabled(True)
        self.checkbox_textoverwite = PyQt6.QtWidgets.QCheckBox("Overwite\n existing text", self)
        self.checkbox_textoverwite.setGeometry(625, 70, 100, 50)
        self.checkbox_textoverwite.setStatusTip("With this enabled, writing text won't change filesize")
        self.checkbox_textoverwite.clicked.connect(lambda: self.file_content_text.setOverwriteMode(not self.file_content_text.overwriteMode()))
        self.checkbox_textoverwite.hide()
        self.button_longfile = PyQt6.QtWidgets.QPushButton("Press this button to view file,\nbut be warned that this file is very big.\nTherefore if you choose to view it,\nit will take some time to load\nand the program will be unresponsive.\n\nAlternatively, you could export the file and open it in a hex editor", self.file_content_text)
        self.button_longfile.pressed.connect(lambda: self.button_longfile.hide())
        self.button_longfile.pressed.connect(lambda: print("will take a while"))
        self.button_longfile.pressed.connect(lambda: self.file_content_text.setDisabled(False))
        self.button_longfile.pressed.connect(lambda: self.file_content_text.setPlainText((self.rom.files[int(self.tree.currentItem().text(0))]).hex()))
        self.button_longfile.hide()

        self.file_content_gfx = GFXView(self.file_content)
        self.file_content_gfx.resize(self.file_content.size())
        self.file_content_gfx.hide()
        self.dropdown_gfx_depth = PyQt6.QtWidgets.QComboBox(self)
        self.dropdown_gfx_depth.move(725, 60)
        self.dropdown_gfx_depth.addItems(["1bpp", "2bpp(WIP)", "4bpp", "8bpp(WIP)"])
        self.dropdown_gfx_depth.currentTextChanged.connect(self.treeCall)# Update gfx with current depth
        self.dropdown_gfx_depth.hide()

        # Make a line edit widget that can change value when you click on the arrows
        self.relative_adress = 0x00000000
        self.field_address = PyQt6.QtWidgets.QLineEdit(self)
        self.field_address.setGeometry(850, 60, 100, 25)
        self.field_address.textChanged.connect(lambda: self.treeCall(True))
        self.field_address.hide()
        self.button_address_inc = HoldButton("⯅", self)
        self.button_address_inc.timeout_func = [lambda: self.value_update_Call("relative_adress", min(self.relative_adress + 1, len(self.rom.files[int(self.tree.currentItem().text(0))])), False), lambda: self.field_address.setText(f"{self.base_address+self.relative_adress:08X}")]
        self.button_address_inc.allow_press = True
        self.button_address_inc.setGeometry(950, 55, 25, 20)
        self.button_address_inc.hide()
        self.button_address_dec = HoldButton("⯆", self)
        self.button_address_dec.timeout_func = [lambda: self.value_update_Call("relative_adress", max(self.relative_adress - 1, 0), False), lambda: self.field_address.setText(f"{self.base_address+self.relative_adress:08X}")]
        self.button_address_dec.allow_press = True
        self.button_address_dec.setGeometry(950, 75, 25, 20)
        self.button_address_dec.hide()
        #PyQt6.QtWidgets.QKeySequenceEdit()

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
            self.arm9 = self.rom.loadArm9()
            self.arm7 = self.rom.loadArm7()
            self.setWindowTitle("Mega Man ZX Editor" + " (" + self.romToEdit_name + self.romToEdit_ext + ")")
            print(self.rom.filenames)
            self.importSubmenu.setDisabled(False)
            self.button_save.setDisabled(False)
            #self.button_codeedit.setDisabled(False)
            self.tree.setCurrentItem(None)
            self.treeUpdate()
            self.file_content_text.setDisabled(True)

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

    def replacebynameCall(self):
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
                if str(dialog.selectedFiles()[0]).split("/")[-1].removesuffix("']") in str(self.rom.filenames): # if file you're trying to replace is in ROM
                    with open(*dialog.selectedFiles(), 'rb') as f:
                        fileEdited = f.read()
                        w.rom.setFileByName(str(dialog.selectedFiles()).split("/")[-1].removesuffix("']"), fileEdited)
                    print(str(dialog.selectedFiles()).split("/")[-1].removesuffix("']") + " imported")
                elif str(dialog.selectedFiles()[0]).split("/")[-1].removesuffix("']").split(".")[0] in str(self.rom.filenames): # if filename of file(without extension) you're trying to replace is in ROM
                    with open(*dialog.selectedFiles(), 'rb') as f:
                        fileEdited = f.read()
                        match str(dialog.selectedFiles()[0]).split("/")[-1].removesuffix("']").split(".")[1]:
                            case "txt":
                                try:
                                    print(w.rom.filenames.idOf(str(dialog.selectedFiles()).split("/")[-1].removesuffix("']").replace(".txt", ".bin")))
                                    w.rom.files[w.rom.filenames.idOf(str(dialog.selectedFiles()).split("/")[-1].removesuffix("']").replace(".txt", ".bin"))] = dataconverter.convertdata_text_to_bin(fileEdited.decode("utf-8"))
                                except Exception as e:
                                    print(e)
                            case _:
                                print("format not recognized")
                else:
                    print("no " + str(dialog.selectedFiles()[0]).split("/")[-1].removesuffix("']") + " in ROM")
                self.treeCall()

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
            if dialog.exec(): # if file you're trying to replace is in ROM
                    with open(*dialog.selectedFiles(), 'rb') as f:
                        fileEdited = f.read()
                        match str(dialog.selectedFiles()[0]).split("/")[-1].removesuffix("']").split(".")[1]:
                            case "txt":
                                try:
                                    print(w.tree.currentItem().text(0))
                                    w.rom.files[int(w.tree.currentItem().text(0))] = dataconverter.convertdata_text_to_bin(fileEdited.decode("utf-8"))
                                except Exception as e:
                                    print(e)
                            case _:
                                w.rom.files[int(w.tree.currentItem().text(0))] = fileEdited
                                print("raw data replaced")
                    print(str(dialog.selectedFiles()).split("/")[-1].removesuffix("']") + " imported")
                    self.treeCall()
    
    def switch_theme(self, isupdate=False):
        if isupdate == False:
            self.theme_switch = not self.theme_switch
            init_readwrite.write_preferences(self)
        if self.theme_switch:
            app = PyQt6.QtCore.QCoreApplication.instance()
            app.setStyleSheet(open('dark_theme.qss').read())
        else:
            app = PyQt6.QtCore.QCoreApplication.instance()
            app.setStyleSheet("")

    def exitCall(self):
        self.close()
    
    def display_format_toggleCall(self):
        self.fileDisplayRaw = not self.fileDisplayRaw
        self.displayFormatSubmenu.setDisabled(self.displayFormatSubmenu.isEnabled())
        self.toggle_widget_icon(self.displayRawAction, PyQt6.QtGui.QIcon('icon_brain.png'), PyQt6.QtGui.QIcon('icon_document-binary.png'))
        self.treeCall()

    def value_update_Call(self, var, val, istreecall=True):
        setattr(self, var, val)
        if istreecall:
            self.treeCall(True)
    
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

    #def codeeditCall(self):
        #self.tree.clearSelection()
        #self.arm9 = ndspy.code.MainCodeFile(w.rom.files[0], 0x00000000)
        #self.file_content_text.setPlainText(str(self.arm9))
        #print("code")

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

    def treeCall(self, isValueUpdate=False):
        self.button_longfile.hide()
        self.file_content_text.setReadOnly(False)
        if self.tree.currentItem() != None:
            self.fileToEdit_name = str(self.tree.currentItem().text(1) + "." + self.tree.currentItem().text(2))
            if self.fileToEdit_name.find(".Folder") == -1:
                if self.fileDisplayRaw == False:
                    if (self.fileDisplayMode == "English dialogue") or (self.fileDisplayMode == "Adapt" and self.tree.currentItem().text(1).find("talk") != -1 and self.tree.currentItem().text(1).find("en") != -1): # if english text
                        self.file_editor_show("Text")
                        self.file_content_text.setPlainText(dataconverter.convertdata_bin_to_text(self.rom.files[int(self.tree.currentItem().text(0))]))
                    elif (self.fileDisplayMode == "Graphics") or (self.fileDisplayMode == "Adapt" and (self.tree.currentItem().text(1).find("obj_fnt") != -1 or self.tree.currentItem().text(1).find("font") != -1 or self.tree.currentItem().text(1).find("face") != -1)):
                        print(self.dropdown_gfx_depth.currentText()[:1] + " bpp graphics")
                        self.file_content_gfx.resetScene()
                        if not isValueUpdate:
                            self.file_editor_show("Graphics")
                        self.base_address = 0x00179400
                        # set text to current ROM address
                        # first viewable file has address 0x00179400 and id 0117
                        self.field_address.setText(f"{self.base_address+self.relative_adress:08X}")
                        addItem_tilesQImage_frombytes(self.file_content_gfx, self.rom.files[int(self.tree.currentItem().text(0))][self.relative_adress:], depth=int(self.dropdown_gfx_depth.currentText()[:1]))
                    else:
                        self.file_editor_show("Text")
                        self.file_content_text.setReadOnly(True)
                        self.file_content_text.setPlainText("This file format is unknown/not supported at the moment.\n Go to [View > Converted formats] to disable file interpretation and view hex data.")
                else:
                    self.file_editor_show("Text")
                    if len((self.rom.files[int(self.tree.currentItem().text(0))]).hex()) > 100000:
                        self.button_longfile.setGeometry(self.file_content_text.geometry())
                        self.button_longfile.show()
                        self.file_content_text.setPlainText("")
                        self.file_content_text.setDisabled(True)
                    else:
                        self.file_content_text.setPlainText(self.rom.files[int(self.tree.currentItem().text(0))].hex())
                self.file_content_text.setDisabled(False)
            else:
                self.file_content_text.setPlainText("")
                self.file_content_text.setDisabled(True)
            self.exportAction.setDisabled(False)
            self.button_file_save.setDisabled(True)
        else:# Nothing is selected, reset edit space
            self.file_content_text.setPlainText("")
            self.button_file_save.setDisabled(True)

    def file_editor_show(self, mode):
        match mode:
            case "Text":
                # Hide unwanted widgets
                self.file_content_gfx.hide()
                self.dropdown_gfx_depth.hide()
                self.field_address.hide()
                self.button_address_inc.hide()
                self.button_address_dec.hide()

                # Show wanted widgets
                self.file_content_text.show()
                self.checkbox_textoverwite.show()
            case "Graphics":
                # Hide unwanted widgets
                self.file_content_text.hide()
                self.checkbox_textoverwite.hide()

                # Reset Values
                self.relative_adress = 0x00000000
                print(f"{len(self.rom.save()):08X}")

                # Show wanted widgets
                self.file_content_gfx.show()
                self.dropdown_gfx_depth.show()
                self.field_address.show()
                self.button_address_inc.show()
                self.button_address_dec.show()

    def treeContextMenu(self):
        self.tree_context_menu = PyQt6.QtWidgets.QMenu(self.tree)
        self.tree_context_menu.setGeometry(self.tree.cursor().pos().x(), self.tree.cursor().pos().y(), 50, 50)
        exportAction = self.tree_context_menu.addAction("Export " + self.tree.currentItem().text(1) + ("." + self.tree.currentItem().text(2)).replace(".Folder", " and contents"))
        importAction = self.tree_context_menu.addAction("Replace " + self.tree.currentItem().text(1) + ("." + self.tree.currentItem().text(2)).replace(".Folder", " and contents"))
        action2 = self.tree_context_menu.exec()
        if action2 is not None:
            if action2 == exportAction:
                self.exportCall()
            elif action2 == importAction:
                self.replaceCall()

    def save_filecontent(self):
        if self.fileDisplayRaw == False:
            if (self.fileDisplayMode == "English dialogue") or (self.fileDisplayMode == "Adapt" and self.tree.currentItem().text(1).find("talk") != -1 and self.tree.currentItem().text(1).find("en") != -1): # if english text
                w.rom.files[int(self.tree.currentItem().text(0))] = dataconverter.convertdata_text_to_bin(self.file_content_text.toPlainText())
        else:
            w.rom.files[int(self.tree.currentItem().text(0))] = bytearray.fromhex(self.file_content_text.toPlainText())
        print("file changes saved")
        self.button_file_save.setDisabled(True)

app = PyQt6.QtWidgets.QApplication(sys.argv)
w = MainWindow()

# Draw contents of tile viewer
def addItem_tilesQImage_frombytes(view, data, palette=[0xff000000+((0x0b7421*i)%0x1000000) for i in range(256)], depth=1, tilesPerRow=4, tilesPerColumn=56, tileWidth=8, tileHeight=8):
    for tile in range(tilesPerRow*tilesPerColumn):
        # get data of current tile from bytearray, multiplying tile index by amount of pixels in a tile and by amount of bits per pixel, then dividing by amount of bits per byte
        # that data is then converted into a QImage that is used to create the QPixmap of the tile
        gfx = PyQt6.QtGui.QPixmap.fromImage(dataconverter.convertdata_bin_to_qt(data[int(tile*(tileWidth*tileHeight)*depth/8):int(tile*(tileWidth*tileHeight)*depth/8+(tileWidth*tileHeight)*depth/8)], palette, depth, tileWidth, tileHeight))
        gfx_container = PyQt6.QtWidgets.QGraphicsPixmapItem()
        gfx_container.setPixmap(gfx)
        #print(tile)
        #print(str(gfx_container.pos().x()) + " " + str(gfx_container.pos().y()))
        gfx_container.setPos(tileWidth*(tile % tilesPerRow), tileHeight*int(tile / tilesPerRow))
        #print(str(gfx_container.pos().x()) + " " + str(gfx_container.pos().y()))
        view._scene.addItem(gfx_container)
    return

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