from PyQt6 import QtGui, QtWidgets, QtCore, QtQuickWidgets, QtQuick
import lib

class Toolbar(QtWidgets.QToolBar):
    def __init__(self, *args, span: list[int]=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.SPAN = span
        if self.SPAN != None:
            self.setMinimumSize(self.SPAN[0], self.SPAN[0])
            self.orientationChanged.connect(lambda: self.setMaximumSize(
                self.SPAN[1] if self.orientation() == QtCore.Qt.Orientation.Horizontal else self.SPAN[0],
                self.SPAN[0] if self.orientation() == QtCore.Qt.Orientation.Horizontal else self.SPAN[1]))

class View(QtWidgets.QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.SCALE_MIN = 0.075
        self.SCALE_MAX = 50
        self.SCALE_FACTOR = 1.25
        #Antialiasing:
        # OAMView = prevent weird scaling artifacts on overlapping items
        # LevelView = Fix details disappearing at certain zoom levels
        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        self.setOptimizationFlags(QtWidgets.QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing |
                                  QtWidgets.QGraphicsView.OptimizationFlag.DontSavePainterState)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setScene(QtWidgets.QGraphicsScene())
        self.scene().setParent(self) # allow to find MainWindow from scene
        self.setMouseTracking(True)
        self.mousePressed = False
        self.mouseLeftPressed = False
        self.mouseRightPressed = False

    def fitInView2(self, scale=True):
        self.setSceneRect(self.scene().itemsBoundingRect())
        self.fitInView(self.sceneRect(), QtCore.Qt.AspectRatioMode.KeepAspectRatio if scale else QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding)
    
    def mousePressEvent(self, event):
        #print("QGraphicsView mousePress")
        self.mousePressed = True
        self.mouseLeftPressed = (event.button() == QtCore.Qt.MouseButton.LeftButton)
        self.mouseRightPressed = (event.button() == QtCore.Qt.MouseButton.RightButton)
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        #print("QGraphicsView mouseRelease")
        if self.mousePressed:
            self.mousePressed = False
            self.mouseLeftPressed = False
            self.mouseRightPressed = False
        super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event):
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                factor = self.SCALE_FACTOR
                if self.transform().m11() >= self.SCALE_MAX:
                    factor = 1
            else:
                factor = 1/self.SCALE_FACTOR
                if self.transform().m11() <= self.SCALE_MIN:
                    factor = 1
            trans = QtGui.QTransform(self.transform().m11()*factor,0,0,0,self.transform().m22()*factor,0, 0, 0, 1)
            self.setTransform(trans)

        elif event.modifiers() == QtCore.Qt.KeyboardModifier.ShiftModifier:
            self.horizontalScrollBar().setSliderPosition(self.horizontalScrollBar().sliderPosition()-event.angleDelta().y())
        else:
            self.verticalScrollBar().setSliderPosition(self.verticalScrollBar().sliderPosition()-event.angleDelta().y())


class GFXView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.horizontalScrollBar().setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        self.verticalScrollBar().setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        self._graphic = QtWidgets.QGraphicsPixmapItem()
        self.scene().addItem(self._graphic)
        self.pen = QtGui.QPen()
        self.pen.setColor(0x00010101) # grayscale color for indexed images
        self.start = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.end_previous = QtCore.QPoint()
        self.mousePressed = False
        self.draw_mode = "pixel"
        self.rectangle = None # used for drawing rectangles

    def resetScene(self):
        self.scene().clear()
        self.rectangle = None
        self._graphic = QtWidgets.QGraphicsPixmapItem()
        self.scene().addItem(self._graphic)

    #def setGraphic(self, pixmap: QtGui.QPixmap=None):
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
            img.setColorTable(self.window().gfx_palette) # re-apply colors
            self._graphic.setPixmap(QtGui.QPixmap.fromImage(img, QtCore.Qt.ImageConversionFlag.NoFormatConversion))
            self.window().button_file_save.setDisabled(False)
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
        super().mouseMoveEvent(event) # allow Anchor under mouse
        #print("QGraphicsView mouseMove")
        self.end = self.mapToScene(event.pos())
        if self._graphic.isUnderMouse():
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        else:
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        if self.mousePressed:
            self.drawShape()
        if self.draw_mode != "rectangle":
            self.end_previous = self.end

    def mouseReleaseEvent(self, event):
        #print("QGraphicsView mouseRelease")
        self.mousePressed = False

class OAMView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_current: OAMObjectItem | None = None

class TilesetView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_spacing = 1
        self.item_columns = 16
        self.metaTiles: list[LevelTileItem] = []
        self.item_first = None # first selected item
        self.scene().selectionChanged.connect(self.selectionChange)
        self.shortcut_left = QtGui.QShortcut(QtGui.QKeySequence("left"), self, lambda: self.moveSelection(-1), context=QtCore.Qt.ShortcutContext.WidgetShortcut)
        self.shortcut_right = QtGui.QShortcut(QtGui.QKeySequence("right"), self, lambda: self.moveSelection(1), context=QtCore.Qt.ShortcutContext.WidgetShortcut)
        self.shortcut_up = QtGui.QShortcut(QtGui.QKeySequence("up"), self, lambda: self.moveSelection(-self.item_columns), context=QtCore.Qt.ShortcutContext.WidgetShortcut)
        self.shortcut_down = QtGui.QShortcut(QtGui.QKeySequence("down"), self, lambda: self.moveSelection(self.item_columns), context=QtCore.Qt.ShortcutContext.WidgetShortcut)

    def moveSelection(self, direction:int):
        if len(self.scene().selectedItems()) >= 1:
            self.item_first.setSelected(False)
            self.item_first = self.metaTiles[min(max(0, self.metaTiles.index(self.item_first)+direction), len(self.metaTiles)-1)]
            if self.item_first != None:
                self.item_first.setSelected(True)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        item_dest = self.itemAt(event.pos())
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ShiftModifier and not None in [self.item_first, item_dest]:
            #print(self.item_first.pos(), item_dest.pos())
            select_rect = QtCore.QRectF(self.item_first.pos(), item_dest.pos())
            select_rect.setHeight(1 if select_rect.height() == 0 else select_rect.height())
            select_rect.setWidth(1 if select_rect.width() == 0 else select_rect.width())
            items = [item for item in self.scene().items() if item.sceneBoundingRect().intersects(select_rect)]
            for item in items:
                item.setSelected(True)
        else:
            super().mousePressEvent(event)
    
    def selectionChange(self):
        #print(self.scene().selectedItems())
        if len(self.scene().selectedItems()) == 1:
            self.item_first = self.scene().selectedItems()[0]

class LevelView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tileGroups: list[list[list[LevelTileItem]]] = []

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.levelInteract(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.levelInteract(event)

    def levelInteract(self, event: QtGui.QMouseEvent):
        if not self.mousePressed: return
        if len(self.window().gfx_scene_tileset.scene().selectedItems()) > 0:
            if self.mouseLeftPressed:
                self.tileDraw(event.pos())
            elif self.mouseRightPressed:
                self.tilePick(event.pos(), event.modifiers() == QtCore.Qt.KeyboardModifier.ShiftModifier)
        else:
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                # select screen to swap position?
                print("screen swap")
                pass
            elif event.button() == QtCore.Qt.MouseButton.RightButton:
                # bring up contextual menu to modify screen in room layout
                item_target = self.itemAt(event.pos())
                if isinstance(item_target, LevelTileItem):
                    print(f"screen ID: 0x{item_target.screen:02X}")

    def tileDraw(self, pos: QtCore.QPoint):
        sItem_event = self.window().gfx_scene_tileset.item_first
        for sItem in self.window().gfx_scene_tileset.scene().selectedItems():
            sItem_delta = sItem.pos().toPoint()-sItem_event.pos().toPoint()
            sItem_delta_spacing = QtCore.QPoint(sItem_delta.x()//16, sItem_delta.y()//16)
            sItem_delta_transformed = (sItem_delta-sItem_delta_spacing)*self.window().gfx_scene_level.transform().m11()
            item_target = self.itemAt(pos+sItem_delta_transformed)
            if isinstance(item_target, LevelTileItem):
                for item in item_target.tileGroup:
                    if item != sItem:
                        item.tileReplace(sItem)
                        self.window().button_level_save.setEnabled(True)
                self.window().levelEdited_object.levels[self.window().dropdown_level_type.currentIndex()].screens[item_target.screen][item_target.index] = item_target.id
        
    def tilePick(self, pos: QtCore.QPoint, keepSelection=False):
        item_target = self.itemAt(pos)
        if not keepSelection:
            for item in self.window().gfx_scene_tileset.scene().selectedItems():
                item.setSelected(False)
        if isinstance(item_target, LevelTileItem):
            self.window().gfx_scene_tileset.metaTiles[item_target.id].setSelected(True)

class PixmapItem(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # fix unwanted gaps between items when scaling, at the cost of performance
        self.setCacheMode(QtWidgets.QGraphicsPixmapItem.CacheMode.ItemCoordinateCache)

    def getWindow(self):
        if self.scene():
            return self.scene().parent().window()

class TilesetItem(PixmapItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlags(QtWidgets.QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable)
        self.pixmaps = [] # depending on tileset offset

class LevelTileItem(PixmapItem):
    def __init__(self, *args, index=0, id=0, screen=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = index
        self.id = id
        self.screen = screen
        self.tileGroup: list[LevelTileItem] = None

    def tileReplace(self, item: QtWidgets.QGraphicsPixmapItem):
        if item == None: return
        #print(f"tile {self.index} of screen {self.screen} = {self.getWindow().gfx_scene_tileset.metaTiles.index(item)}")
        self.setPixmap(item.pixmap())
        self.id = self.getWindow().gfx_scene_tileset.metaTiles.index(item)

class OAMObjectItem(PixmapItem):
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
                rect = self.getWindow().file_content_oam.sceneRect()
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
            self.getWindow().dropdown_oam_obj.setCurrentIndex(self.obj_id)
            self.getWindow().treeCall()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.editable:
            # prevent drag from emitting valueChanged signal, because it affects item position in turn
            self.getWindow().field_objX.blockSignals(True)
            self.getWindow().field_objY.blockSignals(True)
            self.getWindow().field_objX.setValue(self.scenePos().x())
            self.getWindow().field_objY.setValue(self.scenePos().y())
            self.getWindow().field_objX.blockSignals(False)
            self.getWindow().field_objY.blockSignals(False)
            self.getWindow().button_file_save.setEnabled(True)

class GridLayout(QtWidgets.QGridLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._columns = 0 # amount of used columns
        self._rows = 0
    
    def addWidget(self, *args, **kwargs):
        super().addWidget(*args, **kwargs)
        item_pos = self.getItemPosition(self.indexOf(args[0]))
        self._rows = max(self._rows, item_pos[0]+1)
        self._columns = max(self._columns, item_pos[1]+1)
    
    def addItem2(self, *args, **kwargs):
        super().addItem(*args, **kwargs)
        item_pos = self.getItemPosition(self.indexOf(args[0]))
        self._rows = max(self._rows, item_pos[0]+1)
        self._columns = max(self._columns, item_pos[1]+1)
    
    def addLayout(self, *args, **kwargs):
        super().addLayout(*args, **kwargs)
        item_pos = self.getItemPosition(self.indexOf(args[0]))
        self._rows = max(self._rows, item_pos[0]+1)
        self._columns = max(self._columns, item_pos[1]+1)

    def rearrange(self, columns: int, rows: int=-1):
        if columns == self._columns and self._rows == rows: return
        column_index = 0
        row_index = 0
        column_target = 0
        row_target = 0
        #print(self._rows, rows)
        #print(self._columns, columns)
        for item_index in range(self.count()):
            column_index = item_index%self._columns
            row_index = item_index//self._columns
            column_target = item_index%columns
            row_target = item_index//columns
            #print(row_index)
            item = self.itemAtPosition(row_index, column_index)
            item_target = self.itemAtPosition(row_target, column_target)
            #print(item.widget().pos()-self.contentsRect().topLeft())
            if rows != -1 and row_target >= rows:
                item.widget().hide()
            else:
                item.widget().show()
            if item_target == item:
                continue
            else:
                self.removeItem(item)
                self.addItem(item, row_target, column_target)
        self._columns = columns
        self._rows = row_target+1 if rows == -1 else rows

class EditorTree(QtWidgets.QTreeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ContextNameType = "[Filenames]"

    def getMainWindow(self):
        if hasattr(self.window(), "rom"):
            return self.window()
        else:
            return self.window().parent()

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
                self.getMainWindow().exportCall(self.currentItem())
            elif action2 == importAction:
                self.getMainWindow().replaceCall(self.currentItem())
            elif action2 == sdatAction:
                self.getMainWindow().dialog_sdat.show()
                self.getMainWindow().dialog_sdat.setFocus()
    
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
        
    def page_charcount(self):
        return int(int(self.width()/self.fontMetrics().averageCharWidth() - 1)*self.page_linecount()/2)
    
    def page_linecount(self):
        return int(self.height()/self.fontMetrics().lineSpacing() - 1)

    def contextMenuOpen(self): #quick menu to insert special values in dialogue file
        self.context_menu = QtWidgets.QMenu(self)
        self.context_menu.setGeometry(self.cursor().pos().x(), self.cursor().pos().y(), 50, 50)
        for char_index in range(len(lib.dialogue.SPCHARS_E)):
            if char_index >= 0xf0 and not isinstance(lib.dialogue.SPCHARS_E[char_index], int):
                self.context_menu.addAction(f"{lib.datconv.numToStr(char_index, self.window().displayBase, self.window().displayAlphanumeric).zfill(2)} - {lib.dialogue.SPCHARS_E[char_index][1]}")
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