from PyQt6 import QtGui, QtWidgets, QtCore#, QtMultimedia #Qt6, Qt6.qsci
import sys, os, platform, re, math
import argparse
#import logging, time, random
#import numpy
import ndspy
#import ndspy.graphics2D
#import ndspy.model
import ndspy.lz10
import ndspy.rom, ndspy.code, ndspy.codeCompression
import ndspy.soundArchive
import ndspy.soundSequenceArchive
import lib
#Global variables
global EDITOR_VERSION
EDITOR_VERSION = "0.4.3" # objective, feature, WIP

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
class View(QtWidgets.QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._zoom = 0
        self._zoom_limit = 70
        self.setOptimizationFlags(QtWidgets.QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing |
                                  QtWidgets.QGraphicsView.OptimizationFlag.DontSavePainterState)
        scene = QtWidgets.QGraphicsScene()
        self.setScene(scene)
        self.setMouseTracking(True)
        self.mousePressed = False

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(0, 0, 0, 0)
        for item in self.items():
            if isinstance(item, QtWidgets.QGraphicsLineItem): continue
            item_rect =  item.boundingRect()
            if item.pos().x() < rect.left():
                rect.setLeft(item.pos().x())
            if item.pos().y() < rect.top():
                rect.setTop(item.pos().y())
            if item.pos().x() + item_rect.width() > rect.right():
                rect.setRight(item.pos().x() + item_rect.width())
            if item.pos().y() + item_rect.height() > rect.bottom():
                rect.setBottom(item.pos().y() + item_rect.height())
        self.setSceneRect(rect)
        if self.scene().isActive() and scale:
            #print("fit")
            unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            viewrect = self.viewport().rect()
            scenerect = self.sceneRect()
            factor = min(viewrect.width() / scenerect.width(),
                            viewrect.height() / scenerect.height())
            self.scale(factor, factor)
        self._zoom = 0
    
    def mousePressEvent(self, event):
        #print("QGraphicsView mousePress")
        self.mousePressed = True
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        #print("QGraphicsView mouseRelease")
        if self.mousePressed:
            self.mousePressed = False
        super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event):
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.80
                self._zoom -= 1
            if self._zoom >= self._zoom_limit:
                factor = 1
                self._zoom = self._zoom_limit
            if self._zoom > 0:
                view_pos = QtCore.QRect(event.position().toPoint(), QtCore.QSize(1, 1))
                scene_pos = self.mapToScene(view_pos)
                self.centerOn(scene_pos.boundingRect().center())
                self.scale(factor, factor)
                delta = self.mapToScene(view_pos.center()) - self.mapToScene(self.viewport().rect().center())
                self.centerOn(scene_pos.boundingRect().center() - delta)
            #print(self._zoom)
        elif event.modifiers() == QtCore.Qt.KeyboardModifier.ShiftModifier:
            self.horizontalScrollBar().setSliderPosition(self.horizontalScrollBar().sliderPosition()-event.angleDelta().y())
        else:
            self.verticalScrollBar().setSliderPosition(self.verticalScrollBar().sliderPosition()-event.angleDelta().y())
        if self._zoom <= 0:
            self.fitInView()

class GFXView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setInteractive(False)
        self._zoom = 0
        self._zoom_limit = 70
        self.setOptimizationFlag(QtWidgets.QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True)
        self.setOptimizationFlag(QtWidgets.QGraphicsView.OptimizationFlag.DontSavePainterState, True)
        scene = QtWidgets.QGraphicsScene()
        self.setScene(scene)
        self._graphic = QtWidgets.QGraphicsPixmapItem()
        self._graphic.setFlag(QtWidgets.QGraphicsPixmapItem.GraphicsItemFlag.ItemIgnoresParentOpacity, True)
        self.scene().addItem(self._graphic)
        self.pen = QtGui.QPen()
        self.pen.setColor(0x00010101) # grayscale color for indexed images
        self.start = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.end_previous = QtCore.QPoint()
        self.setMouseTracking(True)
        self.mousePressed = False
        self.draw_mode = "pixel"
        self.rectangle = None # used for drawing rectangles

    def resetScene(self):
        self.scene().clear()
        self.rectangle = None
        self._graphic = QtWidgets.QGraphicsPixmapItem()
        self.scene().addItem(self._graphic)

    #def setGraphic(self, pixmap: QtGui.QPixmap=None):
    #    self._zoom = 0
    #    if pixmap and not pixmap.isNull():
    #        self._empty = False
    #        self._graphic.setPixmap(pixmap)
    #    else:
    #        self._empty = True
    #        self._graphic.setPixmap(QtGui.QPixmap())
    #        #self._graphic.pixmap()
    #    self.fitInView()


    def drawShape(self):
        if self.draw_mode == "pixel":
            gfx_zone = self._graphic.pixmap() # create a pixmap that can be used by painter
            painter = QtGui.QPainter()
            painter.begin(gfx_zone) # image is auto-converted to Format_Grayscale8 for painting thanks to the NoFormatConversion flag which kept it in Format_Indexed8 until then
            painter.setPen(self.pen)

            pos = QtCore.QLine(int(self.end_previous.x()),int(self.end_previous.y()),int(self.end.x()),int(self.end.y()))
            painter.drawLine(pos)

            painter.end() # release resources to prevent crash
            # unfortunately, toImage does not return a QImage in indexed format, so the format must be corrected manually
            img = gfx_zone.toImage().convertToFormat(QtGui.QImage.Format.Format_Grayscale8).convertToFormat(QtGui.QImage.Format.Format_Indexed8) # convert from grayscale to indexed
            img.setColorTable(w.gfx_palette) # re-apply colors
            self._graphic.setPixmap(QtGui.QPixmap.fromImage(img, QtCore.Qt.ImageConversionFlag.NoFormatConversion))
            w.button_file_save.setDisabled(False)
        elif self.draw_mode == "rectangle":
            width = abs(self.start.x() - self.end.x())
            height = abs(self.start.y() - self.end.y())
            if self.rectangle == None:
                self.rectangle = self.scene().addRect(min(self.start.x(), self.end.x()), min(self.start.y(), self.end.y()), width, height, self.pen)
            else:
                self.rectangle.setRect(min(self.start.x(), self.end.x()), min(self.start.y(), self.end.y()), width, height)
                self.rectangle.setPen(self.pen)

    def createGrid(self, tileWidth: int=8, tileHeight: int=8):
        if self._graphic.pixmap().isNull(): return
        img = self._graphic.pixmap().toImage().scaled(1, 1, transformMode=QtCore.Qt.TransformationMode.SmoothTransformation) # get average
        img.invertPixels() # for a contrasting grid color
        #print(color.getRgb())
        pen = QtGui.QPen(img.pixelColor(0, 0))
        pen.setWidthF(0.05) # extra thin line
        pos = [self._graphic.scenePos().x(), self._graphic.scenePos().y()]
        size = [self._graphic.pixmap().size().width(), self._graphic.pixmap().size().height()]
        if tileWidth != 0:
            for i in range(1, size[0]//tileWidth):
                vline = QtCore.QLineF(pos[0]+i*tileWidth, pos[1], pos[0]+i*tileWidth, pos[1]+size[1])
                self.scene().addLine(vline, pen)
        
        if tileHeight != 0:
            for i in range(1, size[1]//tileHeight):
                hline = QtCore.QLineF(pos[0], pos[1]+i*tileHeight, pos[0]+size[0], pos[1]+i*tileHeight)
                self.scene().addLine(hline, pen)

    def mousePressEvent(self, event):
        #print("QGraphicsView mousePress")
        self.mousePressed = True
        # Reset vars to avoid abnormal drawing positions
        self.start = self.mapToScene(event.pos())
        self.end = self.start
        self.end_previous = self.end
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.draw_mode = "pixel"
        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            self.draw_mode = "rectangle"
        self.drawShape()

    def mouseMoveEvent(self, event):
        #print("QGraphicsView mouseMove")
        self.end = self.mapToScene(event.pos())
        if self.draw_mode == "rectangle":
            if self.mousePressed:
                self.drawShape()
        else:
            if self.mousePressed:
                self.drawShape()
            self.end_previous = self.end

    def mouseReleaseEvent(self, event):
        #print("QGraphicsView mouseRelease")
        if self.mousePressed:
            self.mousePressed = False

class OAMView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True) # prevent weird scaling artifacts on overlapping items
        self.setSceneRect(QtCore.QRectF(-128, -128, 256, 256)) # dimensions correspond to max positions of object
        self.item_current: OAMObjectItem | None = None

    def fitInView(self, scale=True):
        if self.scene().isActive() and scale:
            #print("fit")
            unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            viewrect = self.viewport().rect()
            scenerect = self.sceneRect()
            factor = min(viewrect.width() / scenerect.width(),
                            viewrect.height() / scenerect.height())
            self.scale(factor, factor)
        self._zoom = 0

class OAMObjectItem(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, *args, id=0, editable=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.obj_id = id
        self.editable = editable
        if editable:
            self.setFlags(QtWidgets.QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable |
                        QtWidgets.QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable |
                        QtWidgets.QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsGeometryChanges)

    def itemChange(self, change: QtWidgets.QGraphicsPixmapItem.GraphicsItemChange, value: QtCore.QVariant):
        if change == QtWidgets.QGraphicsPixmapItem.GraphicsItemChange.ItemPositionChange and self.scene():
            if QtWidgets.QApplication.mouseButtons() == QtCore.Qt.MouseButton.LeftButton:
                rect = w.file_content_oam.sceneRect()
                x = min(max(rect.left(), value.x()), rect.right())
                y = min(max(rect.top(), value.y()), rect.bottom())
                return QtCore.QPointF(int(x), int(y))
            else:
                return value
        else:
            return super().itemChange(change, value)
    
    def setSelected(self, selected):
        if selected:
            self.scene().views()[0].item_current = self
        super().setSelected(selected)
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self.editable:
            w.dropdown_oam_obj.setCurrentIndex(self.obj_id)
            w.treeCall()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.editable:
            # prevent drag from emitting valueChanged signal, because it affects item position in turn
            w.field_objX.blockSignals(True)
            w.field_objY.blockSignals(True)
            w.field_objX.setValue(self.scenePos().x())
            w.field_objY.setValue(self.scenePos().y())
            w.field_objX.blockSignals(False)
            w.field_objY.blockSignals(False)
            w.button_file_save.setEnabled(True)


class EditorTree(QtWidgets.QTreeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ContextNameType = "[Filenames]"

    def contextMenuOpen(self): #quick menu to export or replace selected file
        self.context_menu = QtWidgets.QMenu(self)
        self.context_menu.setGeometry(self.cursor().pos().x(), self.cursor().pos().y(), 50, 50)
        contextName = self.ContextNameType + self.currentItem().text(0)
        if self.ContextNameType == "[Filenames]":
            contextName = self.currentItem().text(1) + ("." + self.currentItem().text(2)).replace(".Folder", " and contents")
        exportAction = self.context_menu.addAction("Export " + contextName)
        importAction = self.context_menu.addAction("Replace " + contextName)
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
                w.dialog_sdat.setFocus()
    
    def mousePressEvent(self, event: QtCore.QEvent): #redefine mouse press to insert custom code on right click
        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            super(EditorTree, self).mousePressEvent(event)
            if event.button() == QtCore.Qt.MouseButton.RightButton and self.currentItem() != None: # execute different code if right click
                self.contextMenuOpen()

class HoldButton(QtWidgets.QPushButton): #change class to use pyqt signals instead
    pressed_quick = QtCore.pyqtSignal(bool)
    held = QtCore.pyqtSignal(bool)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = 0
        self.rate = 100
        self.allow_press = False
        self.allow_repeat = True
        self.press_quick_threshold = 1
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_timeout)
        self.pressed.connect(self.on_press)
        self.released.connect(self.on_release)
        #self.timeout_func = None # when button held

    def on_timeout(self):
        #print(str(self.counter) + " vs " + str(self.press_quick_threshold))
        self.counter += 1
        if self.counter > self.press_quick_threshold:
            #print("hold " + str(self.counter))
            self.held.emit(True)
            if not self.allow_repeat:
                self.counter = -1
                self.timer.stop()
                self.setDown(False)

    def on_press(self):
        #print("pressed")
        self.counter = 0
        self.timer.start(self.rate)

    def on_release(self):
        #print("release " + str(self.counter))
        self.timer.stop()
        #self.held.emit(False)
        if self.counter != -1 and self.counter <= self.press_quick_threshold and self.allow_press == True:
            self.pressed_quick.emit(True)
            #print("quick")
        #self.pressed_quick.emit(False)
        self.counter = -1

class PlayButton(QtWidgets.QPushButton):
    frameRequested = QtCore.pyqtSignal(bool)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rate = 16
        self.counter = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_timeout)
        self.pressed.connect(self.on_press)
        self.icon_play = QtGui.QIcon('icons\\control.png')
        self.icon_pause = QtGui.QIcon('icons\\control-pause.png')
        self.setIcon(self.icon_play)

    def on_timeout(self):
        self.counter += 1
        self.frameRequested.emit(True)

    def on_press(self):
        if self.timer.isActive():
            self.timer.stop()
            self.setIcon(self.icon_play)
        else:
            self.timer.start(self.rate)
            self.setIcon(self.icon_pause)
    
    def autoPause(self):
        self.timer.stop()
        self.counter = 0
        self.setIcon(self.icon_play)
    
class BetterSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alphanum = True
        self.numbase = 10
        self.setKeyboardTracking(False) # I don't even know why this isn't false by default
        self.setRange(-0xFFFFFFFF, 0xFFFFFFFF)
        #self.setDecimals(16) # cannot do setDecimals here because it will crash the program for... some reason. Have to do it for each instance instead.
        self.numfill = 0
        self.isInt = False
        self.acceptedSymbols = [".", "{", "}", *lib.datconv.symbols]
        #self.setCorrectionMode(self.CorrectionMode.CorrectToNearestValue)

    def fixup(self, str):
        return super().fixup(str)

    def validate(self, input, pos): # hijack validator to accept alphanumeric values
        input2 = input.upper()
        #print("input: " + input)
        for c in self.acceptedSymbols:
            input2 = input2.replace(c, "")
        if input2 == "":
            #print("valid input detected: " + input)
            return (QtGui.QValidator.State.Acceptable, input, pos)
        else:
            #print("invalid input detected: " + input)
            return (QtGui.QValidator.State.Invalid, input, pos)

    def textFromValue(self, value): # ovewrite of existing function with 2 args that determines how value is displayed inside spinbox
        if self.isInt:
            self.acceptedSymbols = ["-", "{", "}", *lib.datconv.symbols]
            return lib.datconv.numToStr(int(value), self.numbase, self.alphanum).zfill(self.numfill)
        else:
            self.acceptedSymbols = ["-", ".", "{", "}", *lib.datconv.symbols]
            return lib.datconv.numToStr(value, self.numbase, self.alphanum).zfill(self.numfill)
    
    def valueFromText(self, text):
        if self.isInt:
            return int(lib.datconv.strToNum(text, self.numbase))
        else:
            return float(lib.datconv.strToNum(text, self.numbase))
    
    def value(self):
        if self.isInt:
            return int(super().value())
        else:
            return super().value()

class LongTextEdit(QtWidgets.QPlainTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.charcount_page = lambda: int(int(self.width()/self.fontMetrics().averageCharWidth() - 1)*int(self.height()/self.fontMetrics().lineSpacing() -1)/2)

    def contextMenuOpen(self): #quick menu to insert special values in dialogue file
        self.context_menu = QtWidgets.QMenu(self)
        self.context_menu.setGeometry(self.cursor().pos().x(), self.cursor().pos().y(), 50, 50)
        for char_index in range(len(lib.dialogue.SPECIAL_CHARACTER_LIST)):
            if char_index >= 0xe0 and not isinstance(lib.dialogue.SPECIAL_CHARACTER_LIST[char_index], int):
                self.context_menu.addAction(f"{lib.datconv.numToStr(char_index, w.displayBase, w.displayAlphanumeric).zfill(2)} - {lib.dialogue.SPECIAL_CHARACTER_LIST[char_index][1]}")
        action2 = self.context_menu.exec()
        if action2 is not None:
            self.insertPlainText(action2.text()[action2.text().find("├"):])

    def mousePressEvent(self, event: QtCore.QEvent): #redefine mouse press to insert custom code on right click
        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            super(LongTextEdit, self).mousePressEvent(event)
            if event.button() == QtCore.Qt.MouseButton.RightButton: # execute different code if right click
                self.contextMenuOpen()

class LabeledSlider(QtWidgets.QWidget): # https://stackoverflow.com/a/54819051
    def __init__(self, parent, minimum, maximum, interval=1, orientation=QtCore.Qt.Orientation.Horizontal, labels=None):
        super(LabeledSlider, self).__init__(parent=parent)

        levels=range(minimum, maximum+interval, interval)
        if labels is not None:
            if not isinstance(labels, (tuple, list)):
                raise Exception("<labels> is a list or tuple.")
            if len(labels) != len(levels):
                raise Exception("Size of <labels> doesn't match levels.")
            self.levels=list(zip(levels,labels))
        else:
            self.levels=list(zip(levels,map(str,levels)))

        if orientation==QtCore.Qt.Orientation.Horizontal:
            self.setLayout(QtWidgets.QVBoxLayout(self))
        elif orientation==QtCore.Qt.Orientation.Vertical:
            self.setLayout(QtWidgets.QHBoxLayout(self))
        else:
            raise Exception("<orientation> wrong.")

        # gives some space to print labels
        self.left_margin=10
        self.top_margin=10
        self.right_margin=10
        self.bottom_margin=10

        self.layout().setContentsMargins(self.left_margin,self.top_margin,
                self.right_margin,self.bottom_margin)

        self.sl=QtWidgets.QSlider(orientation, self)
        self.sl.setMinimum(minimum)
        self.sl.setMaximum(maximum)
        self.sl.setValue(minimum)
        if orientation==QtCore.Qt.Orientation.Horizontal:
            self.sl.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        else:
            self.sl.setTickPosition(QtWidgets.QSlider.TickPosition.TicksLeft)
        self.sl.setTickInterval(interval)
        self.sl.setSingleStep(1)

        self.layout().addWidget(self.sl)

    def setLabels(self, labels: list[str]):
        for i in range(len(self.levels)):
            self.levels[i] = (self.levels[i][0], labels[i])
        self.repaint()

    def paintEvent(self, e):

        super(LabeledSlider,self).paintEvent(e)

        style=self.sl.style()
        painter=QtGui.QPainter(self)
        st_slider=QtWidgets.QStyleOptionSlider()
        st_slider.initFrom(self.sl)
        st_slider.orientation=self.sl.orientation()

        length=style.pixelMetric(QtWidgets.QStyle.PixelMetric.PM_SliderLength, st_slider, self.sl)
        available=style.pixelMetric(QtWidgets.QStyle.PixelMetric.PM_SliderSpaceAvailable, st_slider, self.sl)

        for v, v_str in self.levels:

            # get the size of the label
            rect=painter.drawText(QtCore.QRect(), QtCore.Qt.TextFlag.TextDontPrint, v_str)

            if self.sl.orientation()==QtCore.Qt.Orientation.Horizontal:
                # I assume the offset is half the length of slider, therefore
                # + length//2
                x_loc=QtWidgets.QStyle.sliderPositionFromValue(self.sl.minimum(),
                        self.sl.maximum(), v, available)+length//2

                # left bound of the text = center - half of text width + L_margin
                left=x_loc-rect.width()//2+self.left_margin
                bottom=self.rect().bottom()

                # enlarge margins if clipping
                if v==self.sl.minimum():
                    if left<=0:
                        self.left_margin=rect.width()//2-x_loc
                    if self.bottom_margin<=rect.height():
                        self.bottom_margin=rect.height()

                    self.layout().setContentsMargins(self.left_margin, self.top_margin, self.right_margin, self.bottom_margin)

                if v==self.sl.maximum() and rect.width()//2>=self.right_margin:
                    self.right_margin=rect.width()//2
                    self.layout().setContentsMargins(self.left_margin, self.top_margin, self.right_margin, self.bottom_margin)

            else:
                y_loc=QtWidgets.QStyle.sliderPositionFromValue(self.sl.minimum(), self.sl.maximum(), v, available, upsideDown=True)

                bottom=y_loc+length//2+rect.height()//2+self.top_margin-3
                # there is a 3 px offset that I can't attribute to any metric

                left=self.left_margin-rect.width()
                if left<=0:
                    self.left_margin=rect.width()+2
                    self.layout().setContentsMargins(self.left_margin, self.top_margin, self.right_margin, self.bottom_margin)

            pos=QtCore.QPoint(left, bottom)
            painter.drawText(pos, v_str)

        return

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

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
                                       \rThe current version is {EDITOR_VERSION}."""
                                       )
            firstLaunch_dialog.setInformativeText(f"""Editor's current features ({EDITOR_VERSION.split('.')[1]}):
                                                  \r- English dialogue text editor
                                                  \r- Patcher(no patches available yet)
                                                  \r- Graphics editor
                                                  \r- Font editor

                                                  \rWIP ({EDITOR_VERSION.split('.')[2]}):
                                                  \r- Sound data editor
                                                  \r- VX file editor
                                                  \r- OAM editor""")
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
                                \rEditor version: {EDITOR_VERSION} (final objective(s) completed, major functional features, WIP features)\
                                \rPython version: 3.13.2 (your version is {platform.python_version()})\
                                \rPyQt version: 6.8.1 (your version is {QtCore.PYQT_VERSION_STR})\
                                \rNDSPy version: 4.2.0 (your version is {list(ndspy.VERSION)[0]}.{list(ndspy.VERSION)[1]}.{list(ndspy.VERSION)[2]})""")
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
        self.button_playtest = HoldButton(QtGui.QIcon('icons\\control.png'), "", self)
        self.button_playtest.setToolTip("Playtest ROM (Hold for options)")
        self.button_playtest.setStatusTip("Create a temporary ROM to test saved changes")
        self.button_playtest.allow_repeat = False
        self.button_playtest.allow_press = True
        self.button_playtest.pressed_quick.connect(lambda: self.testCall(True))
        self.button_playtest.held.connect(lambda: self.testCall(False))
        self.button_playtest.setDisabled(True)
        self.button_reload = HoldButton(QtGui.QIcon('icons\\arrow-circle-315.png'), "", self)
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

        self.tree_arm9 = EditorTree(self.page_arm9)
        self.page_arm9.layout().addWidget(self.tree_arm9)
        self.tree_arm9.ContextNameType = "code-section at "
        self.tree_arm9.setColumnCount(3)
        self.tree_arm9.setHeaderLabels(["RAM Address", "Name", "Implicit"])
        self.tree_arm9.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        self.tree_arm9Ovltable = EditorTree(self.page_arm9Ovltable)
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

        self.tree_arm7 = EditorTree(self.page_arm7)
        self.page_arm7.layout().addWidget(self.tree_arm7)
        self.tree_arm7.ContextNameType = "code-section at "
        self.tree_arm7.setColumnCount(3)
        self.tree_arm7.setHeaderLabels(["RAM Address", "Name", "Implicit"])
        self.tree_arm7.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        self.tree_arm7Ovltable = EditorTree(self.page_arm7Ovltable)
        self.page_arm7Ovltable.layout().addWidget(self.tree_arm7Ovltable)
        self.tree_arm7Ovltable.ContextNameType = "overlay "
        self.tree_arm7Ovltable.setColumnCount(10)
        self.tree_arm7Ovltable.setHeaderLabels(["File ID", "RAM Address", "Compressed", "Size", "RAM Size", "BSS Size", "StaticInit Start", "StaticInit End", "Flags", "Verify Hash"])
        self.tree_arm7Ovltable.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        # File explorer
        self.tree = EditorTree(self.page_explorer)
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
        self.layout_colorpick = QtWidgets.QGridLayout()
        self.layout_colorpick.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        self.button_file_save = QtWidgets.QPushButton("Save file", self.page_explorer)
        self.button_file_save.setMaximumWidth(100)
        self.button_file_save.setToolTip("save this file's changes")
        self.button_file_save.pressed.connect(self.save_filecontent)
        self.button_file_save.setDisabled(True)
        self.button_file_save.hide()

        self.file_content = QtWidgets.QGridLayout()
        self.file_content_text = LongTextEdit(self.page_explorer)
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
        self.dropdown_textindex.hide()

        self.checkbox_textoverwite = QtWidgets.QCheckBox("Overwite\n existing text", self.page_explorer)
        self.checkbox_textoverwite.setStatusTip("With this enabled, writing text won't change filesize")
        self.checkbox_textoverwite.clicked.connect(lambda: self.file_content_text.setOverwriteMode(not self.file_content_text.overwriteMode()))
        self.checkbox_textoverwite.hide()

        self.layout_editzone_row1.addWidget(self.checkbox_textoverwite)
        self.layout_editzone_row1.addWidget(self.dropdown_textindex)

        self.file_content_gfx = GFXView(self.page_explorer)
        self.file_content_gfx.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Expanding)
        self.file_content_gfx.hide()
        self.file_content.addWidget(self.file_content_gfx)
        self.file_content.addWidget(self.file_content_text)

        self.dropdown_gfx_depth = QtWidgets.QComboBox(self.page_explorer)
        self.dropdown_gfx_depth.addItems(["1bpp", "4bpp", "8bpp"])# order of names is determined by the enum in dataconverter
        self.dropdown_gfx_depth.currentIndexChanged.connect(lambda: self.treeCall())# Update gfx with current depth
        self.dropdown_gfx_depth.hide()

        self.font_caps = QtGui.QFont()
        self.font_caps.setCapitalization(QtGui.QFont.Capitalization.AllUppercase)
        
        #Address bar
        self.field_address = BetterSpinBox(self.page_explorer)
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
        self.label_file_size.setText("Size: N/A")
        self.label_file_size.hide()
        #Tile Wifth
        self.tile_width = 8
        self.field_tile_width = BetterSpinBox(self.page_explorer)
        self.field_tile_width.setStatusTip(f"Set tile width to {lib.datconv.numToStr(16, self.displayBase, self.displayAlphanumeric)} or {lib.datconv.numToStr(32, self.displayBase, self.displayAlphanumeric)} for some ZXA sprites")
        self.field_tile_width.setFont(self.font_caps)
        self.field_tile_width.setValue(self.tile_width)
        self.field_tile_width.setMinimum(1)
        self.field_tile_width.numbase = self.displayBase
        self.field_tile_width.isInt = True
        self.field_tile_width.valueChanged.connect(lambda: self.value_update_Call("tile_width", int(self.field_tile_width.value()), True))
        self.field_tile_width.valueChanged.connect(self.file_content_gfx.fitInView)
        self.field_tile_width.hide()

        self.label_tile_width = QtWidgets.QLabel(self.page_explorer)
        self.label_tile_width.setText(" width")
        self.label_tile_width.hide()

        self.layout_tile_width = QtWidgets.QVBoxLayout()
        self.layout_tile_width.addWidget(self.field_tile_width)
        self.layout_tile_width.addWidget(self.label_tile_width)
        self.layout_tile_width.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        #Tile Height
        self.tile_height = 8
        self.field_tile_height = BetterSpinBox(self.page_explorer)
        self.field_tile_height.setFont(self.font_caps)
        self.field_tile_height.setValue(self.tile_height)
        self.field_tile_height.setMinimum(1)
        self.field_tile_height.numbase = self.displayBase
        self.field_tile_height.isInt = True
        self.field_tile_height.valueChanged.connect(lambda: self.value_update_Call("tile_height", int(self.field_tile_height.value()), True)) 
        self.field_tile_height.valueChanged.connect(self.file_content_gfx.fitInView)
        self.field_tile_height.hide()

        self.label_tile_height = QtWidgets.QLabel(self.page_explorer)
        self.label_tile_height.setText(" height")
        self.label_tile_height.hide()

        self.layout_tile_height = QtWidgets.QVBoxLayout()
        self.layout_tile_height.addWidget(self.field_tile_height)
        self.layout_tile_height.addWidget(self.label_tile_height)
        self.layout_tile_height.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        #Tiles Per row
        self.tiles_per_row = 8
        self.field_tiles_per_row = BetterSpinBox(self.page_explorer)
        self.field_tiles_per_row.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.field_tiles_per_row.setFont(self.font_caps)
        self.field_tiles_per_row.setValue(self.tiles_per_row)
        self.field_tiles_per_row.setMinimum(1)
        self.field_tiles_per_row.isInt = True
        self.field_tiles_per_row.numbase = self.displayBase
        self.field_tiles_per_row.valueChanged.connect(lambda: self.value_update_Call("tiles_per_row", int(self.field_tiles_per_row.value()), True))
        self.field_tiles_per_row.valueChanged.connect(self.file_content_gfx.fitInView)
        self.field_tiles_per_row.hide()

        self.label_tiles_per_row = QtWidgets.QLabel(self.page_explorer)
        self.label_tiles_per_row.setText(" columns")
        self.label_tiles_per_row.hide()

        self.layout_tiles_per_row = QtWidgets.QVBoxLayout()
        self.layout_tiles_per_row.addWidget(self.field_tiles_per_row)
        self.layout_tiles_per_row.addWidget(self.label_tiles_per_row)
        self.layout_tiles_per_row.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        #Tiles Per Column
        self.tiles_per_column = 8
        self.field_tiles_per_column = BetterSpinBox(self.page_explorer)
        self.field_tiles_per_column.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.field_tiles_per_column.setFont(self.font_caps)
        self.field_tiles_per_column.setValue(self.tiles_per_column)
        self.field_tiles_per_column.setMinimum(1)
        self.field_tiles_per_column.isInt = True
        self.field_tiles_per_column.numbase = self.displayBase
        self.field_tiles_per_column.valueChanged.connect(lambda: self.value_update_Call("tiles_per_column", int(self.field_tiles_per_column.value()), True))
        self.field_tiles_per_column.valueChanged.connect(self.file_content_gfx.fitInView)
        self.field_tiles_per_column.hide()

        self.label_tiles_per_column = QtWidgets.QLabel(self.page_explorer)
        self.label_tiles_per_column.setText(" rows")
        self.label_tiles_per_column.hide()

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
        self.dropdown_gfx_index.hide()
        self.dropdown_gfx_subindex = QtWidgets.QComboBox(self.page_explorer)
        self.dropdown_gfx_subindex.setPlaceholderText("no sub-entries")
        self.dropdown_gfx_subindex.setToolTip("Choose sub-index")
        self.dropdown_gfx_subindex.setStatusTip("Select the image index to go to in gfx object")
        self.dropdown_gfx_subindex.currentIndexChanged.connect(lambda: self.treeCall())
        self.dropdown_gfx_subindex.hide()

        self.checkbox_depthUpdate = QtWidgets.QCheckBox(self.page_explorer)
        self.checkbox_depthUpdate.setStatusTip("Update depth to match palette size")
        self.checkbox_depthUpdate.setChecked(True)
        self.checkbox_depthUpdate.checkStateChanged.connect(lambda: self.treeCall())
        self.checkbox_depthUpdate.hide()

        self.label_depthUpdate = QtWidgets.QLabel(self.page_explorer)
        self.label_depthUpdate.setText("Guess correct depth")
        self.label_depthUpdate.hide()

        self.layout_other_settings = QtWidgets.QGridLayout()
        self.layout_other_settings.addWidget(self.checkbox_depthUpdate, 0,0, QtCore.Qt.AlignmentFlag.AlignRight)
        self.layout_other_settings.addWidget(self.label_depthUpdate, 0,1)
        self.layout_other_settings.addWidget(self.dropdown_gfx_index, 1,0)
        self.layout_other_settings.addWidget(self.dropdown_gfx_subindex, 1,1)

        #Palettes
        for i in range(256): #setup default palette
            setattr(self, f"button_palettepick_{i}", HoldButton(self.page_explorer))
            button_palettepick: HoldButton = getattr(self, f"button_palettepick_{i}")
            button_palettepick.allow_press = True
            button_palettepick.press_quick_threshold = 1
            button_palettepick.setStyleSheet(f"background-color: #{self.gfx_palette[i]:08x}; color: white;")
            button_palettepick.setMaximumSize(10, 10)
            self.layout_colorpick.addWidget(button_palettepick, int(i/16), int(i%16))
            button_palettepick.held.connect(lambda hold, press=None, color_index=i: self.colorpickCall(color_index, press, hold))
            button_palettepick.pressed_quick.connect(lambda press, hold=None, color_index=i: self.colorpickCall(color_index, press, hold))
            button_palettepick.hide()

        self.dropdown_gfx_palette = QtWidgets.QComboBox(self.page_explorer)
        self.dropdown_gfx_palette.addItems(["Default Palette", "Font Palette", "Sprites Palette", "BG Palette"]) # order of names is determined by the enum in dataconverter
        self.dropdown_gfx_palette.setToolTip("Choose palette")
        self.dropdown_gfx_palette.setStatusTip("Select the color palette preset that you want to use to render images")
        self.dropdown_gfx_palette.currentIndexChanged.connect(lambda: self.setPalette(self.GFX_PALETTES[self.dropdown_gfx_palette.currentIndex()])) # Update gfx with current depth
        self.dropdown_gfx_palette.currentIndexChanged.connect(lambda: self.treeCall())
        self.dropdown_gfx_palette.hide()

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
        self.dropdown_oam_entry.hide()

        self.tabs_oam = QtWidgets.QTabWidget(self.page_explorer)
        self.tabs_oam.hide()
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

        self.field_oam_animFrameId = BetterSpinBox(self.page_oam_anims)
        self.field_oam_animFrameId.setToolTip("Frame Id")
        self.field_oam_animFrameId.setStatusTip("Frame index as seen in the frame editing tab")
        self.field_oam_animFrameId.isInt = True
        self.field_oam_animFrameId.setRange(0, 0xFF)
        self.field_oam_animFrameId.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.field_oam_animFrameId.valueChanged.connect(lambda: self.treeCall(addr_disabled=True))

        self.field_oam_animFrameDuration = BetterSpinBox(self.page_oam_anims)
        self.field_oam_animFrameDuration.setToolTip("Duration (Frames)")
        self.field_oam_animFrameDuration.setStatusTip("Duration of current frame; After the first frame, 0xFE and 0xFF are treated as loop and end")
        self.field_oam_animFrameDuration.isInt = True
        self.field_oam_animFrameDuration.setRange(0, 0xFF)
        self.field_oam_animFrameDuration.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.field_oam_animFrameDuration.valueChanged.connect(lambda: self.treeCall(addr_disabled=True))

        self.checkbox_oam_animLoop = QtWidgets.QCheckBox(self.page_oam_anims)
        self.checkbox_oam_animLoop.setText("Loop")
        self.checkbox_oam_animLoop.setToolTip("Loop")
        self.checkbox_oam_animLoop.setStatusTip("Enable/Disable animation loop point")
        self.checkbox_oam_animLoop.checkStateChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.checkbox_oam_animLoop.checkStateChanged.connect(lambda: self.field_oam_animLoopStart.setEnabled(self.checkbox_oam_animLoop.isChecked()))

        self.field_oam_animLoopStart = BetterSpinBox(self.page_oam_anims)
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

        self.button_oam_animPlay = PlayButton(self.page_oam_anims)
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

        self.field_objTileId = BetterSpinBox(self.page_oam_frames)
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

        self.slider_objSizeIndex = LabeledSlider(self.page_oam_frames, 0, 3, interval=1, orientation=QtCore.Qt.Orientation.Horizontal, labels=["1x1", "2x2", "4x4", "8x8"])
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

        self.field_objX = BetterSpinBox(self.page_oam_frames)
        self.field_objX.setToolTip("X")
        self.field_objX.isInt = True
        self.field_objX.setRange(-128, 127)
        self.field_objX.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.field_objX.valueChanged.connect(lambda: self.file_content_oam.item_current.setX(self.field_objX.value()))
        self.field_objY = BetterSpinBox(self.page_oam_frames)
        self.field_objY.setToolTip("Y")
        self.field_objY.isInt = True
        self.field_objY.setRange(-128, 127)
        self.field_objY.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.field_objY.valueChanged.connect(lambda: self.file_content_oam.item_current.setY(self.field_objY.value()))

        self.file_content_oam = OAMView(self.page_explorer)
        self.file_content_oam.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Expanding)
        self.file_content_oam.hide()
        self.file_content.addWidget(self.file_content_oam)

        self.layout_oam_navigation = QtWidgets.QGridLayout()
        self.layout_oam_navigation.addWidget(self.dropdown_oam_entry, 0, 0)
        self.page_oam_anims.layout().addWidget(self.dropdown_oam_anim, 0, 0, 1, 2)
        self.page_oam_anims.layout().addWidget(self.dropdown_oam_animFrame, 0, 2)
        self.page_oam_anims.layout().addWidget(self.field_oam_animFrameId, 1, 2)
        self.page_oam_anims.layout().addWidget(self.field_oam_animFrameDuration, 2, 2)
        self.page_oam_anims.layout().addWidget(self.checkbox_oam_animLoop, 1, 0)
        self.page_oam_anims.layout().addWidget(self.field_oam_animLoopStart, 2, 0)
        self.page_oam_anims.layout().addWidget(self.button_oam_animToStart, 3, 0)
        self.page_oam_anims.layout().addWidget(self.button_oam_animPlay, 3, 1)
        self.page_oam_anims.layout().addWidget(self.button_oam_animToEnd, 3, 2)
        self.page_oam_frames.layout().addWidget(self.dropdown_oam_objFrame, 0, 0)
        self.page_oam_frames.layout().addWidget(self.dropdown_oam_obj, 0, 1)
        self.page_oam_frames.layout().addWidget(self.button_oam_objSelect, 0, 2)
        self.page_oam_frames.layout().addWidget(self.field_objTileId, 1, 0, 1, 3)
        self.page_oam_frames.layout().addWidget(self.checkbox_objFlipH, 2, 0)
        self.page_oam_frames.layout().addWidget(self.checkbox_objFlipV, 3, 0)
        self.page_oam_frames.layout().addWidget(self.slider_objSizeIndex, 4, 0)
        self.page_oam_frames.layout().addWidget(self.group_oam_objShape, 4, 1, 1, 2)
        self.page_oam_frames.layout().addWidget(self.field_objX, 5, 0)
        self.page_oam_frames.layout().addWidget(self.field_objY, 5, 1, 1, 2)

        #Font
        self.field_font_size = BetterSpinBox(self.page_explorer)
        self.field_font_size.setFont(self.font_caps)
        self.field_font_size.setMinimum(0)
        self.field_font_size.isInt = True
        self.field_font_size.numbase = self.displayBase
        self.field_font_size.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.field_font_size.hide()
        self.label_font_size = QtWidgets.QLabel(self.page_explorer)
        self.label_font_size.setText("file size")
        self.label_font_size.hide()
        self.layout_font_size = QtWidgets.QVBoxLayout()
        self.layout_font_size.addWidget(self.field_font_size)
        self.layout_font_size.addWidget(self.label_font_size)
        self.layout_font_size.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.field_font_width = BetterSpinBox(self.page_explorer)
        self.field_font_width.setFont(self.font_caps)
        self.field_font_width.setMinimum(0)
        self.field_font_width.isInt = True
        self.field_font_width.numbase = self.displayBase
        self.field_font_width.setStatusTip("Make sure that this is an even number to prevent the game from crashing")
        self.field_font_width.valueChanged.connect(lambda: self.treeCall())
        self.field_font_width.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.field_font_width.valueChanged.connect(self.file_content_gfx.fitInView)
        self.field_font_width.hide()
        self.label_font_width = QtWidgets.QLabel(self.page_explorer)
        self.label_font_width.setText("char width")
        self.label_font_width.hide()
        self.layout_font_width = QtWidgets.QVBoxLayout()
        self.layout_font_width.addWidget(self.field_font_width)
        self.layout_font_width.addWidget(self.label_font_width)
        self.layout_font_width.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.field_font_height = BetterSpinBox(self.page_explorer)
        self.field_font_height.setFont(self.font_caps)
        self.field_font_height.setMinimum(0)
        self.field_font_height.isInt = True
        self.field_font_height.numbase = self.displayBase
        self.field_font_height.valueChanged.connect(lambda: self.treeCall())
        self.field_font_height.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.field_font_height.valueChanged.connect(self.file_content_gfx.fitInView)
        self.field_font_height.hide()
        self.label_font_height = QtWidgets.QLabel(self.page_explorer)
        self.label_font_height.setText("char height")
        self.label_font_height.hide()
        self.layout_font_height = QtWidgets.QVBoxLayout()
        self.layout_font_height.addWidget(self.field_font_height)
        self.layout_font_height.addWidget(self.label_font_height)
        self.layout_font_height.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.label_font_indexingSpace = QtWidgets.QLabel(self.page_explorer)
        self.label_font_indexingSpace.setText("indexing space: ")
        self.label_font_indexingSpace.hide()

        self.label_font_charCount = QtWidgets.QLabel(self.page_explorer)
        self.label_font_charCount.setText("char count: ")
        self.label_font_charCount.hide()

        self.label_font_unusedStr = QtWidgets.QLabel(self.page_explorer)
        self.label_font_unusedStr.setText("unused string: ")
        self.label_font_unusedStr.hide()

        self.layout_editzone_row0.addWidget(self.button_file_save)
        self.layout_editzone_row0.addWidget(self.label_file_size)
        self.layout_editzone_row0.addWidget(self.dropdown_gfx_depth)
        self.layout_editzone_row0.addWidget(self.field_address)
        
        self.layout_editzone_row1.addItem(self.layout_colorpick)
        self.layout_editzone_row1.addItem(self.layout_gfx_settings)
        self.layout_editzone_row1.addItem(self.layout_oam_navigation)

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

        self.tree_sdat = EditorTree(self.dialog_sdat)
        self.dialog_sdat.setCentralWidget(self.tree_sdat)
        self.tree_sdat.setColumnCount(3)
        self.tree_sdat.setHeaderLabels(["File ID", "Name", "Type"])
        self.tree_sdat.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        #VX
        self.label_vxHeader_length = QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_length.setText("Duration(frames): ")
        self.label_vxHeader_length.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_vxHeader_length.hide()
        self.field_vxHeader_length = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_length.setFont(self.font_caps)
        self.field_vxHeader_length.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_length.numfill = 8
        self.field_vxHeader_length.isInt = True
        self.field_vxHeader_length.hide()
        self.field_vxHeader_length.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_length = QtWidgets.QVBoxLayout()
        self.layout_vxHeader_length.addWidget(self.label_vxHeader_length)
        self.layout_vxHeader_length.addWidget(self.field_vxHeader_length)

        self.label_vxHeader_framerate = QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_framerate.setText("Frame rate: ")
        self.label_vxHeader_framerate.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_vxHeader_framerate.hide()
        self.field_vxHeader_framerate = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_framerate.setDecimals(16) # increase precision to allow spinbox to respect range
        self.field_vxHeader_framerate.setRange(0x00000000,65535.9999847412109375) # prevent impossible values (max is ffff.ffff)
        #self.field_vxHeader_framerate.numfill = 8
        self.field_vxHeader_framerate.hide()
        self.field_vxHeader_framerate.textChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_framerate = QtWidgets.QVBoxLayout()
        self.layout_vxHeader_framerate.addWidget(self.label_vxHeader_framerate)
        self.layout_vxHeader_framerate.addWidget(self.field_vxHeader_framerate)

        self.label_vxHeader_frameSizeMax = QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_frameSizeMax.setText("Maximal frame data size: ")
        self.label_vxHeader_frameSizeMax.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_vxHeader_frameSizeMax.hide()
        self.field_vxHeader_frameSizeMax = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_frameSizeMax.setFont(self.font_caps)
        self.field_vxHeader_frameSizeMax.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_frameSizeMax.numfill = 8
        self.field_vxHeader_frameSizeMax.isInt = True
        self.field_vxHeader_frameSizeMax.hide()
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
        self.label_vxHeader_streamCount.hide()
        self.field_vxHeader_streamCount = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_streamCount.setFont(self.font_caps)
        self.field_vxHeader_streamCount.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_streamCount.numfill = 8
        self.field_vxHeader_streamCount.isInt = True
        self.field_vxHeader_streamCount.hide()
        self.field_vxHeader_streamCount.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_streamCount = QtWidgets.QVBoxLayout()
        self.layout_vxHeader_streamCount.addWidget(self.label_vxHeader_streamCount)
        self.layout_vxHeader_streamCount.addWidget(self.field_vxHeader_streamCount)

        self.label_vxHeader_sampleRate = QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_sampleRate.setText("Sound sample rate(Hz): ")
        self.label_vxHeader_sampleRate.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_vxHeader_sampleRate.hide()
        self.field_vxHeader_sampleRate = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_sampleRate.setFont(self.font_caps)
        self.field_vxHeader_sampleRate.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_sampleRate.numfill = 8
        self.field_vxHeader_sampleRate.isInt = True
        self.field_vxHeader_sampleRate.hide()
        self.field_vxHeader_sampleRate.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_sampleRate = QtWidgets.QVBoxLayout()
        self.layout_vxHeader_sampleRate.addWidget(self.label_vxHeader_sampleRate)
        self.layout_vxHeader_sampleRate.addWidget(self.field_vxHeader_sampleRate)

        self.label_vxHeader_audioExtraDataOffset = QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_audioExtraDataOffset.setText("Extra audio data offset: ")
        self.label_vxHeader_audioExtraDataOffset.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_vxHeader_audioExtraDataOffset.hide()
        self.field_vxHeader_audioExtraDataOffset = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_audioExtraDataOffset.setFont(self.font_caps)
        self.field_vxHeader_audioExtraDataOffset.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_audioExtraDataOffset.numfill = 8
        self.field_vxHeader_audioExtraDataOffset.isInt = True
        self.field_vxHeader_audioExtraDataOffset.hide()
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
        self.label_vxHeader_width.hide()
        self.field_vxHeader_width = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_width.setFont(self.font_caps)
        self.field_vxHeader_width.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_width.numfill = 8
        self.field_vxHeader_width.isInt = True
        self.field_vxHeader_width.hide()
        self.field_vxHeader_width.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_width = QtWidgets.QVBoxLayout()
        self.layout_vxHeader_width.addWidget(self.label_vxHeader_width)
        self.layout_vxHeader_width.addWidget(self.field_vxHeader_width)

        self.label_vxHeader_height = QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_height.setText("Frame height(pixels): ")
        self.label_vxHeader_height.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_vxHeader_height.hide()
        self.field_vxHeader_height = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_height.setFont(self.font_caps)
        self.field_vxHeader_height.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_height.numfill = 8
        self.field_vxHeader_height.isInt = True
        self.field_vxHeader_height.hide()
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
        self.label_vxHeader_quantiser.hide()
        self.field_vxHeader_quantizer = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_quantizer.setFont(self.font_caps)
        self.field_vxHeader_quantizer.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_quantizer.numfill = 8
        self.field_vxHeader_quantizer.isInt = True
        self.field_vxHeader_quantizer.hide()
        self.field_vxHeader_quantizer.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_quantiser = QtWidgets.QVBoxLayout()
        self.layout_vxHeader_quantiser.addWidget(self.label_vxHeader_quantiser)
        self.layout_vxHeader_quantiser.addWidget(self.field_vxHeader_quantizer)

        self.label_vxHeader_seekTableOffset = QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_seekTableOffset.setText("Seek table offset: ")
        self.label_vxHeader_seekTableOffset.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_vxHeader_seekTableOffset.hide()
        self.field_vxHeader_seekTableOffset = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_seekTableOffset.setFont(self.font_caps)
        self.field_vxHeader_seekTableOffset.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_seekTableOffset.numfill = 8
        self.field_vxHeader_seekTableOffset.isInt = True
        self.field_vxHeader_seekTableOffset.hide()
        self.field_vxHeader_seekTableOffset.valueChanged.connect(lambda: self.button_file_save.setEnabled(True))
        self.layout_vxHeader_seekTableOffset = QtWidgets.QVBoxLayout()
        self.layout_vxHeader_seekTableOffset.addWidget(self.label_vxHeader_seekTableOffset)
        self.layout_vxHeader_seekTableOffset.addWidget(self.field_vxHeader_seekTableOffset)

        self.label_vxHeader_seekTableEntryCount = QtWidgets.QLabel(self.page_explorer)
        self.label_vxHeader_seekTableEntryCount.setText("Seek table entry count: ")
        self.label_vxHeader_seekTableEntryCount.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_vxHeader_seekTableEntryCount.hide()
        self.field_vxHeader_seekTableEntryCount = BetterSpinBox(self.page_explorer)
        self.field_vxHeader_seekTableEntryCount.setFont(self.font_caps)
        self.field_vxHeader_seekTableEntryCount.setRange(0x00000000, 0xFFFFFFFF) # prevent impossible values
        self.field_vxHeader_seekTableEntryCount.numfill = 8
        self.field_vxHeader_seekTableEntryCount.isInt = True
        self.field_vxHeader_seekTableEntryCount.hide()
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
            self.label_tiles_per_column
            ]
        self.WIDGETS_OAM: list[QtWidgets.QWidget] = [
            self.file_content_oam,
            self.tabs_oam,
            self.dropdown_oam_entry
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
            self.button_palettepick_0,
            self.button_palettepick_1
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
        for i in range(256):
            self.WIDGETS_GRAPHIC.append(getattr(self, f"button_palettepick_{i}"))

        # Level Editor(Coming Soon™)
        self.layout_level_editpannel = QtWidgets.QVBoxLayout()

        self.dropdown_editor_area = QtWidgets.QComboBox(self.page_leveleditor)
        self.dropdown_editor_area.setToolTip("Choose an area to modify")
        self.gfx_scene_level = GFXView()


        self.page_leveleditor.layout().addItem(self.layout_level_editpannel)
        self.layout_level_editpannel.addWidget(self.dropdown_editor_area)

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

        self.page_tweaks_animations = QtWidgets.QWidget(self.tabs_tweaks)
        self.page_tweaks_animations.setLayout(QtWidgets.QGridLayout())

        self.page_tweaks_misc = QtWidgets.QWidget(self.tabs_tweaks)
        self.page_tweaks_misc.setLayout(QtWidgets.QGridLayout())

        self.tabs_tweaks.addTab(self.page_tweaks_stats, "Stats")


        self.tabs_tweaks.addTab(self.page_tweaks_physics, "Physics")


        self.tabs_tweaks.addTab(self.page_tweaks_behaviour, "Behaviour")

        self.checkbox_paralyzed = QtWidgets.QCheckBox(self.page_tweaks_behaviour)
        self.page_tweaks_behaviour.layout().addWidget(self.checkbox_paralyzed)


        self.tabs_tweaks.addTab(self.page_tweaks_animations, "Animations")


        self.tabs_tweaks.addTab(self.page_tweaks_misc, "Misc.")


        # Patches
        self.tree_patches = EditorTree(self.page_patches)
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
        self.window_progress.show() # show progress on task

    def progressUpdate(self, completed: str, status: str=""):
        self.progress.setValue(completed)
        self.label_progress.setText(status)
        app.processEvents()

    def progressHide(self):
        self.progress.setValue(0)
        self.label_progress.setText("")
        self.window_progress.close() # show progress on task

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
        return [data, name, obj, obj2]
        
    def set_dialog_button_name(self, dialog: QtWidgets.QDialog, oldtext: str, newtext: str):
        for btn in dialog.findChildren(QtWidgets.QPushButton):
            if btn.text() == self.tr(oldtext):
                QtCore.QTimer.singleShot(0, lambda btn=btn: btn.setText(newtext))
        dialog.findChild(QtWidgets.QTreeView).selectionModel().currentChanged.connect(
            lambda: self.set_dialog_button_name(dialog, oldtext, "Import")
            )
    
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
            self.progressShow()

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
        self.dropdown_editor_area.addItems([item.text(1) for item in self.tree.findItems("^[a-z][0-9][0-9]", QtCore.Qt.MatchFlag.MatchRegularExpression, 1)])

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
        self.dropdown_editor_area.clear()

    def exportCall(self, item: QtWidgets.QTreeWidgetItem):
        dialog = QtWidgets.QFileDialog(
                self,
                "Save ROM",
                "",
                "Folders Only",
                options=QtWidgets.QFileDialog.Option.DontUseNativeDialog,
                )
        dialog.setAcceptMode(dialog.AcceptMode.AcceptSave)
        dialog.setFileMode(dialog.FileMode.Directory)
        self.set_dialog_button_name(dialog, "&Open", "Save")
        if dialog.exec(): # if you saved a file
            dialog_formatselect = QtWidgets.QDialog(self)
            dialog_formatselect.setWindowTitle("Choose format and compression")
            dropdown_formatselect = QtWidgets.QComboBox(dialog_formatselect)
            dropdown_formatselect.addItems(["Raw", "English dialogue"])
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
                selectedFiles = dialog.selectedFiles()
                print("Selected: " + dropdown_formatselect.currentText() + ", " + dropdown_compressselect.currentText())
                print("Item: " + item.text(0))
                if item != None:
                    fileData = self.file_fromItem(item)
                    if fileData == [b'', "", None]:
                        print("could not fetch data from tree item")
                        return
                    elif not isinstance(fileData[0], (bytes, bytearray)): # both bytes and bytearray are essentially the same, but need to be checked for separately
                        fileData[0] = fileData[0][1].save()
                        print(fileData[0])
                        if isinstance(fileData[0], tuple):
                            fileData[0] = fileData[0][0]
                    if not "Folder" in item.text(2): # if file
                        extract(*fileData[:2], path=selectedFiles[0], format=dropdown_formatselect.currentText(), compress=dropdown_compressselect.currentIndex())
                    else: # if folder
                        folder_path = os.path.join(selectedFiles[0] + "/" + w.fileToEdit_name.removesuffix(".Folder"))
                        if os.path.exists(folder_path) == False:
                            print("Folder " + folder_path  + " will be created")
                            os.makedirs(folder_path)
                        else:
                            print("Folder " + folder_path  + " will be used")
                        print(item.childCount() - 1)
                        for i in range(item.childCount()):
                            print(item.child(i).text(0))
                            extract(*self.file_fromItem(item.child(i))[:2], path=selectedFiles[0] + "/" + w.fileToEdit_name.removesuffix(".Folder"), format=dropdown_formatselect.currentText(), compress=dropdown_compressselect.currentIndex())#, w.fileToEdit_name.replace(".Folder", "/")
                            #str(w.tree.currentItem().child(i).text(1) + "." + w.tree.currentItem().child(i).text(2)), 

    def replacebynameCall(self):
        if hasattr(w.rom, "name"):
            dialog = QtWidgets.QFileDialog(
                self,
                "Import File",
                "",
                "All Files (*)",
                options=QtWidgets.QFileDialog.Option.DontUseNativeDialog,
                )
            self.set_dialog_button_name(dialog, "&Open", "Import")
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

    def replaceCall(self, item: QtWidgets.QTreeWidgetItem):
        if hasattr(w.rom, "name"):
            dialog = QtWidgets.QFileDialog(
                self,
                "Import File",
                "",
                "All Files (*)",
                options=QtWidgets.QFileDialog.Option.DontUseNativeDialog,
                )
            dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles) # allow more than one file to be selected
            self.set_dialog_button_name(dialog, "&Open", "Import")
            if dialog.exec(): # if file you're trying to replace is in ROM
                    selectedFiles = dialog.selectedFiles()
                    dialog2 = QtWidgets.QMessageBox()
                    dialog2.setWindowTitle("Import Status")
                    dialog2.setWindowIcon(QtGui.QIcon('icons\\information.png'))
                    dialog2.setText("File import failed!")
                    fileInfo = self.file_fromItem(item)
                    if str(selectedFiles[0]).split("/")[-1].split(".")[1] == "txt" and re.search(r".*(_\d+)$", str(selectedFiles[0]).split("/")[-1].split(".")[0]): # fileExt and fileName
                        dialogue = lib.dialogue.DialogueFile(fileInfo[2][fileInfo[2].index(fileInfo[0])]) # object created before loop to improve performance
                    for file in selectedFiles:
                        with open(file, 'rb') as f:
                            fileEdited = f.read()
                            try:
                                fileName = str(f.name).split("/")[-1].split(".")[0]
                                fileExt = str(f.name).split("/")[-1].split(".")[1]
                            except IndexError:
                                fileName = ""
                                fileExt = ""
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
                            elif not isinstance(fileInfo[2], None):
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

                    if isinstance(fileInfo[2], bytearray): # other
                            fileInfo[2][fileInfo[2].index(fileInfo[0]):fileInfo[2].index(fileInfo[0])+len(fileInfo[0])] = data
                            print(data[:0x15].hex())
                    elif fileInfo[3] == None: # rom files
                        fileInfo[2][fileInfo[2].index(fileInfo[0])] = data
                        print(data[:0x15].hex())
                    elif any(x for x in self.sdat.__dict__.values() if x == fileInfo[3]):
                        newName = fileName
                        oldObject = fileInfo[0][1]
                        newObject = type(oldObject).fromFile(f.name)
                        if isinstance(fileInfo[0][1], ndspy.soundSequenceArchive.soundSequence.SSEQ): # bankID fix (defaults to 0)
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
                        fileInfo[3][fileInfo[3].index(fileInfo[0])] = (newName, newObject) 
                        fileInfo[2][self.sdat.fileID] = self.sdat.save()
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

    def OAM_updateItemGFX(self, obj_index: int, item: OAMObjectItem | None=None): # creates and returns an item if none specified
        gfxsec: lib.graphic.GraphicSection = self.fileEdited_object.gfxsec
        if len(gfxsec.graphics) <= 0:
            print("no graphics in section!")
            return
        depth = gfxsec.graphics[0].depth//2
        indexingFactor = 1 # I guess this is changed based on the size of assembled gfx
        # in 4bpp, oam tile id * indexingFactor = vram tile id
        # in 8bpp, oam tile id * indexingFactor // 2 = vram tile id
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
        index_img = self.fileEdited_object.frame[2]
        if index_img >= len(gfxsec.graphics):
            print(f"Graphic Section {index_img} does not exist!")
            return
        if gfxsec.graphics[index_img].oam_tile_indexing == 0:
            indexingFactor = 1
        elif gfxsec.graphics[index_img].oam_tile_indexing == 0x18:
            indexingFactor = 4
        else:
            print(f"unhandled tile indexing mode: {gfxsec.graphics[index_img].oam_tile_indexing}")
        pal_off = gfxsec.graphics[index_img].offset_start + gfxsec.graphics[index_img].palette_offset+0xc
        pal = [0xffffffff]*(gfxsec.graphics[index_img].unk13 & 0xf0)
        pal.extend(lib.datconv.BGR15_to_ARGB32(self.fileEdited_object.auxfile.data[pal_off:pal_off+gfxsec.graphics[index_img].palette_size]))
        tileId = gfxsec.graphics[index_img].oam_tile_offset + obj.tileId
        # multiply oam tile id by indexingFactor and 4bpp tile size to get vram tile id
        gfxOffset = gfxsec.graphics[index_img].offset_start + gfxsec.graphics[index_img].gfx_offset + int(tileId*indexingFactor*32) # 8*8pixels*4bpp/8bits = 32bytes
        #print(f"offset: {gfxOffset:04X}")
        #print(f"tile {tileId:02X}")
        try: #gfxOffset+gfxsec.graphics[index_img].gfx_size
            obj_img = lib.datconv.binToQt(self.fileEdited_object.auxfile.data[gfxOffset:], pal,
                                                *[member for member in lib.datconv.CompressionAlgorithmEnum if member.depth == depth],
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
            obj_item = OAMObjectItem(QtGui.QPixmap.fromImage(obj_img), id=obj_index, editable=(self.tabs_oam.currentWidget()==self.page_oam_frames))
        else:
            obj_item = item
            obj_item.setPixmap(QtGui.QPixmap.fromImage(obj_img))
        obj_item.setPixmap(
            obj_item.pixmap().transformed(QtGui.QTransform().scale(-1 if obj.flip_h else 1,-1 if obj.flip_v else 1)))
        obj_item.setPos(obj.x, obj.y)
        if item == None:
            return obj_item
        
    def OAM_playAnimFrame(self):
        if self.fileDisplayState != "OAM": # prevents crash when loading another file
            self.button_oam_animPlay.autoPause()
            return
        anim: lib.oam.Animation = self.fileEdited_object.oamsec_anim
        frame_index = self.dropdown_oam_animFrame.currentIndex()
        frame = anim.frames[frame_index]
        if self.button_oam_animPlay.counter >= frame[1]:
            #print(f"{self.button_oam_animPlay.counter} vs {frame[1]}")
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
            button_palettepick: HoldButton = getattr(self, f"button_palettepick_{i}")
            if i < len(self.gfx_palette):
                button_palettepick.setStyleSheet(f"background-color: #{self.gfx_palette[i]:08x}; color: white;")
            else:
                button_palettepick.setStyleSheet(f"background-color: white; color: white;") # fill missing colors with white

    def colorpickCall(self, color_index: int, press=None, hold=None):
        #print(color_index)
        button: HoldButton = getattr(self, f"button_palettepick_{color_index}")
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
                    button_palettepick: HoldButton = getattr(self, f"button_palettepick_{i}")
                    button_palettepick.setStyleSheet(f"background-color: #{self.gfx_palette[i]:08x}; color: white;")
                for i in range(color_index2, color_index2+2**depth): # change affected buttons (selected)
                    button_palettepick: HoldButton = getattr(self, f"button_palettepick_{i}")
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
        self.set_dialog_button_name(dialog, "&Open", "Save")
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
            item_sseqplayer = QtWidgets.QTreeWidgetItem(["N/A", "Sequence Player", "SSEQ"]) #SSEQ
            item_strm = QtWidgets.QTreeWidgetItem(["N/A", "Multi-Channel Stream", "STRM"]) #STRM
            item_strmplayer = QtWidgets.QTreeWidgetItem(["N/A", "Stream Player", "STRM"]) #STRM
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
        for widget in self.findChildren(BetterSpinBox): # update all widgets of same type with current settings
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
                            
                            if current_ext == "vx":
                                self.fileDisplayState = "VX"
                            elif current_ext == "sdat":
                                self.fileDisplayState = "Sound"
                            elif "font" in current_name:
                                self.fileDisplayState = "Font"
                            elif ("talk" in current_name or "m_" in current_name):
                                if "en" in current_name:
                                    self.fileDisplayState = "English dialogue"
                                elif "jp" in current_name:
                                    self.fileDisplayState = "Japanese dialogue"
                            elif current_ext == "bin" and any(indicator in current_name for indicator in indicator_list_gfx):
                                self.fileDisplayState = "Graphics"
                            elif current_ext == "bin" and any(indicator.replace("fnt", "dat") in current_name for indicator in indicator_list_gfx):
                                self.fileDisplayState = "OAM"
                            else:
                                self.fileDisplayState = "None"
                    else:
                        self.fileDisplayState = self.fileDisplayMode

                    if self.fileDisplayState == "English dialogue": # if english text
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
                        if sender in self.FILEOPEN_WIDGETS: # reset from viewing font
                            self.tile_width = self.field_tile_width.value()
                            self.tile_height = self.field_tile_height.value()
                            if current_name == "face": # for convenience
                                self.tiles_per_column = 7
                                self.tiles_per_row = 6
                                self.field_tiles_per_column.setValue(self.tiles_per_column)
                                self.field_tiles_per_row.setValue(self.tiles_per_row)
                            self.dropdown_gfx_index.clear()
                            self.dropdown_gfx_subindex.clear()
                            try:
                                self.fileEdited_object = lib.graphic.File(self.rom.files[current_id])
                                for i in range(len(self.fileEdited_object.address_list)):
                                    self.dropdown_gfx_index.addItem(f"entry {i}")
                                self.dropdown_gfx_index.setCurrentIndex(0)
                            except AssertionError:
                                try:
                                    self.fileEdited_object = lib.graphic.GraphicSection(self.rom.files[current_id])
                                except AssertionError:
                                    print("failed to load graphic entry table!")
                                    self.fileEdited_object = None
                        if self.fileEdited_object != None:
                            if isinstance(self.fileEdited_object, lib.graphic.File):
                                gfxsec = lib.graphic.GraphicSection.fromParent(self.fileEdited_object, self.dropdown_gfx_index.currentIndex())
                            elif isinstance(self.fileEdited_object, lib.graphic.GraphicSection):
                                gfxsec = self.fileEdited_object
                            if sender == self.dropdown_gfx_index or sender in self.FILEOPEN_WIDGETS: # if graphic section changed, reload header list
                                self.dropdown_gfx_subindex.clear()
                                for i in range(len(gfxsec.graphics)):
                                    self.dropdown_gfx_subindex.addItem(f"image {i}")
                                self.dropdown_gfx_subindex.setCurrentIndex(0)
                            if self.dropdown_gfx_subindex.count() > 0:
                                if sender == self.dropdown_gfx_index or sender == self.dropdown_gfx_subindex or sender in self.FILEOPEN_WIDGETS or sender == self.checkbox_depthUpdate:
                                    header_index = self.dropdown_gfx_subindex.currentIndex()
                                    gfxOffset = gfxsec.graphics[header_index].offset_start + gfxsec.graphics[header_index].gfx_offset
                                    pal_off = gfxsec.graphics[header_index].offset_start + gfxsec.graphics[header_index].palette_offset+0xc
                                    self.relative_address = gfxOffset
                                    self.field_address.setRange(self.base_address+gfxOffset, self.base_address + gfxOffset+gfxsec.graphics[header_index].gfx_size)
                                    self.field_address.setValue(self.base_address+self.relative_address)
                                    print(f"{gfxsec.entryCount} entries")
                                    print(f"oam tile offset: {gfxsec.graphics[header_index].oam_tile_offset:02X}")
                                    print(f"oam_tile_indexing: {gfxsec.graphics[header_index].oam_tile_indexing:02X}")
                                    print(f"unk08: {gfxsec.graphics[header_index].unk08:02X}")
                                    print(f"unk09: {gfxsec.graphics[header_index].unk09:02X}")
                                    print(f"unk13 & 0F: {gfxsec.graphics[header_index].unk13 & 0x0f:02X}")
                                    if self.checkbox_depthUpdate.isChecked():
                                        if gfxsec.graphics[header_index].depth//2 == 4:
                                            self.dropdown_gfx_depth.setCurrentIndex(1)
                                        elif gfxsec.graphics[header_index].depth//2 == 8:
                                            self.dropdown_gfx_depth.setCurrentIndex(2)
                                        else:
                                            print(f"unrecognized depth {gfxsec.graphics[header_index].depth}")
                                            self.dropdown_gfx_depth.setCurrentIndex(1)
                                    pal = [0xffffffff]*(gfxsec.graphics[header_index].unk13 & 0xf0)
                                    pal.extend(lib.datconv.BGR15_to_ARGB32(self.rom.files[current_id][pal_off:pal_off+gfxsec.graphics[header_index].palette_size]))
                                    self.setPalette(pal)
                            else:
                                print(f"{gfxsec.entryCount} graphic entries!")
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
                            self.fileEdited_object.oamsec_anim = lib.oam.Animation(self.fileEdited_object.oamsec, self.dropdown_oam_anim.currentIndex())
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
                        
                        if sender in [self.dropdown_oam_animFrame, self.dropdown_oam_entry, self.dropdown_oam_anim, *self.FILEOPEN_WIDGETS]:
                            if (self.dropdown_oam_animFrame.previousIndex != self.dropdown_oam_animFrame.currentIndex() and self.button_file_save.isEnabled()):
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
                                          self.dropdown_oam_objFrame, self.tabs_oam, self.button_reload, *self.FILEOPEN_WIDGETS]:
                                self.file_content_oam.scene().clear()
                                sceneRect = self.file_content_oam.sceneRect()
                                crosshairPen = QtGui.QPen()
                                crosshairPen.setWidthF(0.05) # extra thin line
                                self.file_content_oam.scene().addRect(sceneRect)
                                self.file_content_oam.scene().addLine(sceneRect.left(), 0, sceneRect.right(), 0, crosshairPen)
                                self.file_content_oam.scene().addLine(0, sceneRect.top(), 0, sceneRect.bottom(), crosshairPen)
                                if not isinstance(sender, BetterSpinBox) and sender != self.dropdown_oam_animFrame:
                                    self.button_file_save.setDisabled(True)
                                self.fileEdited_object.objs.clear()
                                self.dropdown_oam_obj.clear()
                                #print("start")
                                item_list = []
                                for i in range(self.fileEdited_object.frame[1]):
                                    if i >= 128:
                                        print("Object limit reached! Proceed at your own risk!")
                                        break
                                    self.dropdown_oam_obj.addItem(f"object {i}")
                                    obj_offset = self.fileEdited_object.oamsec.frameTable_offset + self.fileEdited_object.frame[0] + i*0x04
                                    self.fileEdited_object.objs.append(lib.oam.Object(self.fileEdited_object.oamsec.data[obj_offset:obj_offset+0x04]))
                                    obj_item = self.OAM_updateItemGFX(i)
                                    item_list.append(obj_item)
                                item_list.reverse()
                                for i in range(len(item_list)):
                                    self.file_content_oam.scene().addItem(item_list[i])

                                if sender == self.dropdown_oam_entry:
                                    self.file_content_oam.fitInView()
                                self.file_content_oam.item_current = item_list[-1]
                                self.dropdown_oam_obj.previousIndex = 0
                                self.dropdown_oam_obj.setCurrentIndex(0)

                            if sender in [self.button_oam_objSelect, self.dropdown_oam_obj, self.dropdown_oam_entry, self.dropdown_oam_objFrame, self.tabs_oam, self.file_content_oam.scene(), *self.FILEOPEN_WIDGETS]:
                                #print(f"{frame[0]:02X}")
                                #print(f"frame: {self.dropdown_oam_objFrame.currentIndex()}")
                                if self.tabs_oam.currentWidget()!=self.page_oam_frames:return
                                if self.dropdown_oam_obj.currentIndex() == -1: return
                                if self.dropdown_oam_obj.previousIndex != self.dropdown_oam_obj.currentIndex() and self.button_file_save.isEnabled(): # save state of previous object
                                    obj_prev = self.fileEdited_object.objs[self.dropdown_oam_obj.previousIndex]
                                    obj_prev.tileId = self.field_objTileId.value()
                                    obj_prev.flip_h = self.checkbox_objFlipH.isChecked()
                                    obj_prev.flip_v = self.checkbox_objFlipV.isChecked()
                                    obj_prev.sizeIndex = self.slider_objSizeIndex.sl.value()
                                    obj_prev.shape = self.buttonGroup_oam_objShape.checkedId()
                                    obj_prev.x = self.field_objX.value()
                                    obj_prev.y = self.field_objY.value()
                                offset = self.fileEdited_object.oamsec.frameTable_offset + self.fileEdited_object.frame[0] + self.dropdown_oam_obj.currentIndex()*0x04
                                self.relative_address = self.fileEdited_object.address_list[self.dropdown_oam_entry.currentIndex()] + offset
                                self.field_address.setValue(self.relative_address + self.base_address)
                                obj = self.fileEdited_object.objs[self.dropdown_oam_obj.currentIndex()]#lib.oam.Object(oamsec.data[offset:offset+0x04])
                                self.dropdown_oam_obj.previousIndex = self.dropdown_oam_obj.currentIndex()
                                if sender in [self.dropdown_oam_obj, self.button_oam_objSelect]:
                                    for item in self.file_content_oam.scene().items():
                                        if isinstance(item, OAMObjectItem):
                                            item.setSelected(item.obj_id == self.dropdown_oam_obj.currentIndex())
                                self.field_objTileId.setValue(obj.tileId)
                                self.checkbox_objFlipH.setChecked(obj.flip_h)
                                self.checkbox_objFlipV.setChecked(obj.flip_v)
                                self.slider_objSizeIndex.sl.setValue(obj.sizeIndex)
                                self.group_oam_objShape.findChildren(QtWidgets.QRadioButton)[obj.shape].setChecked(True)
                                self.slider_objSizeIndex.setLabels(lib.oam.SPRITE_DIMENSIONS[self.buttonGroup_oam_objShape.checkedId()])
                                self.field_objX.setValue(obj.x)
                                self.field_objY.setValue(obj.y)
                        else:
                            print("empty frame!")
                    elif self.fileDisplayState == "Font":
                        self.widget_set = "Font"
                        if sender in self.FILEOPEN_WIDGETS:
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
                                                   algorithm=lib.datconv.CompressionAlgorithmEnum.ONEBPP,
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
                            self.field_vxHeader_frameSizeMax.setValue(self.fileEdited_object.frame_size_max)
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

    def treeBaseUpdate(self, tree: EditorTree):
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
        modes = ["Empty", "Hex", "Text", "Graphics", "OAM", "Font", "Sound", "VX"]
        # Associates each mode with a set of widgets to show or hide
        widget_sets = [self.WIDGETS_EMPTY, self.WIDGETS_HEX, self.WIDGETS_TEXT, self.WIDGETS_GRAPHIC, self.WIDGETS_OAM, self.WIDGETS_FONT, self.WIDGETS_SOUND, self.WIDGETS_VX]

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
            if self.file_content_gfx.sceneRect().width() != 0: # disallow division
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
                    for obj_index in range(self.dropdown_oam_obj.count()):
                        offset = section.frameTable_offset + frame[0] + obj_index*0x04
                        obj = lib.oam.Object(section.data[offset:offset+0x04])
                        if obj_index == self.dropdown_oam_obj.currentIndex(): # save current changes
                            obj.tileId = self.field_objTileId.value()
                            obj.tileId_add = self.field_objTileId.value() & 0x300
                            obj.flip_h = self.checkbox_objFlipH.isChecked()
                            obj.flip_v = self.checkbox_objFlipV.isChecked()
                            obj.sizeIndex = self.slider_objSizeIndex.sl.value()
                            obj.shape = self.buttonGroup_oam_objShape.checkedId()
                            obj.x = self.field_objX.value()
                            obj.y = self.field_objY.value()
                        else: # save cached changes
                            obj = self.fileEdited_object.objs[obj_index]
                        save_data += obj.toBytes()
                    offset2 = section.offset_start + section.frameTable_offset + frame[0]
                    w.rom.files[file_id][offset2:offset2+frame[1]*0x04] = save_data
                elif self.tabs_oam.currentWidget()==self.page_oam_anims:
                    if -1 in [self.dropdown_oam_entry.currentIndex(), self.dropdown_oam_anim.currentIndex(),
                            self.dropdown_oam_animFrame.currentIndex()]:
                        print("no valid animation data to save!")
                        return
                    section = self.fileEdited_object.oamsec
                    anim = self.fileEdited_object.oamsec_anim
                    anim.isLooping = self.checkbox_oam_animLoop.isChecked()
                    anim.loopStart = self.field_oam_animLoopStart.value()
                    anim.frames[self.dropdown_oam_animFrame.currentIndex()] = [
                        self.field_oam_animFrameId.value(),
                        self.field_oam_animFrameDuration.value()
                    ]
                    save_data = anim.toBytes()
                    print(save_data.hex())
                    save_offset =  self.fileEdited_object.oamsec.offset_start+self.fileEdited_object.oamsec.animTable_offset+anim.frames_offset
                    print(w.rom.files[file_id][save_offset:save_offset+len(anim.frames)*0x02].hex())
                    w.rom.files[file_id][save_offset:save_offset+len(anim.frames)*0x02] = save_data
                # update data of oamsec
                self.fileEdited_object.oamsec = lib.oam.OAMSection(self.fileEdited_object, self.dropdown_oam_entry.currentIndex())

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

        for item_i in range(len(tree_list)):# Iterate through patch groups
            if tree_list[item_i].childCount() != 0:
                if tree_list[item_i].checkState(0) != self.tree_patches_checkboxes[item_i]: # if checkstate changed
                    for child_i in range(tree_list[item_i].childCount()): # update children
                        tree_list[item_i].child(child_i).setCheckState(0, tree_list[item_i].checkState(0))
                else: # update according to children
                    subPatchMatches = 0
                    for child_i in range(tree_list[item_i].childCount()):
                        if tree_list[item_i].child(child_i).checkState(0) == QtCore.Qt.CheckState.Checked:
                            subPatchMatches += 1
                    if subPatchMatches == tree_list[item_i].childCount(): # Check for already applied patches
                            tree_list[item_i].setCheckState(0, QtCore.Qt.CheckState.Checked)
                    elif subPatchMatches > 0:
                        tree_list[item_i].setCheckState(0, QtCore.Qt.CheckState.PartiallyChecked)
                    else:
                        tree_list[item_i].setCheckState(0, QtCore.Qt.CheckState.Unchecked)

        for item_i in range(len(tree_list)):# Go through unchecked ones first
            if (tree_list[item_i].checkState(0) == QtCore.Qt.CheckState.Unchecked):
                # Revert patch
                if tree_list[item_i].childCount() == 0: # if not a patch group
                    newData = bytes.fromhex(patch_list[item_i][3])
                    rom_patched[patch_list[item_i][0]:patch_list[item_i][0]+len(newData)] = newData # write og data
                        
        for item_i in range(len(tree_list)):# Then through active patches
            if (tree_list[item_i].checkState(0) == QtCore.Qt.CheckState.Checked):
                # Apply patch
                if tree_list[item_i].childCount() == 0: # if not a patch group\
                    newData = patch_list[item_i][4]
                    for s in range(len(patch_list[item_i][4])):
                        if newData[s] == "-":
                            newData = newData[:s] + patch_list[item_i][3][s] + newData[s+1:] # replace '-' with og data
                    newData = bytes.fromhex(newData)
                    rom_patched[patch_list[item_i][0]:patch_list[item_i][0]+len(newData)] = newData # write patch data

        for item_i in range(len(tree_list)):# Iterate through all patches
            self.tree_patches_checkboxes[item_i] = tree_list[item_i].checkState(0) #and update checkbox state list

        self.rom = ndspy.rom.NintendoDSRom(rom_patched)# update the editor with patched ROM
        self.tree_patches.blockSignals(False)

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()

# Draw contents of tile viewer
def draw_tilesQImage_fromBytes(view: GFXView, data: bytearray, algorithm=lib.datconv.CompressionAlgorithmEnum.ONEBPP,  grid: bool=True):
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
                for text in text_list:
                    data[text_list.index(text)] = bytes(text, "utf-8")
            except AssertionError: # not a real dialogue file
                data = bytes(lib.dialogue.DialogueFile.binToText(data), "utf-8")
        elif format == "VX":
            #ext = ".png"
            #data = library.act.ActImagine(data).interpret_vx()
            lib.act.ActImagine(data).interpret_vx() # needs to allow specific file location
            return
        else:
            print("could not find method for converting to specified format.")
            return
    if compress == 1:
        data = ndspy.lz10.compress(data)

    print(os.path.join(path + "/" + name.split(".")[0] + ext))
    if isinstance(data, bytes): # one file
        with open(os.path.join(path + "/" + name.split(".")[0] + ext), 'wb') as f:
            f.write(data)
    else: # list of bytes
        for subdata in data:
            with open(os.path.join(path + "/" + name.split(".")[0] + "_" + str(data.index(subdata)) + ext), 'wb') as f:
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