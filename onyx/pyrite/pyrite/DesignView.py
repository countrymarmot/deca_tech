# DesignView.py
# Created by Craig Bishop on 18 July 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

from PySide.QtCore import QRectF, QLineF, QPointF, Qt, Signal
from PySide.QtGui import QGraphicsView, QGraphicsScene, QGraphicsItem,\
  QPen, QBrush, QColor, QPainterPath, QTransform
from ObjectProxy import ObjectProxy
from malachite import Design, Geom, maxTraceWidthForPath, PathSegment,\
    PathArc, distancePointToDesignObject, Point,\
    closestLineSegOnLineSegPathToPoint, distanceDesignObjectToDesignObject
from DVActionSystem import DVWheelZoomActionListener, DVArrowPanActionListener,\
    DVSelectionActionListener, DVMousePanActionListener
import weakref
import math

class DesignView(QGraphicsView):
  selectionChanged = Signal(object)

  def __init__(self, parent):
    QGraphicsView.__init__(self, parent)
    self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
    self.scale(1, -1)
    self.setStyleSheet("background: black;")
    self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    self._design = None
    
    self._persistentActionListeners = []
    self._activeAction = None
    self._selectedDesignObject = None
    self._layerVisibility = None

    # add default action listeners
    self.addPersistentActionListener(DVWheelZoomActionListener())
    self.addPersistentActionListener(DVArrowPanActionListener())
    self.addPersistentActionListener(DVSelectionActionListener())
    self.addPersistentActionListener(DVMousePanActionListener())

  def setDesign(self, design):
    self.cancelActiveAction()
    self.setSelectedDesignObject(None)

    DesignObjectGraphicsItem.clearCaches()
    self._design = design
    curTransform = self.transform()
    scene = QGraphicsScene(-100000, -100000, 200000, 200000)
    self.setScene(scene)

    # create graphics items for the hierarchy
    item = DesignObjectGraphicsItem.graphicsItemForDesignObject(self._design.package)
    scene.addItem(item)
    for die in self._design.package.dies:
      item = DesignObjectGraphicsItem.graphicsItemForDesignObject(die)
      scene.addItem(item)
    for net in self._design.package.nets:
      for branch in net.branches:
        for child in branch.children:
          item = DesignObjectGraphicsItem.graphicsItemForDesignObject(child)
          scene.addItem(item)
    for routeDef in self._design.routeDefinitions:
      item = DesignObjectGraphicsItem.graphicsItemForDesignObject(routeDef)
      scene.addItem(item)

    self.setScene(scene)
    self.setLayerVisibility(self._layerVisibility)
    self.setTransform(curTransform)

  def addPersistentActionListener(self, listener):
    self._persistentActionListeners.append(listener)

  def setActiveAction(self, action):
    if self._activeAction:
      self._activeAction.cancel()
    self._activeAction = action

  def cancelActiveAction(self):
    if self._activeAction:
      self._activeAction.cancel()
      self.repaint()
    self._activeAction = None

  def selectedDesignObject(self):
    return self._selectedDesignObject

  def setSelectedDesignObject(self, dobj):
    if self._selectedDesignObject:
      gfxItem = DesignObjectGraphicsItem.graphicsItemForDesignObject(self._selectedDesignObject)
      gfxItem.setHighlighted(False)
    self._selectedDesignObject = dobj
    if dobj:
      gfxItem = DesignObjectGraphicsItem.graphicsItemForDesignObject(dobj)
      gfxItem.setHighlighted(True)
    self.selectionChanged.emit(self._selectedDesignObject)
    self.repaint()

  def setLayerVisibility(self, layerVis):
    self._layerVisibility = layerVis

    # update visibility of graphics items
    for wdo in DesignObjectGraphicsItem._graphicsItems:
      gfxItem = DesignObjectGraphicsItem._graphicsItems[wdo]
      objType = gfxItem()._designObject.objType
      if objType == "PAD" or objType == "PATH" or objType == "SHAPE":
        gfxItem().setVisible(self.layerIsVisible(gfxItem()._designObject.layer))

    # check visibility of selected item
    if self._selectedDesignObject and self._selectedDesignObject.objType in ['PAD', 'PATH', 'SHAPE']:
      if not self.layerIsVisible(self._selectedDesignObject.layer):
        self.setSelectedDesignObject(None)

    self.repaint()

  def layerIsVisible(self, layer):
    if not self._layerVisibility:
      return True
    else:
      return self._layerVisibility.get(layer.name, True)

  def designObjectUnderPoint(self, pos, ignoreTypes=[]):
    # find design space coordinates
    p = self.mapToScene(pos)

    # go through all the graphics items,
    # if mouse point intersects bounding rect
    # do a more thorough check
    possibleItems = []
    for wdo in DesignObjectGraphicsItem._graphicsItems:
      gfxItem = DesignObjectGraphicsItem._graphicsItems[wdo]
      if gfxItem().boundingRect().contains(p):
        possibleItems.append(gfxItem)

    if len(possibleItems) <= 0:
      return None, None

    mpoint = Point.fromXY(p.x(), p.y())

    def isVisible(do):
      if do.objType in ['PAD', 'PATH', 'SHAPE']:
        return self.layerIsVisible(do.layer)
      else:
        return True
    possibleItems = filter(lambda wk: isVisible(wk()._designObject),
        possibleItems)

    def notIgnored(do):
      return (do.objType not in ignoreTypes)
    possibleItems = filter(lambda wk: notIgnored(wk()._designObject),
        possibleItems)

    def distZero(do):
      d = distancePointToDesignObject(mpoint, do)
      return d <= 0
    possibleItems = filter(lambda wk: distZero(wk()._designObject._obj),
        possibleItems)

    minSize = float("inf")
    selectedItem = None
    for item in possibleItems:
      do = item()._designObject._obj
      s = float("inf")
      if do.objType == "SHAPE" or do.objType == "DIE":
        brect = item().boundingRect()
        s = brect.width() * brect.height()
      elif do.objType == "PATH":
        seg = closestLineSegOnLineSegPathToPoint(do, mpoint)
        s = seg.traceWidth**2
      elif do.objType == "PAD":
        s = do.diameter**2
      elif do.objType == "ROUTEDEFINITION":
        rdef = do
        s = (min(20, rdef.traceWidth))**2
      if s < minSize:
        minSize = s
        selectedItem = item

    do = None
    if selectedItem:
      do = selectedItem()._designObject._obj
      selectedItem = selectedItem()
    return selectedItem, do

  def setZoom(self, zoomFactor):
    transform = QTransform()
    transform.scale(zoomFactor, -1.0 * zoomFactor)
    self.setTransform(transform)

  def zoom(self, zoomFactor, centerOnMouse=False):
    if centerOnMouse:
      self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
    else:
      self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
    self.scale(zoomFactor, zoomFactor)
    self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

  def zoomIn(self):
    self.cancelActiveAction()
    self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
    scaleFactor = 1.5
    self.scale(scaleFactor, scaleFactor)
    self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

  def zoomOut(self):
    self.cancelActiveAction()
    self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
    scaleFactor = 1.0 / 1.5
    self.scale(scaleFactor, scaleFactor)
    self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

  def zoomFitAll(self):
    packageItem = DesignObjectGraphicsItem.graphicsItemForDesignObject(self._design.package)
    self.fitInView(packageItem.boundingRect(), Qt.KeepAspectRatio)

  def focusOutEvent(self, event):
    super(DesignView, self).focusOutEvent(event)
    event.setAccepted(False)
    if self._activeAction:
      if self._activeAction.focusOutEvent(self, self._design, event):
        self.cancelActiveAction()
    for listener in self._persistentActionListeners:
      if event.isAccepted():
        break
      listener.focusOutEvent(self, self._design, event)

  def keyPressEvent(self, event):
    # if escape, cancel the action
    if event.key() == Qt.Key_Escape:
      self.cancelActiveAction()

    event.setAccepted(False)
    if self._activeAction:
      if self._activeAction.keyPressEvent(self, self._design, event):
        self.cancelActiveAction()

    for listener in self._persistentActionListeners:
      if event.isAccepted():
        break
      listener.keyPressEvent(self, self._design, event)

  def keyReleaseEvent(self, event):
    event.setAccepted(False)
    if self._activeAction:
      if self._activeAction.keyReleaseEvent(self, self._design, event):
        self.cancelActiveAction()
    for listener in self._persistentActionListeners:
      if event.isAccepted():
        break
      listener.keyReleaseEvent(self, self._design, event)

  def wheelEvent(self, event):
    event.setAccepted(False)
    if self._activeAction:
      if self._activeAction.wheelEvent(self, self._design, event):
        self.cancelActiveAction()
    for listener in self._persistentActionListeners:
      if event.isAccepted():
        break
      listener.wheelEvent(self, self._design, event)

  def mousePressEvent(self, event):
    super(DesignView, self).mousePressEvent(event)
    event.setAccepted(False)
    if self._activeAction:
      if self._activeAction.mousePressEvent(self, self._design, event):
        self.cancelActiveAction()
    for listener in self._persistentActionListeners:
      if event.isAccepted():
        break
      listener.mousePressEvent(self, self._design, event)

  def mouseReleaseEvent(self, event):
    super(DesignView, self).mouseReleaseEvent(event)
    event.setAccepted(False)
    if self._activeAction:
      if self._activeAction.mouseReleaseEvent(self, self._design, event):
        self.cancelActiveAction()
    for listener in self._persistentActionListeners:
      if event.isAccepted():
        break
      listener.mouseReleaseEvent(self, self._design, event)

  def mouseMoveEvent(self, event):
    super(DesignView, self).mouseMoveEvent(event)
    event.setAccepted(False)
    if self._activeAction:
      if self._activeAction.mouseMoveEvent(self, self._design, event):
        self.cancelActiveAction()
    for listener in self._persistentActionListeners:
      if event.isAccepted():
        break
      listener.mouseMoveEvent(self, self._design, event)

  def leaveEvent(self, event):
    super(DesignView, self).leaveEvent(event)
    event.setAccepted(False)
    if self._activeAction:
      if self._activeAction.mouseLeaveEvent(self, self._design, event):
        self.cancelActiveAction()
    for listener in self._persistentActionListeners:
      if event.isAccepted():
        break
      listener.mouseLeaveEvent(self, self._design, event)

  def paintEvent(self, event):
    super(DesignView, self).paintEvent(event)
    for listener in self._persistentActionListeners:
      listener.paintEvent(self, self._design, event)
    if self._activeAction:
      self._activeAction.paintEvent(self, self._design, event)


class DesignObjectGraphicsItem(QGraphicsItem):
  _graphicsItems = {}
  _factoryTypes = {}

  @classmethod
  def clearCaches(cls):
    for wkr in cls._graphicsItems.values():
      wkr().unObserve()
    cls._graphicsItems = {}

  @classmethod
  def graphicsItemForDesignObject(cls, dobj):
    wkr = weakref.ref(dobj)
    if wkr in cls._graphicsItems:
      return cls._graphicsItems[wkr]()
    else:
      gItem = cls._factoryTypes.get(dobj.objType,
          DesignObjectGraphicsItem)(dobj)
      cls._graphicsItems[wkr] = weakref.ref(gItem)
      return gItem

  def __init__(self, designObj):
    QGraphicsItem.__init__(self)
    self.setPos(QPointF(0, 0))
    self._designObject = ObjectProxy.proxyForObject(designObj)
    self._highlighted = False
    self._visible = True

  def highlighted(self):
    return self._highlighted

  def setHighlighted(self, highlight):
    self._highlighted = highlight

  def visible(self):
    return self._visible

  def setVisible(self, vis):
    self._visible = vis

  def boundingRect(self):
    return QRectF()

  def paint(self, painter, option, widget):
    pass

  def unObserve(self):
    pass

  def __del__(self):
    wkr = weakref.ref(self._designObject._obj)
    if wkr in self._graphicsItems:
      del(self._graphicsItems[wkr])


class PackageGraphicsItem(DesignObjectGraphicsItem):
  def __init__(self, package):
    DesignObjectGraphicsItem.__init__(self, package)
    self._package = self._designObject
    self._package.addObserver(self.packageSizeOrPosChanged)

  def boundingRect(self):
    return QRectF(self._package.center.x - (self._package.width / 2) - 1,
        self._package.center.y - (self._package.height / 2)- 1,
        self._package.width + 2, self._package.height + 2)

  def paint(self, painter, option, widget):
    painter.setPen(QPen(QBrush(QColor(0, 255, 255)), 2.0))
    rect = QRectF(self._package.center.x - (self._package.width / 2),
        self._package.center.y - (self._package.height / 2),
        self._package.width, self._package.height)
    painter.drawRect(rect)

  def packageSizeOrPosChanged(self, obj, attr):
    rect = QRectF(self._package.center.x - (self._package.width / 2) - 1,
        self._package.center.y - (self._package.height / 2)- 1,
        self._package.width + 2, self._package.height + 2)
    self.update(rect)

  def unObserve(self):
    self._package.removeObserver(self.packageSizeOrPosChanged)

DesignObjectGraphicsItem._factoryTypes['PACKAGE'] = PackageGraphicsItem


class DieGraphicsItem(DesignObjectGraphicsItem):
  def __init__(self, die):
    DesignObjectGraphicsItem.__init__(self, die)
    self._die = self._designObject

  def boundingRect(self):
    return QRectF(self._die.center.x - (self._die.width / 2) - 1,
        self._die.center.y - (self._die.height / 2)- 1,
        self._die.width + 2, self._die.height + 2)

  def paint(self, painter, option, widget):
    if self.highlighted():
      painter.setPen(QPen(QBrush(QColor(0, 255, 0)), 4.0))
    else:
      painter.setPen(QPen(QBrush(QColor(255, 0, 255)), 2.0))
    rect = QRectF(self._die.center.x - (self._die.width / 2),
        self._die.center.y - (self._die.height / 2),
        self._die.width, self._die.height)
    painter.drawRect(rect)

DesignObjectGraphicsItem._factoryTypes['DIE'] = DieGraphicsItem


class PadGraphicsItem(DesignObjectGraphicsItem):
  def __init__(self, pad):
    DesignObjectGraphicsItem.__init__(self, pad)
    self._pad = self._designObject._obj
    c = self._pad.branch.net.netColor()
    self._qcolor = QColor(c[0], c[1], c[2])
    self._boundingBox = self.computeBounds()
    self._drawBox = self.computeDrawBox()
    self._designObject.addObserver(self.designObjectChanged)

  def computeBounds(self):
    return QRectF(self._pad.center.x - (self._pad.diameter / 2) - 1,
        self._pad.center.y - (self._pad.diameter / 2) - 1,
        self._pad.diameter + 2, self._pad.diameter + 2)

  def computeDrawBox(self):
    return QRectF(self._pad.center.x - (self._pad.diameter / 2),
        self._pad.center.y - (self._pad.diameter / 2),
        self._pad.diameter, self._pad.diameter)

  def boundingRect(self):
    return self._boundingBox

  def unObserve(self):
    self._designObject.removeObserver(self.designObjectChanged)

  def designObjectChanged(self, obj, attr):
    c = self._pad.branch.net.netColor()
    self._qcolor = QColor(c[0], c[1], c[2])
    self._boundingBox = self.computeBounds()
    self._drawBox = self.computeDrawBox()
    self.update(self.boundingRect())

  def paint(self, painter, option, widget):
    if not self._visible:
      return
    if self.highlighted():
      c = QColor(0, 255, 0)
      painter.setPen(QPen(QBrush(c), 4.0))
    else:
      c = self._qcolor
      painter.setPen(QPen(QBrush(c), 2.0))
    painter.drawEllipse(self._drawBox)

DesignObjectGraphicsItem._factoryTypes['PAD'] = PadGraphicsItem


class PathGraphicsItem(DesignObjectGraphicsItem):
  def __init__(self, path):
    DesignObjectGraphicsItem.__init__(self, path)
    self._path = self._designObject._obj
    c = self._path.branch.net.netColor()
    self._qcolor = QColor(c[0], c[1], c[2])
    self._boundingBox = self.computeBounds()
    self._cached = self.computeQLines()
    self._designObject.addObserver(self.designObjectChanged)

  def computeBounds(self):
    bBox = Geom.boundingBoxForSegments(self._path.segments)
    maxW = maxTraceWidthForPath(self._path)
    return QRectF(bBox.p1.x - maxW, bBox.p1.y - maxW,
        bBox.width() + (2 * maxW), bBox.height() + (2 * maxW))

  def computeQLines(self):
    lines = []
    widths = []
    
    for seg in self._path.segments:
      if isinstance(seg, PathSegment):
        lines.append(QLineF(seg.p1.x, seg.p1.y, seg.p2.x, seg.p2.y))
        widths.append(seg.traceWidth)
      elif isinstance(seg._obj, PathArc):
        theta = seg.startAngle()
        endTheta = seg.endAngle()

        if seg.cw:
          while endTheta >= theta:
            endTheta -= 360
        else:
          while endTheta <= theta:
            endTheta += 360

        r = seg.radius()
        sweep = abs(endTheta - theta)
        L = math.radians(sweep) * r
        steps = max(5, int(L) / 5)
        step = sweep / float(steps)
        if seg.cw:
          step *= -1.0
        lastPos = seg.p1
        for i in range(steps):
          p = seg.center.add(Geom.Point.fromXY(math.cos(math.radians(theta)) * r,
            math.sin(math.radians(theta)) * r))
          lines.append(QLineF(lastPos.x, lastPos.y, p.x, p.y))
          widths.append(seg.traceWidth)
          lastPos = p
          theta += step
    return zip(lines, widths)

  def boundingRect(self):
    return self._boundingBox

  def unObserve(self):
    self._designObject.removeObserver(self.designObjectChanged)

  def designObjectChanged(self, obj, attr):
    c = self._path.branch.net.netColor()
    self._qcolor = QColor(c[0], c[1], c[2])
    self._boundingBox = self.computeBounds()
    self._cached = self.computeQLines()
    self.update(self.boundingRect())

  def paint(self, painter, option, widget):
    if not self._visible:
      return
    c = self._qcolor
    if self.highlighted():
      c = QColor(0, 255, 0)
    pen = QPen(c)
    pen.setCapStyle(Qt.RoundCap)
    for line, width in self._cached:
      pen.setWidthF(width)
      painter.setPen(pen)
      painter.drawLine(line)

DesignObjectGraphicsItem._factoryTypes['PATH'] = PathGraphicsItem


class ShapeGraphicsItem(DesignObjectGraphicsItem):
  def __init__(self, shape):
    DesignObjectGraphicsItem.__init__(self, shape)
    self._shape = self._designObject._obj
    c = self._shape.branch.net.netColor()
    self._qcolor = QColor(c[0], c[1], c[2])
    self._boundingBox = self.computeBounds()
    self._painterPath = self.computePainterPath()
    self._designObject.addObserver(self.designObjectChanged)

  def computeBounds(self):
    bBox = Geom.boundingBoxForSegments(self._shape.segments)
    return QRectF(bBox.p1.x, bBox.p1.y, bBox.width(), bBox.height())

  def computePainterPath(self):
    seg0 = self._shape.segments[0]
    path = QPainterPath(QPointF(seg0.p1.x, seg0.p1.y))
    for seg in self._shape.segments:
      if isinstance(seg, Geom.LineSeg):
        path.lineTo(seg.p2.x, seg.p2.y)
      elif isinstance(seg, Geom.Arc):
        theta = seg.startAngle()
        endTheta = seg.endAngle()

        if seg.cw:
          while endTheta >= theta:
            endTheta -= 360
        else:
          while endTheta <= theta:
            endTheta += 360

        r = seg.radius()
        sweep = abs(endTheta - theta)
        L = math.radians(sweep) * r
        steps = max(5, int(L) / 5)
        step = sweep / float(steps)
        if seg.cw:
          step *= -1.0

        for i in range(steps):
          p = seg.center.add(Geom.Point.fromXY(math.cos(math.radians(theta)) * r,
            math.sin(math.radians(theta)) * r))
          path.lineTo(p.x, p.y)
          theta += step
    return path

  def boundingRect(self):
    return self._boundingBox

  def unObserve(self):
    self._designObject.removeObserver(self.designObjectChanged)

  def designObjectChanged(self, obj, attr):
    c = self._shape.branch.net.netColor()
    self._qcolor = QColor(c[0], c[1], c[2])
    self._boundingBox = self.computeBounds()
    self._painterPath = self.computePainterPath()
    self.update(self.boundingRect())

  def paint(self, painter, option, widget):
    if not self._visible:
      return
    if self.highlighted():
      c = QColor(0, 255, 0)
      pen = QPen(QBrush(c), 4.0)
    else:
      c = self._qcolor
      pen = QPen(QBrush(c), 2.0)
    painter.setPen(pen)
    painter.strokePath(self._painterPath, pen)

DesignObjectGraphicsItem._factoryTypes['SHAPE'] = ShapeGraphicsItem

class RouteDefinitionGraphicsItem(DesignObjectGraphicsItem):
  def __init__(self, routeDef):
    DesignObjectGraphicsItem.__init__(self, routeDef)
    self._routeDef = self._designObject
    c = self._routeDef.designObject1.branch.net.netColor()
    self._qcolor = QColor(c[0], c[1], c[2])
    self._endPoints = self._routeDef.endPoints()
    self._boundingBox = self.computeBounds()
    self._line = self.computeLine()

  def computeBounds(self):
    seg = Geom.LineSeg()
    seg.p1 = self._endPoints[0]
    seg.p2 = self._endPoints[1]
    bBox = Geom.boundingBoxForSegments([seg])
    rect = QRectF(bBox.p1.x, bBox.p1.y, bBox.width(), bBox.height())
    tw = self._routeDef.traceWidth
    if rect.width() < tw:
      rect.setLeft(rect.left() - (tw / 2))
      rect.setWidth(tw)
    if rect.height() < tw:
      rect.setTop(rect.top() - (tw / 2))
      rect.setHeight(tw)
    return rect

  def boundingRect(self):
    return self._boundingBox

  def computeLine(self):
    p1 = self._endPoints[0]
    p2 = self._endPoints[1]
    return QLineF(p1.x, p1.y, p2.x, p2.y)

  def paint(self, painter, option, widget):
    c = self._qcolor
    if self.highlighted():
      c = QColor(0, 255, 0)
    painter.setPen(QPen(QBrush(c), 2.0, Qt.DashLine))
    painter.drawLine(self._line)

DesignObjectGraphicsItem._factoryTypes['ROUTEDEFINITION'] = RouteDefinitionGraphicsItem

