import PyQt6
import PyQt6.QtGui, PyQt6.QtWidgets, PyQt6.QtCore
import sys, os, platform
#import logging, time, random
#import numpy
import ndspy
import ndspy.rom, ndspy.code
import ndspy.soundArchive
#import PyQt6.Qt6
#import PyQt6.Qt6.qsci
import library.dataconverter, library.patchdata, library.init_readwrite, library.actimagine
#Global variables
global EDITOR_VERSION
EDITOR_VERSION = "0.2.3" # objective, feature, WIP

class ThreadSignals(PyQt6.QtCore.QObject):
    signal_RunnableDisplayRawText = PyQt6.QtCore.pyqtSignal(str)

class RunnableDisplayRawText(PyQt6.QtCore.QRunnable):

    def __init__(self, n):
        super().__init__()
        self.n = n
        self.signals = ThreadSignals()

    def run(self):
        print("runnable active")
        #PyQt6.QtCore.QMetaObject.invokeMethod(w.file_content_text, "decSetUnavailable", PyQt6.QtCore.Qt.ConnectionType.QueuedConnection, PyQt6.QtCore.Q_ARG(bool, True))
        #PyQt6.QtCore.QMetaObject.invokeMethod(w.file_content_text, "decSetLongText", PyQt6.QtCore.Qt.ConnectionType.QueuedConnection, PyQt6.QtCore.Q_ARG(str, ""))
        #text = w.rom.files[int(w.tree.currentItem().text(0))].hex()
        #chunk_size = 1000
        #for i in range(int(len(text)/chunk_size)):
        #    text = w.rom.files[int(w.tree.currentItem().text(0))].hex()[i*chunk_size:i*chunk_size+chunk_size]
        #    PyQt6.QtCore.QMetaObject.invokeMethod(w.file_content_text, "decSetLongText", PyQt6.QtCore.Qt.ConnectionType.QueuedConnection, PyQt6.QtCore.Q_ARG(str, text))
        #    time.sleep(1)
        #self.signals.signal_RunnableDisplayRawText.emit((w.rom.files[int(w.tree.currentItem().text(0))]).hex())
        #PyQt6.QtCore.QMetaObject.invokeMethod(w.file_content_text, "decSetUnavailable", PyQt6.QtCore.Qt.ConnectionType.QueuedConnection, PyQt6.QtCore.Q_ARG(bool, False))
        print("runnable finish")

class GFXView(PyQt6.QtWidgets.QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._zoom = 0
        self._empty = True
        self._scene = PyQt6.QtWidgets.QGraphicsScene(self)
        self._graphic = PyQt6.QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._graphic)
        self.setScene(self._scene)

        self.pen = PyQt6.QtGui.QPen()
        self.pen.setColor(PyQt6.QtCore.Qt.GlobalColor.black)
        self.start = PyQt6.QtCore.QPoint()
        self.end = PyQt6.QtCore.QPoint()
        self.end_previous = PyQt6.QtCore.QPoint()
        self.setMouseTracking(True)
        self.mousePressed = False
        self.draw_mode = "pixel"
        self.rectangle, self.line = None, None # used for drawing rectangles

    def resetScene(self):
        self._scene.clear()
        self._graphic = PyQt6.QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._graphic)

    def hasGraphic(self):
        return self._scene.isActive()

    def fitInView(self, scale=True):
        rect = PyQt6.QtCore.QRectF(self._graphic.pixmap().rect())
        self.setSceneRect(rect)
        if self.hasGraphic() and scale:
            #print("fit")
            unity = self.transform().mapRect(PyQt6.QtCore.QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            viewrect = self.viewport().rect()
            scenerect = self.sceneRect()
            factor = min(viewrect.width() / scenerect.width(),
                            viewrect.height() / scenerect.height())
            self.scale(factor, factor)
        self._zoom = 0

    def setGraphic(self, pixmap: PyQt6.QtGui.QPixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self._graphic.setPixmap(pixmap)
        else:
            self._empty = True
            self._graphic.setPixmap(PyQt6.QtGui.QPixmap())
        self.fitInView()


    def drawShape(self):
        if self.draw_mode == "pixel":
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
                w.button_file_save.setDisabled(False)
        elif self.draw_mode == "rectangle":
                if self.start.isNull() or self.end.isNull():
                    return
                if self.start.x() == self.end.x() and self.start.y() == self.end.y():
                    return
                elif abs(self.end.x() - self.start.x()) < 1 or abs(self.end.y() - self.start.y()) < 1:
                    if self.rectangle != None:
                        self.scene().removeItem(self.rectangle)
                        self.rectangle = None
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
                    if self.rectangle == None:
                        self.rectangle = self.scene().addRect(min(self.start.x(), self.end.x()), min(self.start.y(), self.end.y()), width, height, self.pen)
                    else:
                        self.rectangle.setRect(min(self.start.x(), self.end.x()), min(self.start.y(), self.end.y()), width, height)

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
        #print(self._zoom)
        if event.modifiers() == PyQt6.QtCore.Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.80
                self._zoom -= 1
            if self._zoom > 0:
                view_pos = PyQt6.QtCore.QRect(event.position().toPoint(), PyQt6.QtCore.QSize(1, 1))
                scene_pos = self.mapToScene(view_pos)
                self.centerOn(scene_pos.boundingRect().center())
                self.scale(factor, factor)
                delta = self.mapToScene(view_pos.center()) - self.mapToScene(self.viewport().rect().center())
                self.centerOn(scene_pos.boundingRect().center() - delta)
        if self._zoom <= 0:
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
            self.rectangle, self.line = None, None

class EditorTree(PyQt6.QtWidgets.QTreeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def contextMenuOpen(self): #quick menu to export or replace selected file
        self.context_menu = PyQt6.QtWidgets.QMenu(self)
        self.context_menu.setGeometry(self.cursor().pos().x(), self.cursor().pos().y(), 50, 50)
        exportAction = self.context_menu.addAction("Export " + self.currentItem().text(1) + ("." + self.currentItem().text(2)).replace(".Folder", " and contents"))
        importAction = self.context_menu.addAction("Replace " + self.currentItem().text(1) + ("." + self.currentItem().text(2)).replace(".Folder", " and contents"))
        if self.currentItem().text(2) == "sdat":
            sdatAction = self.context_menu.addAction("Open Sound Archive")
        action2 = self.context_menu.exec()
        if action2 is not None:
            if action2 == exportAction:
                w.exportCall(self.currentItem())
            elif action2 == importAction:
                w.replaceCall(self.currentItem())
            elif action2 == sdatAction:
                w.dialog_sdat.show()
    
    def mousePressEvent(self, event: PyQt6.QtCore.QEvent): #redefine mouse press to insert custom code on right click
        if event.type() == PyQt6.QtCore.QEvent.Type.MouseButtonPress:
            super(EditorTree, self).mousePressEvent(event)
            if event.button() == PyQt6.QtCore.Qt.MouseButton.RightButton and self.currentItem() != None: # execute different code if right click
                self.contextMenuOpen()

class HoldButton(PyQt6.QtWidgets.QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = 0
        self.rate = 100
        self.allow_press = False
        self.pressed_quick = False
        self.press_quick_threshold = 0
        self.timer = PyQt6.QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_timeout)
        self.pressed.connect(self.on_press)
        self.released.connect(self.on_release)
        self.timeout_func = None

    def on_timeout(self):
        self.pressed_quick = False
        self.counter += 1
        #print("hold " + str(self.counter))
        if self.timeout_func != None:
            for f in self.timeout_func:
                f()

    def on_press(self):
        #print("pressed")
        self.counter = 0
        self.timer.start(self.rate)

    def on_release(self):
        #print("released")
        if self.counter <= self.press_quick_threshold and self.allow_press == True:
            self.pressed_quick = True
            if self.timeout_func != None:
                for f in self.timeout_func:
                    f()
        self.pressed_quick = False
        self.timer.stop()
        self.counter = -1

class BetterSpinBox(PyQt6.QtWidgets.QSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alphanum = True
        self.setRange(-0x03000000, 0x03000000)
        self.numfill = 0

    def textFromValue(self, value): # ovewrite of existing function with 2 args that determines how value is displayed inside spinbox
        return library.dataconverter.StrFromNumber(value, self.displayIntegerBase(), self.alphanum).zfill(self.numfill)
    
    def valueFromText(self, text):
        return library.dataconverter.IntFromStr(text, self.displayIntegerBase())

class LongTextEdit(PyQt6.QtWidgets.QPlainTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.charcount_page = lambda: int(int(self.width()/self.fontMetrics().averageCharWidth() - 1)*int(self.height()/self.fontMetrics().lineSpacing() -1)/2)

    def contextMenuOpen(self): #quick menu to insert special values in dialogue file
        self.context_menu = PyQt6.QtWidgets.QMenu(self)
        self.context_menu.setGeometry(self.cursor().pos().x(), self.cursor().pos().y(), 50, 50)
        for char_index in range(len(library.dataconverter.SPECIAL_CHARACTER_LIST)):
            if char_index >= 0xe0 and type(library.dataconverter.SPECIAL_CHARACTER_LIST[char_index]) != type(int()):
                self.context_menu.addAction(f"{library.dataconverter.StrFromNumber(char_index, w.displayBase, w.displayAlphanumeric).zfill(2)} - {library.dataconverter.SPECIAL_CHARACTER_LIST[char_index][1]}")
        action2 = self.context_menu.exec()
        if action2 is not None:
            self.insertPlainText(action2.text()[action2.text().find("├"):])

    def mousePressEvent(self, event: PyQt6.QtCore.QEvent): #redefine mouse press to insert custom code on right click
        if event.type() == PyQt6.QtCore.QEvent.Type.MouseButtonPress:
            super(LongTextEdit, self).mousePressEvent(event)
            if event.button() == PyQt6.QtCore.Qt.MouseButton.RightButton: # execute different code if right click
                self.contextMenuOpen()

class MainWindow(PyQt6.QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.window_width = 1024
        self.window_height = 720
        self.setWindowIcon(PyQt6.QtGui.QIcon('icons\\appicon.ico'))
        self.setWindowTitle("Mega Man ZX Editor")
        self.temp_path = f"{os.path.curdir}\\temp\\"
        self.rom = ndspy.rom.NintendoDSRom
        self.sdat = ndspy.soundArchive.SDAT
        self.arm9 = ndspy.code.MainCodeFile
        self.arm7 = ndspy.code.MainCodeFile
        self.base_address = 0
        self.relative_adress = 0
        self.romToEdit_name = ''
        self.romToEdit_ext = ''
        self.fileToEdit_name = ''
        self.fileDisplayRaw = False # Display file in 'raw'(hex) format. Else, diplayed in readable format
        self.fileDisplayMode = "Adapt" # Modes: Adapt, Binary, English dialogue, Japanese dialogue, Graphics, Sound, Movie, Code
        self.fileDisplayState = "None" # Same states as mode
        self.gfx_palette = [0xff000000+((0x0b7421*i)%0x1000000) for i in range(256)]
        self.resize(self.window_width, self.window_height)
        self.theme_index = 0
        self.displayBase = 16
        self.displayAlphanumeric = True
        self.firstLaunch = True
        self.load_preferences()
        self.UiComponents()
        self.show()

    def load_preferences(self):
        #SETTINGS
        library.init_readwrite.load_preferences(self, "SETTINGS", struct="int", exc=["displayAlphanumeric"])
        library.init_readwrite.load_preferences(self, "SETTINGS", struct="bool", inc=["displayAlphanumeric"])
        #MISC
        library.init_readwrite.load_preferences(self, "MISC", struct="bool")
        if self.firstLaunch:
            firstLaunch_dialog = PyQt6.QtWidgets.QMessageBox()
            firstLaunch_dialog.setWindowTitle("First Launch")
            firstLaunch_dialog.setWindowIcon(PyQt6.QtGui.QIcon('icons\\information.png'))
            firstLaunch_dialog.setText("Editor's current features:\n- English dialogue text editor\n- Patcher(no patches available yet)\nWIP:\n- Graphics editor\n- Sound data editor\n- VX file editor")
            firstLaunch_dialog.exec()

    def toggle_widget_icon(self, widget: PyQt6.QtWidgets.QWidget, checkedicon: PyQt6.QtGui.QImage, uncheckedicon: PyQt6.QtGui.QImage):
        if widget.isChecked():
            widget.setIcon(checkedicon)
        else:
            widget.setIcon(uncheckedicon)
    
    def UiComponents(self):
        # reusable
        self.progress = PyQt6.QtWidgets.QProgressBar()
        self.progress.resize(250, 35)
        self.progress.setWindowTitle("Progress")
        self.progress.setValue(0)
        self.progress.hide()
        # Menus
        self.openAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icons\\folder-horizontal-open.png'), '&Open', self)        
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.setStatusTip('Open ROM')
        self.openAction.triggered.connect(self.openCall)

        self.exportAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icons\\blueprint--arrow.png'), '&Export...', self)        
        self.exportAction.setShortcut('Ctrl+E')
        self.exportAction.setStatusTip('Export file in binary or converted format')
        self.exportAction.triggered.connect(lambda: self.exportCall(self.tree.currentItem()))
        self.exportAction.setDisabled(True)

        self.replaceAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icons\\blue-document-import.png'), '&Replace...', self)
        self.replaceAction.setShortcut('Ctrl+R')
        self.replaceAction.setStatusTip('replace with file in binary or converted format')
        self.replaceAction.triggered.connect(lambda: self.replaceCall(self.tree.currentItem()))

        self.replacebynameAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icons\\blue-document-import.png'), '&Replace by name...', self)        
        self.replacebynameAction.setStatusTip('replace with file of same name in binary or converted format')
        self.replacebynameAction.triggered.connect(self.replacebynameCall)

        self.menu_bar = self.menuBar()
        self.fileMenu = self.menu_bar.addMenu('&File')
        self.fileMenu.addActions([self.openAction, self.exportAction])
        self.importSubmenu = self.fileMenu.addMenu('&Import...')
        self.importSubmenu.setIcon(PyQt6.QtGui.QIcon('icons\\blue-document-import.png'))
        self.importSubmenu.addActions([self.replaceAction, self.replacebynameAction])
        self.importSubmenu.setDisabled(True)


        self.dialog_about = PyQt6.QtWidgets.QDialog(self)
        self.dialog_about.setWindowIcon(PyQt6.QtGui.QIcon('icons\\information.png'))
        self.dialog_about.setWindowTitle("About Mega Man ZX Editor")
        self.dialog_about.resize(500, 500)
        self.text_about = PyQt6.QtWidgets.QTextBrowser(self.dialog_about)
        self.text_about.resize(self.dialog_about.width(), self.dialog_about.height())
        self.text_about.setText(f"Supports:\nMEGAMANZX (Mega Man ZX)\nMEGAMANZXA (Mega Man ZX Advent)\n\nVersionning:\nEditor version: {EDITOR_VERSION} (final objective(s) completed, major functional features, WIP features)\nPython version: 3.11.4 (your version is {platform.python_version()})\nPyQt version: 6.5.2 (your version is {PyQt6.QtCore.PYQT_VERSION_STR})\nNDSPy version: 4.1.0 (your version is {list(ndspy.VERSION)[0]}.{list(ndspy.VERSION)[1]}.{list(ndspy.VERSION)[2]})\n")
        self.aboutAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icons\\information.png'), '&About', self)
        self.aboutAction.setStatusTip('Show information about the application')
        self.aboutAction.triggered.connect(lambda: self.dialog_about.exec())

        self.dialog_settings = PyQt6.QtWidgets.QDialog(self)
        self.dialog_settings.setWindowTitle("Settings")
        self.dialog_settings.resize(100, 50)
        self.dialog_settings.setLayout(PyQt6.QtWidgets.QGridLayout())
        self.label_theme = PyQt6.QtWidgets.QLabel("Theme", self.dialog_settings)
        self.dropdown_theme = PyQt6.QtWidgets.QComboBox(self.dialog_settings)
        self.dropdown_theme.activated.connect(lambda: self.switch_theme())
        self.dropdown_theme.addItems(PyQt6.QtWidgets.QStyleFactory.keys())
        self.dropdown_theme.addItem("Custom")
        self.switch_theme(True)# Update theme dropdown with current option
        self.label_base = PyQt6.QtWidgets.QLabel("Numeric Base", self.dialog_settings)
        self.field_base = PyQt6.QtWidgets.QSpinBox(self.dialog_settings)
        self.field_base.setValue(self.displayBase)
        self.field_base.setRange(-1000, 1000)
        self.field_base.editingFinished.connect(lambda: setattr(self, "displayBase", self.field_base.value()))
        self.field_base.editingFinished.connect(lambda: self.reloadCall(True))
        self.label_alphanumeric = PyQt6.QtWidgets.QLabel("Alphanumeric Numbers", self.dialog_settings)
        self.checkbox_alphanumeric = PyQt6.QtWidgets.QCheckBox(self.dialog_settings)
        self.checkbox_alphanumeric.setChecked(self.displayAlphanumeric)
        self.checkbox_alphanumeric.toggled.connect(lambda: setattr(self, "displayAlphanumeric", not self.displayAlphanumeric))
        self.checkbox_alphanumeric.toggled.connect(lambda: self.reloadCall(True))
        self.dialog_settings.layout().addWidget(self.label_theme)
        self.dialog_settings.layout().addWidget(self.dropdown_theme)
        self.dialog_settings.layout().addWidget(self.label_base)
        self.dialog_settings.layout().addWidget(self.field_base)
        self.dialog_settings.layout().addWidget(self.label_alphanumeric)
        self.dialog_settings.layout().addWidget(self.checkbox_alphanumeric)

        self.settingsAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icons\\gear.png'), '&Settings', self)
        self.settingsAction.setStatusTip('Settings')
        self.settingsAction.triggered.connect(lambda: self.dialog_settings.exec())

        self.exitAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icons\\door.png'), '&Exit', self)
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.exitCall)

        self.appMenu = self.menu_bar.addMenu('&Application')
        self.appMenu.addActions([self.aboutAction, self.settingsAction, self.exitAction])

        self.displayRawAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icons\\brain.png'), '&Converted formats', self)
        self.displayRawAction.setStatusTip('Displays files in a readable format instead of hex format.')
        self.displayRawAction.setCheckable(True)
        self.displayRawAction.setChecked(True)
        self.displayRawAction.triggered.connect(self.display_format_toggleCall)

        self.viewAdaptAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icons\\document-node.png'), '&Adapt', self)
        self.viewAdaptAction.setStatusTip('Files will be decrypted on a case per case basis.')
        self.viewAdaptAction.setCheckable(True)
        self.viewAdaptAction.setChecked(True)
        self.viewAdaptAction.triggered.connect(lambda: setattr(self, "fileDisplayMode", "Adapt"))
        self.viewAdaptAction.triggered.connect(lambda: self.treeCall(False))

        self.viewEndialogAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icons\\document-text.png'), '&English Dialogue', self)
        self.viewEndialogAction.setStatusTip('Files will be decrypted as in-game english dialogues.')
        self.viewEndialogAction.setCheckable(True)
        self.viewEndialogAction.triggered.connect(lambda: setattr(self, "fileDisplayMode", "English dialogue"))
        self.viewEndialogAction.triggered.connect(lambda: self.treeCall(False))

        self.viewGraphicAction = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icons\\appicon.ico'), '&Graphics', self)
        self.viewGraphicAction.setStatusTip('Files will be decrypted as graphics.')
        self.viewGraphicAction.setCheckable(True)
        self.viewGraphicAction.triggered.connect(lambda: setattr(self, "fileDisplayMode", "Graphics"))
        self.viewGraphicAction.triggered.connect(lambda: self.treeCall(False))

        self.viewFormatsGroup = PyQt6.QtGui.QActionGroup(self) #group for mutually exclusive togglable items
        self.viewFormatsGroup.addAction(self.viewAdaptAction)
        self.viewFormatsGroup.addAction(self.viewEndialogAction)
        self.viewFormatsGroup.addAction(self.viewGraphicAction)

        self.viewMenu = self.menu_bar.addMenu('&View')
        self.viewMenu.addAction(self.displayRawAction)
        self.displayFormatSubmenu = self.viewMenu.addMenu(PyQt6.QtGui.QIcon('icons\\document-convert.png'), '&Set edit mode...')
        self.displayFormatSubmenu.addAction(self.viewAdaptAction)
        self.displayFormatSubmenu.addSeparator()
        self.displayFormatSubmenu.addActions(self.viewFormatsGroup.actions()[1:])

        #Toolbar
        self.toolbar = PyQt6.QtWidgets.QToolBar("Main Toolbar")
        self.toolbar.setMaximumHeight(23)
        self.addToolBar(self.toolbar)

        self.button_save = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icons\\disk.png'), "Save to ROM", self)
        self.button_save.setStatusTip("Save changes to the ROM")
        self.button_save.triggered.connect(self.saveCall)
        self.button_save.setDisabled(True)
        self.button_playtest = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icons\\control.png'), "Playtest ROM", self)
        self.button_playtest.setStatusTip("Test the ROM with currently saved changes")
        self.button_playtest.triggered.connect(self.testCall)
        self.button_playtest.setDisabled(True)
        self.button_reload = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icons\\arrow-circle-315.png'), "Reload Interface", self)
        self.button_reload.setStatusTip("Reload the displayed data(all changes that aren't saved will be lost)")
        self.button_reload.triggered.connect(self.reloadCall)
        self.button_sdat = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icons\\speaker-volume.png'), "Open Sound Data Archive", self)
        self.button_sdat.setStatusTip("Show the contents of this ROM's sdat file")
        self.button_sdat.triggered.connect(self.sdatOpenCall)
        self.button_sdat.setDisabled(True)
        #self.button_codeedit = PyQt6.QtGui.QAction(PyQt6.QtGui.QIcon('icons\\document-text.png'), "Open code", self)
        #self.button_codeedit.setStatusTip("Edit the ROM's code")
        #self.button_codeedit.triggered.connect(self.codeeditCall)
        #self.button_codeedit.setDisabled(True)
        self.toolbar.addActions([self.button_save, self.button_playtest, self.button_sdat, self.button_reload])
        self.toolbar.addSeparator()

        #Tabs
        self.tabs = PyQt6.QtWidgets.QTabWidget(self)
        self.setCentralWidget(self.tabs)
        self.tabs.resize(self.width(), self.height())
        self.tabs.currentChanged.connect(lambda: self.reloadCall(True))

        self.page_explorer = PyQt6.QtWidgets.QWidget(self.tabs)
        self.page_explorer.setLayout(PyQt6.QtWidgets.QHBoxLayout())

        self.page_leveleditor = PyQt6.QtWidgets.QWidget(self.tabs)
        self.page_leveleditor.setLayout(PyQt6.QtWidgets.QHBoxLayout())

        self.page_tweaks = PyQt6.QtWidgets.QWidget(self.tabs)
        self.page_tweaks.setLayout(PyQt6.QtWidgets.QVBoxLayout())

        self.page_patches = PyQt6.QtWidgets.QWidget(self.tabs)
        self.page_patches.setLayout(PyQt6.QtWidgets.QGridLayout())

        self.tabs.addTab(self.page_explorer, "File Explorer")
        self.tabs.addTab(self.page_leveleditor, "Level Editor") # Coming Soon™
        self.tabs.addTab(self.page_tweaks, "Tweaks") # Coming Soon™
        self.tabs.addTab(self.page_patches, "Patches") # Coming Soon™

        #  ROM-related
        # File explorer
        self.tree = EditorTree(self.page_explorer)
        self.page_explorer.layout().addWidget(self.tree, 0)
        self.tree.setMaximumWidth(450)
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["File ID", "Name", "Type"])
        self.tree.setContextMenuPolicy(PyQt6.QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeUpdate()
        self.tree_called = False
        self.tree.itemSelectionChanged.connect(self.treeCall)

        self.layout_editzone = PyQt6.QtWidgets.QVBoxLayout()
        self.page_explorer.layout().addItem(self.layout_editzone)
        self.layout_editzone_row0 = PyQt6.QtWidgets.QHBoxLayout()
        self.layout_editzone_row1 = PyQt6.QtWidgets.QHBoxLayout()
        self.layout_colorpick = PyQt6.QtWidgets.QGridLayout()

        self.button_file_save = PyQt6.QtWidgets.QPushButton("Save file", self.page_explorer)
        self.button_file_save.setMaximumWidth(100)
        self.button_file_save.setToolTip("save this file's changes")
        self.button_file_save.pressed.connect(self.save_filecontent)
        self.button_file_save.setDisabled(True)
        self.button_file_save.hide()

        self.file_content = PyQt6.QtWidgets.QGridLayout()
        self.file_content_text = LongTextEdit(self.page_explorer)
        self.file_content_text.setSizePolicy(PyQt6.QtWidgets.QSizePolicy.Policy.Expanding, PyQt6.QtWidgets.QSizePolicy.Policy.Expanding)
        font = PyQt6.QtGui.QFont("Monospace")
        font.setStyleHint(PyQt6.QtGui.QFont.StyleHint.TypeWriter)
        self.file_content_text.setFont(font)
        self.file_content_text.setContextMenuPolicy(PyQt6.QtCore.Qt.ContextMenuPolicy.NoContextMenu)
        self.file_content_text.textChanged.connect(lambda: self.button_file_save.setDisabled(False))
        self.file_content_text.setDisabled(True)

        self.checkbox_textoverwite = PyQt6.QtWidgets.QCheckBox("Overwite\n existing text", self.page_explorer)
        self.checkbox_textoverwite.setStatusTip("With this enabled, writing text won't change filesize")
        self.checkbox_textoverwite.clicked.connect(lambda: self.file_content_text.setOverwriteMode(not self.file_content_text.overwriteMode()))
        self.checkbox_textoverwite.hide()
        self.layout_editzone_row1.addWidget(self.checkbox_textoverwite)

        self.file_content_gfx = GFXView(self.page_explorer)
        self.file_content_gfx.setSizePolicy(PyQt6.QtWidgets.QSizePolicy.Policy.Expanding, PyQt6.QtWidgets.QSizePolicy.Policy.Expanding)
        self.file_content_gfx.hide()
        self.file_content.addWidget(self.file_content_gfx)
        self.file_content.addWidget(self.file_content_text)

        self.dropdown_gfx_depth = PyQt6.QtWidgets.QComboBox(self.page_explorer)
        self.dropdown_gfx_depth.addItems(["1bpp", "4bpp", "8bpp"])# order of names is determined by the enum in dataconverter
        self.dropdown_gfx_depth.currentTextChanged.connect(self.treeCall)# Update gfx with current depth
        self.dropdown_gfx_depth.hide()

        self.font_caps = PyQt6.QtGui.QFont()
        self.font_caps.setCapitalization(PyQt6.QtGui.QFont.Capitalization.AllUppercase)
        
        #Address bar
        self.field_address = BetterSpinBox(self.page_explorer)
        self.field_address.numfill = 8
        self.field_address.setFont(self.font_caps)
        self.field_address.setValue(self.base_address+self.relative_adress)
        #self.field_address.setPrefix("0x")
        self.field_address.setDisplayIntegerBase(self.displayBase)
        #self.field_address.textChanged.connect(lambda: self.value_update_Call("relative_adress", library.dataconverter.baseToInt(library.dataconverter.strToBase(self.field_address.text()), self.field_address.displayIntegerBase()) - self.base_address, True))
        self.field_address.textChanged.connect(lambda: self.value_update_Call("relative_adress", self.field_address.valueFromText(self.field_address.text()) - self.base_address, True))
        self.field_address.setDisabled(True)
        self.field_address.hide()
        #notes
        self.label_file_size = PyQt6.QtWidgets.QLabel(self.page_explorer)
        self.label_file_size.setText("Size: N/A")
        self.label_file_size.hide()
        #Tile Wifth
        self.tile_width = 8
        self.field_tile_width = BetterSpinBox(self.page_explorer)
        self.field_tile_width.setStatusTip(f"Set depth to 1bpp and tile width to {library.dataconverter.StrFromNumber(16, self.displayBase, self.displayAlphanumeric)} for JP font")
        self.field_tile_width.setFont(self.font_caps)
        self.field_tile_width.setValue(self.tile_width)
        self.field_tile_width.setDisplayIntegerBase(self.displayBase)
        self.field_tile_width.valueChanged.connect(lambda: self.value_update_Call("tile_width", self.field_tile_width.valueFromText(self.field_tile_width.text()), True)) 
        self.field_tile_width.hide()

        self.label_tile_width = PyQt6.QtWidgets.QLabel(self.page_explorer)
        self.label_tile_width.setText(" width")
        self.label_tile_width.hide()

        self.layout_tile_width = PyQt6.QtWidgets.QVBoxLayout()
        self.layout_tile_width.addWidget(self.field_tile_width)
        self.layout_tile_width.addWidget(self.label_tile_width)
        self.layout_tile_width.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignTop)
        #Tile Height
        self.tile_height = 8
        self.field_tile_height = BetterSpinBox(self.page_explorer)
        self.field_tile_height.setFont(self.font_caps)
        self.field_tile_height.setValue(self.tile_height)
        self.field_tile_height.setDisplayIntegerBase(self.displayBase)
        self.field_tile_height.valueChanged.connect(lambda: self.value_update_Call("tile_height", self.field_tile_height.valueFromText(self.field_tile_height.text()), True)) 
        self.field_tile_height.hide()

        self.label_tile_height = PyQt6.QtWidgets.QLabel(self.page_explorer)
        self.label_tile_height.setText(" height")
        self.label_tile_height.hide()

        self.layout_tile_height = PyQt6.QtWidgets.QVBoxLayout()
        self.layout_tile_height.addWidget(self.field_tile_height)
        self.layout_tile_height.addWidget(self.label_tile_height)
        self.layout_tile_height.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignTop)
        #Tiles Per row
        self.tiles_per_row = 8
        self.field_tiles_per_row = BetterSpinBox(self.page_explorer)
        self.field_tiles_per_row.setFont(self.font_caps)
        self.field_tiles_per_row.setValue(self.tiles_per_row)
        self.field_tiles_per_row.setDisplayIntegerBase(self.displayBase)
        self.field_tiles_per_row.valueChanged.connect(lambda: self.value_update_Call("tiles_per_row", self.field_tiles_per_row.valueFromText(self.field_tiles_per_row.text()), True)) 
        self.field_tiles_per_row.hide()

        self.label_tiles_per_row = PyQt6.QtWidgets.QLabel(self.page_explorer)
        self.label_tiles_per_row.setText(" columns")
        self.label_tiles_per_row.hide()

        self.layout_tiles_per_row = PyQt6.QtWidgets.QVBoxLayout()
        self.layout_tiles_per_row.addWidget(self.field_tiles_per_row)
        self.layout_tiles_per_row.addWidget(self.label_tiles_per_row)
        self.layout_tiles_per_row.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignTop)
        #Tiles Per Column
        self.tiles_per_column = 16
        self.field_tiles_per_column = BetterSpinBox(self.page_explorer)
        self.field_tiles_per_column.setFont(self.font_caps)
        self.field_tiles_per_column.setValue(self.tiles_per_column)
        self.field_tiles_per_column.setDisplayIntegerBase(self.displayBase)
        self.field_tiles_per_column.valueChanged.connect(lambda: self.value_update_Call("tiles_per_column", self.field_tiles_per_column.valueFromText(self.field_tiles_per_column.text()), True)) 
        self.field_tiles_per_column.hide()

        self.label_tiles_per_column = PyQt6.QtWidgets.QLabel(self.page_explorer)
        self.label_tiles_per_column.setText(" rows")
        self.label_tiles_per_column.hide()

        self.layout_tiles_per_column = PyQt6.QtWidgets.QVBoxLayout()
        self.layout_tiles_per_column.addWidget(self.field_tiles_per_column)
        self.layout_tiles_per_column.addWidget(self.label_tiles_per_column)
        self.layout_tiles_per_column.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignTop)

        #Palettes
        for i in range(256): #setup default palette
            setattr(self, f"button_palettepick_{i}", HoldButton(self.page_explorer))
            button_palettepick: HoldButton = getattr(self, f"button_palettepick_{i}")

            button_palettepick.timeout_func = [lambda color_index=i: self.ColorpickCall(color_index)] #lambda color_index=i: print(f"button {color_index} pressed")
            button_palettepick.allow_press = True
            button_palettepick.press_quick_threshold = 1
            button_palettepick.setStyleSheet(f"background-color: #{self.gfx_palette[i]:00x}; color: white;")
            button_palettepick.setMaximumSize(10, 10)
            self.layout_colorpick.addWidget(button_palettepick, int(i/16), int(i%16))
            button_palettepick.hide()

        self.layout_editzone_row1.addItem(self.layout_colorpick)
        self.layout_editzone_row1.addItem(self.layout_tile_width)
        self.layout_editzone_row1.addItem(self.layout_tile_height)
        self.layout_editzone_row1.addItem(self.layout_tiles_per_row)
        self.layout_editzone_row1.addItem(self.layout_tiles_per_column)

        self.layout_editzone_row0.addWidget(self.button_file_save)
        self.layout_editzone_row0.addWidget(self.label_file_size)
        self.layout_editzone_row0.addWidget(self.dropdown_gfx_depth)
        self.layout_editzone_row0.addWidget(self.field_address)

        self.layout_editzone.addItem(self.layout_editzone_row0)
        self.layout_editzone.addItem(self.layout_editzone_row1)
        self.layout_editzone.addItem(self.file_content)

        #Sound Data Archive
        self.dialog_sdat = PyQt6.QtWidgets.QMdiSubWindow()
        self.dialog_sdat.setWindowTitle("Sound Data Archive")
        self.dialog_sdat.setWindowIcon(PyQt6.QtGui.QIcon('icons\\speaker-volume.png'))
        self.dialog_sdat.resize(600, 400)

        self.tree_sdat = EditorTree(self.dialog_sdat)
        self.dialog_sdat.layout().addWidget(self.tree_sdat)
        self.tree_sdat.setColumnCount(3)
        self.tree_sdat.setHeaderLabels(["File ID", "Name", "Type"])
        self.tree_sdat.setContextMenuPolicy(PyQt6.QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        #VX
        self.label_vxHeader_length = PyQt6.QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_length.setText("Duration(frames): ")
        self.label_vxHeader_length.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_vxHeader_length.hide()
        self.field_vxHeader_length = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_length.setMinimum(0x00000000) # prevent impossible values
        self.field_vxHeader_length.numfill = 4
        self.field_vxHeader_length.hide()
        self.field_vxHeader_length.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_length = PyQt6.QtWidgets.QVBoxLayout()
        self.layout_vxHeader_length.addWidget(self.label_vxHeader_length)
        self.layout_vxHeader_length.addWidget(self.field_vxHeader_length)

        self.label_vxHeader_framerate = PyQt6.QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_framerate.setText("Frame rate: ")
        self.label_vxHeader_framerate.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_vxHeader_framerate.hide()
        self.field_vxHeader_framerate = PyQt6.QtWidgets.QLineEdit(self.page_explorer)
        #self.field_vxHeader_framerate.setRange(0x0000,0xFFFF) # prevent impossible values
        #self.field_vxHeader_framerate.numfill = 4
        self.field_vxHeader_framerate.hide()
        self.field_vxHeader_framerate.textChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_framerate = PyQt6.QtWidgets.QVBoxLayout()
        self.layout_vxHeader_framerate.addWidget(self.label_vxHeader_framerate)
        self.layout_vxHeader_framerate.addWidget(self.field_vxHeader_framerate)

        self.label_vxHeader_frameSizeMax = PyQt6.QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_frameSizeMax.setText("Maximal frame data size: ")
        self.label_vxHeader_frameSizeMax.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_vxHeader_frameSizeMax.hide()
        self.field_vxHeader_frameSizeMax = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_frameSizeMax.setMinimum(0x00000000) # prevent impossible values
        self.field_vxHeader_frameSizeMax.numfill = 4
        self.field_vxHeader_frameSizeMax.hide()
        self.field_vxHeader_frameSizeMax.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_frameSizeMax = PyQt6.QtWidgets.QVBoxLayout()
        self.layout_vxHeader_frameSizeMax.addWidget(self.label_vxHeader_frameSizeMax)
        self.layout_vxHeader_frameSizeMax.addWidget(self.field_vxHeader_frameSizeMax)

        self.layout_vx_framesHeader = PyQt6.QtWidgets.QHBoxLayout()
        self.layout_vx_framesHeader.addItem(self.layout_vxHeader_length)
        self.layout_vx_framesHeader.addItem(self.layout_vxHeader_framerate)
        self.layout_vx_framesHeader.addItem(self.layout_vxHeader_frameSizeMax)

        self.label_vxHeader_streamCount = PyQt6.QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_streamCount.setText("Audio stream count: ")
        self.label_vxHeader_streamCount.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_vxHeader_streamCount.hide()
        self.field_vxHeader_streamCount = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_streamCount.setMinimum(0x00000000) # prevent impossible values
        self.field_vxHeader_streamCount.numfill = 4
        self.field_vxHeader_streamCount.hide()
        self.field_vxHeader_streamCount.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_streamCount = PyQt6.QtWidgets.QVBoxLayout()
        self.layout_vxHeader_streamCount.addWidget(self.label_vxHeader_streamCount)
        self.layout_vxHeader_streamCount.addWidget(self.field_vxHeader_streamCount)

        self.label_vxHeader_sampleRate = PyQt6.QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_sampleRate.setText("Sound sample rate(Hz): ")
        self.label_vxHeader_sampleRate.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_vxHeader_sampleRate.hide()
        self.field_vxHeader_sampleRate = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_sampleRate.setMinimum(0x00000000) # prevent impossible values
        self.field_vxHeader_sampleRate.numfill = 4
        self.field_vxHeader_sampleRate.hide()
        self.field_vxHeader_sampleRate.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_sampleRate = PyQt6.QtWidgets.QVBoxLayout()
        self.layout_vxHeader_sampleRate.addWidget(self.label_vxHeader_sampleRate)
        self.layout_vxHeader_sampleRate.addWidget(self.field_vxHeader_sampleRate)

        self.label_vxHeader_audioExtraDataOffset = PyQt6.QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_audioExtraDataOffset.setText("Extra audio data offset: ")
        self.label_vxHeader_audioExtraDataOffset.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_vxHeader_audioExtraDataOffset.hide()
        self.field_vxHeader_audioExtraDataOffset = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_audioExtraDataOffset.setMinimum(0x00000000) # prevent impossible values
        self.field_vxHeader_audioExtraDataOffset.numfill = 4
        self.field_vxHeader_audioExtraDataOffset.hide()
        self.field_vxHeader_audioExtraDataOffset.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_audioExtraDataOffset = PyQt6.QtWidgets.QVBoxLayout()
        self.layout_vxHeader_audioExtraDataOffset.addWidget(self.label_vxHeader_audioExtraDataOffset)
        self.layout_vxHeader_audioExtraDataOffset.addWidget(self.field_vxHeader_audioExtraDataOffset)

        self.layout_vx_soundHeader = PyQt6.QtWidgets.QHBoxLayout()
        self.layout_vx_soundHeader.addItem(self.layout_vxHeader_streamCount)
        self.layout_vx_soundHeader.addItem(self.layout_vxHeader_sampleRate)
        self.layout_vx_soundHeader.addItem(self.layout_vxHeader_audioExtraDataOffset)

        self.label_vxHeader_width = PyQt6.QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_width.setText("Frame width(pixels): ")
        self.label_vxHeader_width.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_vxHeader_width.hide()
        self.field_vxHeader_width = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_width.setMinimum(0x00000000) # prevent impossible values
        self.field_vxHeader_width.numfill = 4
        self.field_vxHeader_width.hide()
        self.field_vxHeader_width.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_width = PyQt6.QtWidgets.QVBoxLayout()
        self.layout_vxHeader_width.addWidget(self.label_vxHeader_width)
        self.layout_vxHeader_width.addWidget(self.field_vxHeader_width)

        self.label_vxHeader_height = PyQt6.QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_height.setText("Frame height(pixels): ")
        self.label_vxHeader_height.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_vxHeader_height.hide()
        self.field_vxHeader_height = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_height.setMinimum(0x00000000) # prevent impossible values
        self.field_vxHeader_height.numfill = 4
        self.field_vxHeader_height.hide()
        self.field_vxHeader_height.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_height = PyQt6.QtWidgets.QVBoxLayout()
        self.layout_vxHeader_height.addWidget(self.label_vxHeader_height)
        self.layout_vxHeader_height.addWidget(self.field_vxHeader_height)

        self.layout_vx_frameSize = PyQt6.QtWidgets.QHBoxLayout()
        self.layout_vx_frameSize.addItem(self.layout_vxHeader_width)
        self.layout_vx_frameSize.addItem(self.layout_vxHeader_height)

        self.label_vxHeader_quantiser = PyQt6.QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_quantiser.setText("Quantiser: ")
        self.label_vxHeader_quantiser.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_vxHeader_quantiser.hide()
        self.field_vxHeader_quantiser = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_quantiser.setMinimum(0x00000000) # prevent impossible values
        self.field_vxHeader_quantiser.numfill = 4
        self.field_vxHeader_quantiser.hide()
        self.field_vxHeader_quantiser.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_quantiser = PyQt6.QtWidgets.QVBoxLayout()
        self.layout_vxHeader_quantiser.addWidget(self.label_vxHeader_quantiser)
        self.layout_vxHeader_quantiser.addWidget(self.field_vxHeader_quantiser)

        self.label_vxHeader_seekTableOffset = PyQt6.QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_seekTableOffset.setText("Seek table offset: ")
        self.label_vxHeader_seekTableOffset.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_vxHeader_seekTableOffset.hide()
        self.field_vxHeader_seekTableOffset = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_seekTableOffset.setMinimum(0x00000000) # prevent impossible values
        self.field_vxHeader_seekTableOffset.numfill = 4
        self.field_vxHeader_seekTableOffset.hide()
        self.field_vxHeader_seekTableOffset.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_seekTableOffset = PyQt6.QtWidgets.QVBoxLayout()
        self.layout_vxHeader_seekTableOffset.addWidget(self.label_vxHeader_seekTableOffset)
        self.layout_vxHeader_seekTableOffset.addWidget(self.field_vxHeader_seekTableOffset)

        self.label_vxHeader_seekTableEntryCount = PyQt6.QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_seekTableEntryCount.setText("Seek table entry count: ")
        self.label_vxHeader_seekTableEntryCount.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_vxHeader_seekTableEntryCount.hide()
        self.field_vxHeader_seekTableEntryCount = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_seekTableEntryCount.setMinimum(0x00000000) # prevent impossible values
        self.field_vxHeader_seekTableEntryCount.numfill = 4
        self.field_vxHeader_seekTableEntryCount.hide()
        self.field_vxHeader_seekTableEntryCount.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_seekTableEntryCount = PyQt6.QtWidgets.QVBoxLayout()
        self.layout_vxHeader_seekTableEntryCount.addWidget(self.label_vxHeader_seekTableEntryCount)
        self.layout_vxHeader_seekTableEntryCount.addWidget(self.field_vxHeader_seekTableEntryCount)

        self.layout_vx_seekTable = PyQt6.QtWidgets.QHBoxLayout()
        self.layout_vx_seekTable.addItem(self.layout_vxHeader_seekTableOffset)
        self.layout_vx_seekTable.addItem(self.layout_vxHeader_seekTableEntryCount)

        self.file_content.addItem(self.layout_vx_framesHeader)
        self.file_content.addItem(self.layout_vx_soundHeader)
        self.file_content.addItem(self.layout_vx_frameSize)
        self.file_content.addItem(self.layout_vxHeader_quantiser)
        self.file_content.addItem(self.layout_vx_seekTable)

        # Level Editor(Coming Soon™)
        self.layout_level_editpannel = PyQt6.QtWidgets.QVBoxLayout()

        self.dropdown_editor_area = PyQt6.QtWidgets.QComboBox(self.page_leveleditor)
        self.dropdown_editor_area.setToolTip("Choose an area to modify")
        self.gfx_scene_level = GFXView()


        self.page_leveleditor.layout().addItem(self.layout_level_editpannel)
        self.layout_level_editpannel.addWidget(self.dropdown_editor_area)

        self.page_leveleditor.layout().addWidget(self.gfx_scene_level)

        # Tweaks(Coming Soon™)
        self.tabs_tweaks = PyQt6.QtWidgets.QTabWidget(self.page_tweaks)

        self.dropdown_tweak_target = PyQt6.QtWidgets.QComboBox(self.page_tweaks)
        self.dropdown_tweak_target.setGeometry(125, 75, 125, 25)
        self.dropdown_tweak_target.setToolTip("Choose a target to appy tweaks to")
        self.dropdown_tweak_target.addItems(["Other", "Player", "Player(Hu)", "Player(X)", "Player(Zx)", "Player(Hx)", "Player(Fx)", "Player(Lx)", "Player(Px)", "Player(Ox)"])# order of names is determined by the enum in dataconverter
        #self.dropdown_tweak_target.currentTextChanged.connect(self.tweakTargetCall)
        self.dropdown_tweak_target.hide()
        self.page_tweaks.layout().addWidget(self.dropdown_tweak_target)
        self.page_tweaks.layout().addWidget(self.tabs_tweaks)

        self.page_tweaks_stats = PyQt6.QtWidgets.QWidget(self.tabs_tweaks)
        self.page_tweaks_stats.setLayout(PyQt6.QtWidgets.QGridLayout())

        self.page_tweaks_physics = PyQt6.QtWidgets.QWidget(self.tabs_tweaks)
        self.page_tweaks_physics.setLayout(PyQt6.QtWidgets.QGridLayout())

        self.page_tweaks_behaviour = PyQt6.QtWidgets.QWidget(self.tabs_tweaks)
        self.page_tweaks_behaviour.setLayout(PyQt6.QtWidgets.QGridLayout())

        self.page_tweaks_animations = PyQt6.QtWidgets.QWidget(self.tabs_tweaks)
        self.page_tweaks_animations.setLayout(PyQt6.QtWidgets.QGridLayout())

        self.page_tweaks_misc = PyQt6.QtWidgets.QWidget(self.tabs_tweaks)
        self.page_tweaks_misc.setLayout(PyQt6.QtWidgets.QGridLayout())

        self.tabs_tweaks.addTab(self.page_tweaks_stats, "Stats")


        self.tabs_tweaks.addTab(self.page_tweaks_physics, "Physics")


        self.tabs_tweaks.addTab(self.page_tweaks_behaviour, "Behaviour")

        self.checkbox_paralyzed = PyQt6.QtWidgets.QCheckBox(self.page_tweaks_behaviour)
        self.page_tweaks_behaviour.layout().addWidget(self.checkbox_paralyzed)


        self.tabs_tweaks.addTab(self.page_tweaks_animations, "Animations")


        self.tabs_tweaks.addTab(self.page_tweaks_misc, "Misc.")


        # Patches
        self.tree_patches = EditorTree(self.page_patches)
        self.page_patches.layout().addWidget(self.tree_patches)
        self.tree_patches.setColumnCount(4)
        self.tree_patches.setHeaderLabels(["Enabed", "Address", "Name", "Type", "Size"])
        self.tree_patches.itemChanged.connect(self.patch_game)
        self.tree_patches_checkboxes = []
        self.ispatching = False

        # Shortcuts
        #PyQt6.QtWidgets.QKeySequenceEdit()

        self.setStatusBar(PyQt6.QtWidgets.QStatusBar(self))
    
    def runTasks(self, runnable_list: list):
        activeThreadCount = PyQt6.QtCore.QThreadPool.globalInstance().activeThreadCount()
        #self.setWindowTitle(f"{self.windowTitle()} Running {activeThreadCount} Threads")
        pool = PyQt6.QtCore.QThreadPool.globalInstance()
        for runnable in runnable_list:
            # 2. Instantiate the subclass of QRunnable
            runnable_inst = runnable(activeThreadCount)
            app.processEvents()
            if runnable == RunnableDisplayRawText:
                #runnable_inst.signals.signal_RunnableDisplayRawText.connect(self.file_content_text.setPlainText)
                pass
            # 3. Call start()
            pool.start(runnable_inst)

    def clearTasks(self):
        pool = PyQt6.QtCore.QThreadPool.globalInstance()
        pool.clear()

    def set_dialog_button_name(self, dialog: PyQt6.QtWidgets.QDialog, oldtext: str, newtext: str):
        for btn in dialog.findChildren(PyQt6.QtWidgets.QPushButton):
            if btn.text() == self.tr(oldtext):
                PyQt6.QtCore.QTimer.singleShot(0, lambda btn=btn: btn.setText(newtext))
        dialog.findChild(PyQt6.QtWidgets.QTreeView).selectionModel().currentChanged.connect(
            lambda: self.set_dialog_button_name(dialog, "&Open", "Import")
            )
    
    def patches_reload(self):
        if self.tree_patches_numbase != self.displayBase or self.tree_patches_numaplha != self.displayAlphanumeric:
            #self.progress.show()
            self.tree_patches.clear()
            if self.rom.name.decode().replace(" ", "_") in library.patchdata.GameEnum.__members__:
                patches = []
                for patch in library.patchdata.GameEnum[self.rom.name.decode().replace(" ", "_")].value[1]:
                    #self.progress.setValue(self.progress.value()+12)
                    #PyQt6.QtWidgets.QTreeWidgetItem(None, ["", "<address>", "<patch name>", "<patch type>", "<size>"])
                    if type(patch[2]) == type([]): # if patch contains patches
                        patch_item = PyQt6.QtWidgets.QTreeWidgetItem(None, ["", "N/A", patch[0], patch[1], "0"])
                        patches.append(patch_item)
                        patch_size = 0
                        subPatchMatches = 0
                        for subPatch in patch:
                            if type(subPatch) == type([]):
                                subPatch_item = PyQt6.QtWidgets.QTreeWidgetItem(None, ["", str(library.dataconverter.StrFromNumber(subPatch[0], self.displayBase, self.displayAlphanumeric).zfill(8)), subPatch[1], "Patch Segment", str(library.dataconverter.StrFromNumber(len(subPatch[3].replace("-", "")), self.displayBase, self.displayAlphanumeric).zfill(1))])
                                subPatch_item.setToolTip(0, subPatch[3])
                                subPatch_item.setFlags(patch_item.flags() | PyQt6.QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                                patch_item.addChild(subPatch_item)
                                patch_size += len(subPatch[3].replace("-", ""))
                                if self.rom.save()[subPatch[0]:subPatch[0]+len(subPatch[3])] == subPatch[3]:
                                    subPatchMatches += 1
                                    subPatch_item.setCheckState(0, PyQt6.QtCore.Qt.CheckState.Checked)
                                else:
                                    subPatch_item.setCheckState(0, PyQt6.QtCore.Qt.CheckState.Unchecked)
                                self.tree_patches_checkboxes.append(subPatch_item.checkState(0))
                        patch_item.setText(4, f"{library.dataconverter.StrFromNumber(patch_size, self.displayBase, self.displayAlphanumeric).zfill(1)}")
                        patch_item.setFlags(patch_item.flags() | PyQt6.QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                        if subPatchMatches == patch_item.childCount(): # Check for already applied patches
                            patch_item.setCheckState(0, PyQt6.QtCore.Qt.CheckState.Checked)
                        elif subPatchMatches > 0:
                            patch_item.setCheckState(0, PyQt6.QtCore.Qt.CheckState.PartiallyChecked)
                        else:
                            patch_item.setCheckState(0, PyQt6.QtCore.Qt.CheckState.Unchecked)
                        self.tree_patches_checkboxes.append(patch_item.checkState(0))
                    else:
                        patch_item = PyQt6.QtWidgets.QTreeWidgetItem(None, ["", str(library.dataconverter.StrFromNumber(patch[0], self.displayBase, self.displayAlphanumeric).zfill(8)), patch[1], patch[2], str(library.dataconverter.StrFromNumber(len(patch[4].replace("-", "")), self.displayBase, self.displayAlphanumeric).zfill(1))])
                        patch_item.setToolTip(0, str(patch[4]))
                        patches.append(patch_item)
                        patch_item.setFlags(patch_item.flags() | PyQt6.QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                        if self.rom.save()[patch[0]:patch[0]+len(patch[4])] == patch[4]: # Check for already applied patches
                            patch_item.setCheckState(0, PyQt6.QtCore.Qt.CheckState.Checked)
                        else:
                            patch_item.setCheckState(0, PyQt6.QtCore.Qt.CheckState.Unchecked)
                        self.tree_patches_checkboxes.append(patch_item.checkState(0))
                self.tree_patches.addTopLevelItems(patches)
            #self.progress.setValue(100)
            #self.progress.close()
        self.tree_patches_numbase = self.displayBase
        self.tree_patches_numaplha = self.displayAlphanumeric

    def openCall(self):
        fname = PyQt6.QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "NDS Files (*.nds *.srl);; All Files (*)",
            options=PyQt6.QtWidgets.QFileDialog.Option.DontUseNativeDialog,
        )
        if not fname == ("", ""): # if file you're trying to open is not none
            self.romToEdit_name = fname[0].split("/")[len(fname[0].split("/")) - 1].rsplit(".", 1)[0]
            self.romToEdit_ext = "." + fname[0].split("/")[len(fname[0].split("/")) - 1].rsplit(".", 1)[1]
            self.rom = ndspy.rom.NintendoDSRom.fromFile(fname[0])
            try:
                self.sdat = ndspy.soundArchive.SDAT(self.rom.files[int(str(self.rom.filenames).rpartition(".sdat")[0].split()[-2])])# manually search for sdat file because getFileByName does not find it when it is in a folder
                print("SDAT at " + str(self.rom.filenames).rpartition(".sdat")[0].split()[-2])
                #self.sdat.fatLengthsIncludePadding = True
                self.button_sdat.setEnabled(True)
            except Exception:
                dialog = PyQt6.QtWidgets.QMessageBox(self)
                dialog.setWindowTitle("No SDAT")
                dialog.setWindowIcon(PyQt6.QtGui.QIcon("icons\\exclamation"))
                dialog.setText("Sound data archive was not found. \n This means that sound data may not be there or may not be in a recognizable format.")
                dialog.exec()
            self.treeSdatUpdate()
            self.arm9 = self.rom.loadArm9()
            self.arm7 = self.rom.loadArm7()
            self.temp_path = f"{os.path.curdir}\\temp\\{self.romToEdit_name+self.romToEdit_ext}"
            self.setWindowTitle("Mega Man ZX Editor" + " <" + self.rom.name.decode() + " v" + self.rom.idCode.decode("utf-8") + " rev" + str(self.rom.version) + " region" + str(self.rom.region) + ">" + " \"" + self.romToEdit_name + self.romToEdit_ext + "\"")
            #print(self.rom.filenames)
            self.tree_patches_numbase = None # set to something that isn't displaybase
            self.tree_patches_numaplha = None # set to something that isn't displayalphanumeric
            self.patches_reload()
            if not self.rom.name.decode().replace(" ", "_") in library.patchdata.GameEnum.__members__:
                print("ROM is NOT supported! Continue at your own risk!")
                dialog = PyQt6.QtWidgets.QMessageBox(self)
                dialog.setWindowTitle("Warning!")
                dialog.setWindowIcon(PyQt6.QtGui.QIcon("icons\\exclamation"))
                dialog.setText("Game \"" + self.rom.name.decode() + "\" is NOT supported! Continue at your own risk!")
                dialog.exec()

            self.tree.setCurrentItem(None)
            self.treeUpdate()
            self.enable_editing_ui()
            self.file_content_text.setDisabled(True)

    def enable_editing_ui(self):
        #self.button_codeedit.setDisabled(False)
        self.importSubmenu.setDisabled(False)
        self.button_file_save.show()
        self.button_save.setDisabled(False)
        self.button_playtest.setDisabled(False)
        self.dropdown_tweak_target.show()
        self.field_address.show()
        self.label_file_size.show()
        self.dropdown_editor_area.addItems([item.text(1) for item in self.tree.findItems("\A[a-z][0-9][0-9]", PyQt6.QtCore.Qt.MatchFlag.MatchRegularExpression, 1)])

    def exportCall(self, item: PyQt6.QtWidgets.QTreeWidgetItem):
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
                        extract(item.text(0), fileToEdit_name=str(item.text(1) + "." + item.text(2)), path=dialog.selectedFiles()[0], format=dropdown_formatselect.currentText(), tree=item.treeWidget())
                    else: # if folder
                        print("Folder " + os.path.join(dialog.selectedFiles()[0] + "/" + w.fileToEdit_name.removesuffix(".Folder")) + " will be created")
                        if os.path.exists(os.path.join(dialog.selectedFiles()[0] + "/" + w.fileToEdit_name.removesuffix(".Folder"))) == False:
                            os.makedirs(os.path.join(dialog.selectedFiles()[0] + "/" + w.fileToEdit_name.removesuffix(".Folder")))
                        print(item.childCount() - 1)
                        for i in range(item.childCount()):
                            print(item.child(i).text(0))
                            extract(item.child(i).text(0), path=dialog.selectedFiles()[0], format=dropdown_formatselect.currentText(), tree=item.treeWidget())#, w.fileToEdit_name.replace(".Folder", "/")
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
                dialog2 = PyQt6.QtWidgets.QMessageBox()
                dialog2.setWindowTitle("Import Status")
                dialog2.setWindowIcon(PyQt6.QtGui.QIcon('icons\\information.png'))
                dialog2.setText("File \"" + str(dialog.selectedFiles()).split("/")[-1].removesuffix("']") + "\" imported!")
                if str(dialog.selectedFiles()[0]).split("/")[-1].removesuffix("']") in str(self.rom.filenames): # if file you're trying to replace is in ROM
                    with open(*dialog.selectedFiles(), 'rb') as f:
                        fileEdited = f.read()
                        w.rom.setFileByName(str(dialog.selectedFiles()).split("/")[-1].removesuffix("']"), bytearray(fileEdited))
                    dialog2.exec()
                elif str(dialog.selectedFiles()[0]).split("/")[-1].removesuffix("']").split(".")[0] in [filename[filename.rfind(" ")+1:filename.find(".")] for filename in str(self.rom.filenames).split("\n")]: # if filename of file(without extension) you're trying to replace is in ROM
                    with open(*dialog.selectedFiles(), 'rb') as f:
                        fileEdited = f.read()
                        if str(dialog.selectedFiles()[0]).split("/")[-1].removesuffix("']").split(".")[1] == "txt":
                            #print(w.rom.filenames.idOf(str(dialog.selectedFiles()).split("/")[-1].removesuffix("']").replace(".txt", ".bin")))
                            w.rom.files[w.rom.filenames.idOf(str(dialog.selectedFiles()).split("/")[-1].removesuffix("']").replace(".txt", ".bin"))] = bytearray(library.dataconverter.convertdata_text_to_bin(fileEdited.decode("utf-8")))
                            dialog2.exec()
                        else:
                            PyQt6.QtWidgets.QMessageBox.critical(
                            self,
                            "Format not recognized",
                            "Please select a file that is supported by the editor."
                            )
                else:
                    PyQt6.QtWidgets.QMessageBox.critical(
                    self,
                    "File \"" + str(dialog.selectedFiles()[0]).split("/")[-1].removesuffix("']") + "\" not found in game files",
                    "Please select a file that has the same name as an existing ROM file."
                    )
                self.treeCall()

    def replaceCall(self, item: PyQt6.QtWidgets.QTreeWidgetItem):
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
                    dialog2 = PyQt6.QtWidgets.QMessageBox()
                    dialog2.setWindowTitle("Import Status")
                    dialog2.setWindowIcon(PyQt6.QtGui.QIcon('icons\\information.png'))
                    dialog2.setText("File import failed!")
                    with open(*dialog.selectedFiles(), 'rb') as f:
                        fileEdited = f.read()
                        if str(dialog.selectedFiles()[0]).split("/")[-1].removesuffix("']").split(".")[1] == "txt": # text file
                                try:
                                    if item.treeWidget() == self.tree_sdat: # implement different import method
                                        dialog2.exec()
                                        return
                                    else:
                                        #print("replacement of file with id " + w.tree.currentItem().text(0) + " was successful")
                                        w.rom.files[int(item.text(0))] = bytearray(library.dataconverter.convertdata_text_to_bin(fileEdited.decode("utf-8")))
                                except Exception as e:
                                    print(e)
                        else: # raw data
                            if item.treeWidget() == self.tree_sdat: # implement different import method
                                dialog2.exec()
                                return
                            else:
                                w.rom.files[int(item.text(0))] = bytearray(fileEdited)
                            #print("raw data replaced")
                    dialog2.setText("File \"" + str(dialog.selectedFiles()).split("/")[-1].removesuffix("']") + "\" imported!")
                    dialog2.exec()
                    self.treeCall()
    
    def switch_theme(self, isupdate=False):
        if isupdate == False:
            self.theme_index = self.dropdown_theme.currentIndex()
            library.init_readwrite.write_preferences(self)
        else:
            self.dropdown_theme.setCurrentIndex(self.theme_index) # Update dropdown with current option

        app: PyQt6.QtWidgets.QMainWindow = PyQt6.QtCore.QCoreApplication.instance()
        #print(app.style().metaObject().className())
        app.setStyle(PyQt6.QtWidgets.QCommonStyle())
        app.setStyleSheet("")
        if self.theme_index < len(PyQt6.QtWidgets.QStyleFactory.keys()):
            app.setStyle(self.dropdown_theme.itemText(self.theme_index))
        else:
            if os.path.exists('theme\\custom_theme.qss'):
                app.setStyleSheet(open('theme\\custom_theme.qss').read())
            else:
                os.mkdir("theme")
                open('theme\\custom_theme.qss', "w")
                dialog = PyQt6.QtWidgets.QMessageBox()
                dialog.setWindowTitle("No custom stylesheet found")
                dialog.setWindowIcon(PyQt6.QtGui.QIcon("icons\\exclamation"))
                dialog.setText("No custom stylesheet was found in location \"theme\\custom_theme.qss\".\nAn empty file has been created there.\nPlease put the contents of your custom stylesheet in it.\nIf you wish to create one yourself but do not know how, refer to this page:\nhttps://doc.qt.io/qtforpython-6.5/overviews/stylesheet-examples.html")
                dialog.exec()

    def exitCall(self):
        self.close()
    
    def display_format_toggleCall(self):
        self.fileDisplayRaw = not self.fileDisplayRaw
        self.displayFormatSubmenu.setDisabled(self.displayFormatSubmenu.isEnabled())
        self.toggle_widget_icon(self.displayRawAction, PyQt6.QtGui.QIcon('icons\\brain.png'), PyQt6.QtGui.QIcon('icons\\document-binary.png'))
        self.treeCall()

    def value_update_Call(self, var, val, istreecall=True):
        #print(f"{self.field_address.value():08X}" + " - " + f"{self.base_address:08X}")
        setattr(self, var, val)
        if istreecall:
            self.treeCall(True)

    def ColorpickCall(self, color_index: int):
        #print(color_index)
        button: HoldButton = getattr(self, f"button_palettepick_{color_index}")
        if button.counter >= 2:
            dialog = PyQt6.QtWidgets.QColorDialog(self)
            dialog.setOptions(PyQt6.QtWidgets.QColorDialog.ColorDialogOption.DontUseNativeDialog)
            dialog.setCurrentColor(int(button.styleSheet()[button.styleSheet().find(":")+3:button.styleSheet().find(";")], 16))
            dialog.exec()
            if dialog.selectedColor().isValid():
                button.setStyleSheet(f"background-color: {dialog.selectedColor().name()}; color: white;")
                if self.file_content_gfx.pen.color().rgba() == self.gfx_palette[color_index]:
                    self.file_content_gfx.pen.setColor(dialog.selectedColor().rgba())
                self.gfx_palette[color_index] = dialog.selectedColor().rgba()
                self.treeCall(True) # update gfx colors
        elif button.pressed_quick:
            #print(button.styleSheet())
            if color_index < 2**list(library.dataconverter.CompressionAlgorithmEnum)[self.dropdown_gfx_depth.currentIndex()].depth:
                self.file_content_gfx.pen.setColor(int(button.styleSheet()[button.styleSheet().find(":")+3:button.styleSheet().find(";")], 16))
                    
    
    def saveCall(self): #Save to external ROM
        dialog = PyQt6.QtWidgets.QFileDialog(
                self,
                "Save ROM",
                "",
                "NDS Files (*.nds *.srl);; All Files (*)",
                options=PyQt6.QtWidgets.QFileDialog.Option.DontUseNativeDialog,
                )
        dialog.setAcceptMode(dialog.AcceptMode.AcceptSave)
        self.set_dialog_button_name(dialog, "&Open", "Save")
        if dialog.exec(): # if you saved a file
            print(*dialog.selectedFiles())
            self.rom.saveToFile(*dialog.selectedFiles())
            print("ROM modifs saved!")

    def testCall(self):
        dialog_playtest = PyQt6.QtWidgets.QDialog(self)
        dialog_playtest.setWindowTitle("Playtest Options")
        dialog_playtest.resize(500, 500)
        dialog_playtest.setLayout(PyQt6.QtWidgets.QGridLayout())
        # Test options; arm 9 at 0x00004000; starting pos x=00A00D00 y=FF6F0400
        input_address = PyQt6.QtWidgets.QLineEdit(dialog_playtest)
        input_address.setPlaceholderText("insert test patch adress")
        input_value = PyQt6.QtWidgets.QLineEdit(dialog_playtest)
        input_value.setPlaceholderText("insert test patch data")

        button_play = PyQt6.QtWidgets.QPushButton("Play", dialog_playtest)
        button_play.move(dialog_playtest.width() - 100, dialog_playtest.height() - 50)
        button_play.pressed.connect(lambda: dialog_playtest.close())
        button_play.pressed.connect(lambda: dialog_playtest.setResult(1))
        dialog_playtest.layout().addWidget(input_address)
        dialog_playtest.layout().addWidget(input_value)
        dialog_playtest.layout().addWidget(button_play)
        dialog_playtest.exec()
        if dialog_playtest.result():
            if not os.path.exists("temp"):
                os.mkdir("temp")
            self.rom.saveToFile(self.temp_path)# Create temporary ROM to playtest
            with open(self.temp_path, "r+b") as f:
                    if input_address.text() != "":
                        try:
                            address = library.dataconverter.IntFromStr(input_address.text(), self.displayBase)
                            value = library.dataconverter.StrToAlphanumStr(input_value.text(), 16, True)
                            f.seek(address)# get to pos for message
                            value_og = library.dataconverter.StrToAlphanumStr(f.read(len(bytes.fromhex(value))).hex(), self.displayBase, self.displayAlphanumeric)
                            print(f"successfully wrote {value_og} => {input_value.text().upper()} to {input_address.text().zfill(8)}")
                            f.seek(address)# get to pos
                            f.write(bytes.fromhex(value))# write data
                        except ValueError as e:
                            PyQt6.QtWidgets.QMessageBox.critical(
                                self,
                                str(e),
                                f"Address input must be numeric and must not go over size {library.dataconverter.StrFromNumber(len(self.rom.save()), self.displayBase, self.displayAlphanumeric)}\nValue input must be numeric."
                                )
                            return
            os.startfile(self.temp_path)
            print("game will start in a few seconds")

    def sdatOpenCall(self):
        if hasattr(self, 'dialog_sdat'):
            self.dialog_sdat.show()


    #def codeeditCall(self):
        #self.tree.clearSelection()
        #self.arm9 = ndspy.code.MainCodeFile(w.rom.files[0], 0x00000000)
        #self.file_content_text.setPlainText(str(self.arm9))
        #print("code")

    def treeUpdate(self):
        tree_files: list[PyQt6.QtWidgets.QTreeWidgetItem] = []
        try: # convert NDS Py filenames to QTreeWidgetItems
            tree_folder: list[PyQt6.QtWidgets.QTreeWidgetItem] = []
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
        except Exception: # if failed, empty list
            tree_files = []
        self.tree.clear()
        self.tree.addTopLevelItems(tree_files)
    
    def treeSdatUpdate(self):
        #print(str(self.sdat.groups)[:13000])
        #progress = PyQt6.QtWidgets.QProgressBar()
        #progress.setValue(0)
        #progress.show()
        self.tree_sdat.clear() 
        # all sdat sections follow the [(Name, object(data)), ...] format except swar with [(Name, object([object(data), ...])), ...] and groups, which have [(Name, [object(data), ...]), ...]
        item_sseq = PyQt6.QtWidgets.QTreeWidgetItem(["N/A", "Sequenced Music", "SSEQ"]) #SSEQ
        item_ssar = PyQt6.QtWidgets.QTreeWidgetItem(["N/A", "Sequenced Sound Effects", "SSAR"]) #SSAR
        item_sbnk = PyQt6.QtWidgets.QTreeWidgetItem(["N/A", "Sound Banks", "SBNK"]) #SBNK
        item_swar = PyQt6.QtWidgets.QTreeWidgetItem(["N/A", "Sound Waves", "SWAR"]) #SWAR
        item_sseqplayer = PyQt6.QtWidgets.QTreeWidgetItem(["N/A", "Sequence Player", "SSEQ"]) #SSEQ
        item_strm = PyQt6.QtWidgets.QTreeWidgetItem(["N/A", "Multi-Channel Stream", "STRM"]) #STRM
        item_strmplayer = PyQt6.QtWidgets.QTreeWidgetItem(["N/A", "Stream Player", "STRM"]) #STRM
        item_group = PyQt6.QtWidgets.QTreeWidgetItem(["N/A", "Group", ""])
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
                category.addChild(PyQt6.QtWidgets.QTreeWidgetItem(["Unknown", section[0], category.text(2)]))
            #progress.setValue(progress.value()+ 100//len(item_list))

        self.tree_sdat.addTopLevelItems([*item_list])
        #progress.setValue(100)
        #progress.close()

    def treeCall(self, isValueUpdate=False):
        #self.clearTasks()
        if isValueUpdate: # prevent treeCall from being executed twice in a row. Reduces lag when clicking to view a file's content
            if self.tree_called == True:
                self.tree_called = False
                return
            #print("call update")
        else:
            self.tree_called = True
            #print("call")
        self.file_content_text.setReadOnly(False)
        self.field_address.setDisabled(False)
        PyQt6.QtCore.qInstallMessageHandler(lambda a, b, c: None) # Silence Invalid base warnings from the following code
        for widget in self.findChildren(BetterSpinBox): # update all widgets of same type with current settings
            widget.alphanum = self.displayAlphanumeric
            widget.setDisplayIntegerBase(self.displayBase)
            widget.setValue(widget.value())# refresh widget text by "changing the value"
        PyQt6.QtCore.qInstallMessageHandler(None) # Revert to default message handler
        if self.dialog_settings.isVisible() and (self.field_address.displayIntegerBase() != self.displayBase): # handle error manually
            PyQt6.QtWidgets.QMessageBox.critical(
                                self,
                                "Numeric Base Warning!",
                                f"Base is not supported for inputting data in spinboxes.\n This means that all spinboxes will revert to base 10 until they are set to a supported base.\n Proceed at your own risk!"
                                )
        self.field_tile_width.setStatusTip(f"Set depth to 1bpp and tile width to {library.dataconverter.StrFromNumber(16, self.displayBase, self.displayAlphanumeric)} for JP font")
        if self.tree.currentItem() != None:
            self.fileToEdit_name = str(self.tree.currentItem().text(1) + "." + self.tree.currentItem().text(2))
            self.base_address = self.rom.save().index(self.rom.files[int(self.tree.currentItem().text(0))])
            # set text to current ROM address
            self.field_address.setMinimum(self.base_address)
            self.field_address.setValue(self.base_address+self.relative_adress)
            self.field_address.setMaximum(self.base_address+len(self.rom.files[int(self.tree.currentItem().text(0))]))
            if self.fileToEdit_name.find(".Folder") == -1:# if it's a file
                self.label_file_size.setText(f"Size: {library.dataconverter.StrFromNumber(len(self.rom.files[int(self.tree.currentItem().text(0))]), self.displayBase, self.displayAlphanumeric).zfill(0)} bytes")
                if self.fileDisplayRaw == False:
                    if self.fileDisplayMode == "Adapt":
                            indicator_list_gfx = ["face", "font", "obj_fnt", "title"]
                            if self.rom.name.decode() == "MEGAMANZX" or self.rom.name.decode() == "ROCKMANZX":
                                indicator_list_gfx.extend(["bbom", "dm23", "elf", "g01", "g03", "g_", "game_parm", "lmlevel", "miss", "repair", "sec_disk", "sub"])
                            elif self.rom.name.decode() == "MEGAMANZXA" or self.rom.name.decode() == "ROCKMANZXA":
                                indicator_list_gfx.extend(["cmm_frame_fnt", "cmm_mega_s", "cmm_rock_s", "Is_m", "Is_trans", "Is_txt_fnt", "sub_db", "sub_oth"])
                            if (self.tree.currentItem().text(1).find("talk") != -1 or self.tree.currentItem().text(1).find("m_") != -1):
                                if self.tree.currentItem().text(1).find("en") != -1:
                                    self.fileDisplayState = "English dialogue"
                                elif self.tree.currentItem().text(1).find("jp") != -1:
                                    self.fileDisplayState = "Japanese dialogue"
                            elif self.tree.currentItem().text(2) == "bin" and any(indicator in self.tree.currentItem().text(1) for indicator in indicator_list_gfx):
                                self.fileDisplayState = "Graphics"
                            elif self.tree.currentItem().text(2) == "sdat":
                                self.fileDisplayState = "Sound"
                            elif self.tree.currentItem().text(2) == "vx":
                                self.fileDisplayState = "VX"
                            else:
                                self.fileDisplayState = "None"
                    elif self.fileDisplayMode != "None":
                        self.fileDisplayState = self.fileDisplayMode
                    else:
                        self.fileDisplayState = "None"

                    if self.fileDisplayState == "English dialogue": # if english text
                        self.file_editor_show("Text")
                        self.file_content_text.setPlainText(library.dataconverter.convertdata_bin_to_text(self.rom.files[int(self.tree.currentItem().text(0))][self.relative_adress:self.relative_adress+0x6000]))
                    elif self.fileDisplayState == "Graphics":
                        #print(self.dropdown_gfx_depth.currentText()[:1] + " bpp graphics")
                        if self.gfx_palette.index(self.file_content_gfx.pen.color().rgba()) >= 2**list(library.dataconverter.CompressionAlgorithmEnum)[self.dropdown_gfx_depth.currentIndex()].depth:
                            self.file_content_gfx.pen.setColor(self.gfx_palette[0])
                        self.file_content_gfx.resetScene()
                        if not isValueUpdate: # if entering graphics mode and func is not called to update other stuff
                            self.file_editor_show("Graphics")
                        addItem_tilesQImage_fromBytes(self.file_content_gfx, self.rom.files[int(self.tree.currentItem().text(0))][self.relative_adress:], algorithm=list(library.dataconverter.CompressionAlgorithmEnum)[self.dropdown_gfx_depth.currentIndex()], tilesPerRow=self.tiles_per_row, tilesPerColumn=self.tiles_per_column, tileWidth=self.tile_width, tileHeight=self.tile_height)
                    elif self.fileDisplayState == "Sound":
                        self.file_editor_show("Text") # placeholder
                        self.checkbox_textoverwite.hide()
                        self.file_content_text.setReadOnly(True)
                        self.file_content_text.setPlainText("Sound editor is not yet implemented.\n Right click on this file > open Sound Archive\nor click on the sound icon in the toolbar to open sound archive viewer.")
                        #self.file_editor_show("Sound")
                        self.field_address.setDisabled(True)
                    elif self.fileDisplayState == "VX":
                        self.file_editor_show("VX")
                        self.field_address.setDisabled(True)
                        vx_file = library.actimagine.VX(self.rom.files[int(self.tree.currentItem().text(0))])
                        #print(self.rom.files[int(self.tree.currentItem().text(0))][5:6].hex()+self.rom.files[int(self.tree.currentItem().text(0))][4:5].hex())
                        self.field_vxHeader_length.setValue(vx_file.frame_count)
                        self.field_vxHeader_width.setValue(vx_file.frame_width)
                        self.field_vxHeader_height.setValue(vx_file.frame_height)
                        self.field_vxHeader_framerate.setText(str(vx_file.frame_rate))
                        self.field_vxHeader_quantiser.setValue(vx_file.quantiser)
                        self.field_vxHeader_sampleRate.setValue(vx_file.audio_sampleRate)
                        self.field_vxHeader_streamCount.setValue(vx_file.audio_streamCount)
                        self.field_vxHeader_frameSizeMax.setValue(vx_file.frame_sizeMax)
                        self.field_vxHeader_audioExtraDataOffset.setValue(vx_file.audio_extraDataOffset)
                        self.field_vxHeader_seekTableOffset.setValue(vx_file.seekTable_offset)
                        self.field_vxHeader_seekTableEntryCount.setValue(vx_file.seekTable_entryCount)
                        self.button_file_save.setDisabled(True)
                    else:
                        self.field_address.setDisabled(True)
                        self.file_editor_show("Text")
                        self.checkbox_textoverwite.hide()
                        self.file_content_text.setReadOnly(True)
                        if self.fileDisplayState == "None":
                            file_knowledge = "unknown"
                        else:
                            file_knowledge = "not supported at the moment"
                        self.file_content_text.setPlainText(f"This file's format is {file_knowledge}.\n Go to [View > Converted formats] to disable file interpretation and view hex data.")
                else:# if in hex display mode
                    self.file_editor_show("Text")
                    self.file_content_text.setPlainText(self.rom.files[int(self.tree.currentItem().text(0))][self.relative_adress:self.relative_adress+self.file_content_text.charcount_page()].hex())
                self.file_content_text.setDisabled(False)
            else:# if it's a folder
                self.label_file_size.setText(f"Size: N/A")
                self.file_editor_show("Text")
                self.checkbox_textoverwite.hide()
                self.field_address.setDisabled(True)
                self.file_content_text.setPlainText("")
                self.file_content_text.setDisabled(True)
            self.exportAction.setDisabled(False)
            self.button_file_save.setDisabled(True)
        else:# Nothing is selected, reset edit space
            self.field_address.setDisabled(True)
            self.label_file_size.setText(f"Size: N/A")
            self.file_content_text.setPlainText("")
            self.button_file_save.setDisabled(True)

    def reloadCall(self, isQuick=False): # Reload all reloadable content
        if hasattr(self.rom, "name"):
            if isQuick: #reload only necessary
                if self.tabs.currentIndex() == self.tabs.indexOf(self.page_explorer):
                    self.treeCall(True)
                elif self.tabs.currentIndex() == self.tabs.indexOf(self.page_patches):
                    #print("b" + str(self.displayAlphanumeric))
                    self.patches_reload()
                    #print("a" + str(self.displayAlphanumeric))
            else: #reload everything
                self.treeCall()
                self.patches_reload()

    def file_editor_show(self, mode: str):
        modes = ["Text", "Graphics", "Sound", "VX"]
        mode_index = modes.index(mode)
        # Contents of widget sets
        text_widgets: list[PyQt6.QtWidgets.QWidget] = [self.file_content_text, self.checkbox_textoverwite]
        graphics_widgets: list[PyQt6.QtWidgets.QWidget] = [
            self.file_content_gfx,
            self.dropdown_gfx_depth,
            self.field_tile_width,
            self.label_tile_width,
            self.field_tile_height,
            self.label_tile_height,
            self.field_tiles_per_row,
            self.label_tiles_per_row,
            self.field_tiles_per_column,
            self.label_tiles_per_column
            ]
        sound_widgets: list[PyQt6.QtWidgets.QWidget] = [
            ]
        vx_widgets: list[PyQt6.QtWidgets.QWidget] = [
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
            self.field_vxHeader_quantiser,
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
        for i in range(256):
            graphics_widgets.append(getattr(self, f"button_palettepick_{i}"))
        # Associates each mode with a set of widgets to show or hide 
        widget_sets = [text_widgets, graphics_widgets, sound_widgets, vx_widgets]
        # Hide all widgets from other modes
        for s in widget_sets:
            if s != widget_sets[mode_index]:
                for w in s:
                    w.hide()
        # Show widgets specific to this mode
        for w in widget_sets[mode_index]:
            w.show()
        # case-specific code
        if mode == "Graphics":
            # Reset Values
            self.relative_adress = 0x00000000
            #print(f"{len(self.rom.save()):08X}")

    def save_filecontent(self): #Save to virtual ROM
        if self.fileDisplayState == "VX":
            w.rom.files[int(self.tree.currentItem().text(0))][0x04:0x08] = bytearray(int.to_bytes(self.field_vxHeader_length.valueFromText(self.field_vxHeader_length.text()), 4, "little"))
            w.rom.files[int(self.tree.currentItem().text(0))][0x08:0x0C] = bytearray(int.to_bytes(self.field_vxHeader_width.valueFromText(self.field_vxHeader_width.text()), 4, "little"))
            w.rom.files[int(self.tree.currentItem().text(0))][0x0C:0x10] = bytearray(int.to_bytes(self.field_vxHeader_height.valueFromText(self.field_vxHeader_height.text()), 4, "little"))
            w.rom.files[int(self.tree.currentItem().text(0))][0x10:0x14] = bytearray(int.to_bytes(int(float(self.field_vxHeader_framerate.text())*0x10000), 4, "little")) #convert float to 16.16
            w.rom.files[int(self.tree.currentItem().text(0))][0x14:0x18] = bytearray(int.to_bytes(self.field_vxHeader_quantiser.valueFromText(self.field_vxHeader_quantiser.text()), 4, "little"))
            w.rom.files[int(self.tree.currentItem().text(0))][0x18:0x1C] = bytearray(int.to_bytes(self.field_vxHeader_sampleRate.valueFromText(self.field_vxHeader_sampleRate.text()), 4, "little"))
            w.rom.files[int(self.tree.currentItem().text(0))][0x1C:0x20] = bytearray(int.to_bytes(self.field_vxHeader_streamCount.valueFromText(self.field_vxHeader_streamCount.text()), 4, "little"))
            w.rom.files[int(self.tree.currentItem().text(0))][0x20:0x24] = bytearray(int.to_bytes(self.field_vxHeader_frameSizeMax.valueFromText(self.field_vxHeader_frameSizeMax.text()), 4, "little"))
            w.rom.files[int(self.tree.currentItem().text(0))][0x24:0x28] = bytearray(int.to_bytes(self.field_vxHeader_audioExtraDataOffset.valueFromText(self.field_vxHeader_audioExtraDataOffset.text()), 4, "little"))
            w.rom.files[int(self.tree.currentItem().text(0))][0x28:0x2C] = bytearray(int.to_bytes(self.field_vxHeader_seekTableOffset.valueFromText(self.field_vxHeader_seekTableOffset.text()), 4, "little"))
            w.rom.files[int(self.tree.currentItem().text(0))][0x2C:0x30] = bytearray(int.to_bytes(self.field_vxHeader_seekTableEntryCount.valueFromText(self.field_vxHeader_seekTableEntryCount.text()), 4, "little"))
        elif self.fileDisplayState == "Sound":
            return
        else:
            if self.fileDisplayRaw == False:
                if self.fileDisplayState == "English dialogue": # if english text
                    rom_save_data = library.dataconverter.convertdata_text_to_bin(self.file_content_text.toPlainText())
                if self.fileDisplayState == "Graphics":
                    rom_save_data = saveData_fromGFXView(self.file_content_gfx)
            else:
                rom_save_data = bytearray.fromhex(library.dataconverter.StrToAlphanumStr(self.file_content_text.toPlainText(), 16, True)) # force to alphanumeric for bytearray conversion
            w.rom.files[int(self.tree.currentItem().text(0))][self.relative_adress:self.relative_adress+len(rom_save_data)] = rom_save_data
        #print(type(w.rom.files[int(self.tree.currentItem().text(0))]))
        print("file changes saved")
        self.button_file_save.setDisabled(True)

    def patch_game(self):# Currently a workaround to having no easy way of writing directly to any address in the ndspy rom object
        if self.ispatching == True:
            return
        self.ispatching = True
        if not os.path.exists("temp"):
            os.mkdir("temp")
        self.rom.saveToFile(self.temp_path)# Create temporary ROM to write patch to
        patch_list = []
        for patch in library.patchdata.GameEnum[self.rom.name.decode().replace(" ", "_")].value[1]: # create a patch list with a consistent format
            if type(patch[2]) == type([]):
                patch_list.append(['N/A', patch[0], patch[1], 'N/A', 'N/A'])
                for subPatch in patch:
                    if type(subPatch) == type([]):
                        patch_list.append([subPatch[0], subPatch[1], "Patch Segment", subPatch[2], subPatch[3]])
            else:
                patch_list.append(patch)

        tree_list = self.tree_patches.findItems("", PyQt6.QtCore.Qt.MatchFlag.MatchContains | PyQt6.QtCore.Qt.MatchFlag.MatchRecursive)

        for item_i in range(len(tree_list)):# Iterate through patch groups
            if tree_list[item_i].childCount() != 0:
                if tree_list[item_i].checkState(0) != self.tree_patches_checkboxes[item_i]: # if checkstate changed
                    for child_i in range(tree_list[item_i].childCount()): # update children
                        tree_list[item_i].child(child_i).setCheckState(0, tree_list[item_i].checkState(0))
                else: # update according to children
                    subPatchMatches = 0
                    for child_i in range(tree_list[item_i].childCount()):
                        if tree_list[item_i].child(child_i).checkState(0) == PyQt6.QtCore.Qt.CheckState.Checked:
                            subPatchMatches += 1
                    if subPatchMatches == tree_list[item_i].childCount(): # Check for already applied patches
                            tree_list[item_i].setCheckState(0, PyQt6.QtCore.Qt.CheckState.Checked)
                    elif subPatchMatches > 0:
                        tree_list[item_i].setCheckState(0, PyQt6.QtCore.Qt.CheckState.PartiallyChecked)
                    else:
                        tree_list[item_i].setCheckState(0, PyQt6.QtCore.Qt.CheckState.Unchecked)

        for item_i in range(len(tree_list)):# Go through unchecked ones first
            if (tree_list[item_i].checkState(0) == PyQt6.QtCore.Qt.CheckState.Unchecked):
                # Revert patch
                if tree_list[item_i].childCount() == 0: # if not a patch group
                    with open(self.temp_path, "r+b") as f:
                        f.seek(patch_list[item_i][0])# get to patch pos
                        #print("seek: " + f"{patch_list[item_i][0]:08X}")
                        f.write(bytes.fromhex(patch_list[item_i][3]))# write og data
                        
        for item_i in range(len(tree_list)):# Then through active patches
            if (tree_list[item_i].checkState(0) == PyQt6.QtCore.Qt.CheckState.Checked):
                # Apply patch
                if tree_list[item_i].childCount() == 0: # if not a patch group
                    with open(self.temp_path, "r+b") as f:
                        f.seek(patch_list[item_i][0])# get to patch pos
                        #print("seek: " + f"{patch_list[item_i][0]:08X}")
                        newData = patch_list[item_i][4]
                        for s in range(len(patch_list[item_i][4])):
                            if newData[s] == "-":
                                newData = newData[:s] + patch_list[item_i][3][s] + newData[s+1:] # replace '-' with og data
                        newData = bytes.fromhex(newData)
                        f.write(newData)# write patch data

        for item_i in range(len(tree_list)):# Iterate through all patches
            self.tree_patches_checkboxes[item_i] = tree_list[item_i].checkState(0) #and update checkbox state list

        self.rom = ndspy.rom.NintendoDSRom.fromFile(self.temp_path)# update the editor with patched ROM
        self.ispatching = False

app = PyQt6.QtWidgets.QApplication(sys.argv)
w = MainWindow()

# Draw contents of tile viewer
def addItem_tilesQImage_fromBytes(view: GFXView, data: bytearray, palette: list[int]=w.gfx_palette, algorithm=library.dataconverter.CompressionAlgorithmEnum.ONEBPP, tilesPerRow=4, tilesPerColumn=8, tileWidth=16, tileHeight=8):
    for tile in range(tilesPerRow*tilesPerColumn):
        # get data of current tile from bytearray, multiplying tile index by amount of pixels in a tile and by amount of bits per pixel, then dividing by amount of bits per byte
        # that data is then converted into a QImage that is used to create the QPixmap of the tile
        gfx = PyQt6.QtGui.QPixmap.fromImage(library.dataconverter.convertdata_bin_to_qt(data[int(tile*(tileWidth*tileHeight)*algorithm.depth/8):int(tile*(tileWidth*tileHeight)*algorithm.depth/8+(tileWidth*tileHeight)*algorithm.depth/8)], palette, algorithm, tileWidth, tileHeight))
        gfx_container = PyQt6.QtWidgets.QGraphicsPixmapItem()
        gfx_container.setPixmap(gfx)
        #print(tile)
        #print(str(gfx_container.pos().x()) + " " + str(gfx_container.pos().y()))
        gfx_container.setPos(tileWidth*int(tile % tilesPerRow), tileHeight*int(tile / tilesPerRow))
        #print(str(gfx_container.pos().x()) + " " + str(gfx_container.pos().y()))
        view._scene.addItem(gfx_container)
    return
# Decode contents of tile viewer
def saveData_fromGFXView(view: GFXView, palette: list[int]=w.gfx_palette, algorithm=library.dataconverter.CompressionAlgorithmEnum.ONEBPP, tilesPerRow=4, tilesPerColumn=8, tileWidth=16, tileHeight=8):
    saved_data = bytearray()
    view._scene.setSceneRect(0, 0, tileWidth*tilesPerRow, tileHeight*tilesPerColumn)
    for tile in range(tilesPerRow*tilesPerColumn):
        print(view._graphic.pos().x())
        print(view._graphic.pos().y())
        tile_rect = PyQt6.QtCore.QRect(int(view._graphic.pos().x() + tileWidth*int(tile % tilesPerRow)), int(view._graphic.pos().y() + tileHeight*int(tile / tilesPerRow)), tileWidth, tileHeight)
        tile_current = view.grab(tile_rect).toImage()
        saved_data +=  library.dataconverter.convertdata_qt_to_bin(tile_current, palette, algorithm, tileWidth, tileHeight)
    return saved_data

def extract(fileToEdit_id: int, folder="", fileToEdit_name="", path="", format="", tree=w.tree):
    if tree == w.tree:
        fileToEdit_id = int(fileToEdit_id)
        fileToEdit = w.rom.files[fileToEdit_id]
        if fileToEdit_name == "":
            fileToEdit_name = w.rom.filenames[fileToEdit_id]
    elif tree == w.tree_sdat: # implement fetching file from sdat
        print("files within archive are not supported")
        return
    else:
        return
    print("file " + str(fileToEdit_id) + ": " + fileToEdit_name)
    print(fileToEdit[0x65:0xc5])

    # create a copy of the file outside ROM
    if format == "" or format == "Raw":
        with open(os.path.join(path + "/" + folder + fileToEdit_name), 'wb') as f:
            f.write(fileToEdit)
            print(os.path.join(path + "/" + folder + fileToEdit_name))
            print("File extracted!")
    else:
        if format == "English dialogue":
                with open(os.path.join(path + "/" + folder + fileToEdit_name.split(".")[0] + ".txt"), 'wb') as f:
                    f.write(bytes(library.dataconverter.convertdata_bin_to_text(fileToEdit), "utf-8"))
                    print(os.path.join(path + "/" + folder + fileToEdit_name.split(".")[0] + ".txt"))
                    print("File extracted!")
        else:
            print("could not find method for converting to specified format.")
#run the app
app.exec()
w.firstLaunch = False
library.init_readwrite.write_preferences(w)
# After execution
if os.path.exists(w.temp_path) and w.romToEdit_name != "":
    try:
        os.remove(w.temp_path) # delete temporary ROM
    except OSError as error:
        print(error)