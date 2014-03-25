# DVActionSystem.py
# Created by Craig Bishop on 22 October 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

from PySide.QtCore import Qt, QPoint, QRect, QRectF
from PySide.QtGui import QPainter, QPen, QBrush, QColor
import DesignView
from malachite import Net, createShortestRouteDefinition
from Command import Command
from ObjectProxy import ObjectProxy


class DVActionListener:
  def cancel(self):
    pass

  def focusOutEvent(self, designView, design, event):
    event.ignore()
    return False

  def keyPressEvent(self, designView, design, event):
    event.ignore()
    return False

  def keyReleaseEvent(self, designView, design, event):
    event.ignore()
    return False

  def wheelEvent(self, designView, design, event):
    event.ignore()
    return False

  def mousePressEvent(self, designView, design, event):
    event.ignore()
    return False

  def mouseReleaseEvent(self, designView, design, event):
    event.ignore()
    return False

  def mouseMoveEvent(self, designView, design, event):
    event.ignore()
    return False

  def mouseLeaveEvent(self, designView, design, event):
    event.ignore()
    return False

  def paintEvent(self, designView, design, event):
    event.ignore()


class DVWheelZoomActionListener(DVActionListener):
  _wheelScaleFactor = 1.15

  def wheelEvent(self, designView, design, event):
    if (event.orientation() == Qt.Horizontal):
      event.accept()
      return False
    else:
      if event.delta() > 0:
        designView.zoom(self._wheelScaleFactor, True)
      else:
        designView.zoom(1.0 / self._wheelScaleFactor, True)
      event.accept()
    return False


class DVArrowPanActionListener(DVActionListener):
  _arrowPanDistance = 100

  def keyPressEvent(self, designView, design, event):
    # pan by 1/10 of screen
    p1 = designView.mapToScene(0, 0)
    p2 = designView.mapToScene(designView.width(), 0)
    step = 0.1 * (p2.x() - p1.x())

    center = designView.mapToScene(designView.rect().center())

    if event.key() == Qt.Key_Up:
      event.accept()
      center.setY(center.y() + step)
      designView.centerOn(center)
    elif event.key() == Qt.Key_Down:
      event.accept()
      center.setY(center.y() - step)
      designView.centerOn(center)
    elif event.key() == Qt.Key_Left:
      event.accept()
      center.setX(center.x() - step)
      designView.centerOn(center)
    elif event.key() == Qt.Key_Right:
      event.accept()
      center.setX(center.x() + step)
      designView.centerOn(center)

    return False


class DVMousePanActionListener(DVActionListener):
  def __init__(self):
    self._lastPoint = QPoint(0, 0)
    self._panning = False

  def mousePressEvent(self, designView, design, event):
    if event.button() in [Qt.RightButton, Qt.MiddleButton]:
      event.accept()
      designView.setCursor(Qt.ClosedHandCursor)
      self._panning = True
      self._lastPoint = event.pos()
    return False

  def mouseMoveEvent(self, designView, design, event):
    if self._panning:
      event.accept()
      delta = event.pos() - self._lastPoint
      newCenter = designView.rect().center() - delta
      designView.centerOn(designView.mapToScene(newCenter))
      self._lastPoint = event.pos()
    return False

  def mouseReleaseEvent(self, designView, design, event):
    if self._panning:
      event.accept()
      self._panning = False
      designView.setCursor(Qt.ArrowCursor)
    return False


class DVSelectionActionListener(DVActionListener):
  def mouseReleaseEvent(self, designView, design, event):
    if event.button() == Qt.LeftButton:
      event.accept()
      gfxItem, do = designView.designObjectUnderPoint(event.pos())
      designView.setSelectedDesignObject(do)
    return False


class DVZoomAreaAction(DVActionListener):
  def __init__(self, qaction, designView):
    self._designView = designView
    self._qaction = qaction
    self._qaction.setChecked(True)
    self._down = False
    self._p1 = QPoint(0, 0)
    self._p2 = QPoint(0, 0)
    self._designView.setCursor(Qt.CrossCursor)

  def cancel(self):
    self._qaction.setChecked(False)
    self._designView.setCursor(Qt.ArrowCursor)
    self._designView._activeAction = None

  def mousePressEvent(self, designView, design, event):
    event.accept()
    self._p1 = event.pos()
    self._p2 = event.pos()
    self._down = True
    designView.repaint()
    return False

  def mouseReleaseEvent(self, designView, design, event):
    event.accept()

    # get rectangle to zoom to
    p1 = designView.mapToScene(self._p1)
    p2 = designView.mapToScene(self._p2)
    designView.fitInView(QRectF(p1, p2), Qt.KeepAspectRatio)
    return True

  def mouseMoveEvent(self, designView, design, event):
    event.accept()
    self._p2 = event.pos()
    designView.repaint()
    return False

  def paintEvent(self, designView, design, event):
    if self._down:
      painter = QPainter(designView.viewport())
      painter.setPen(QPen(QBrush(QColor(0, 255, 0)), 1.0))
      painter.drawRect(QRect(self._p1, self._p2))


class DVChangeNetAction(DVActionListener):
  def __init__(self, qaction, designView, project):
    self._designView = designView
    self._project = project
    self._qaction = qaction
    self._qaction.setChecked(True)
    self._selectedFirst = False
    self._do1 = None
    self._designView.setCursor(Qt.PointingHandCursor)

  def cancel(self):
    if self._do1:
      setBranchHighlighted(self._do1.branch, False)
    self._qaction.setChecked(False)
    self._designView.setCursor(Qt.ArrowCursor)
    self._designView._activeAction = None
    self._designView.repaint()

  def mouseReleaseEvent(self, designView, design, event):
    event.accept()
    if not self._selectedFirst:
      gfxItem, do = designView.designObjectUnderPoint(event.pos())
      if do:
        if do.objType not in ['PAD', 'PATH', 'SHAPE']:
          return False
        self._selectedFirst = True
        self._do1 = do
        setBranchHighlighted(do.branch, True)
        self._designView.repaint()
        event.accept()
    else:
      gfxItem, do2 = designView.designObjectUnderPoint(event.pos())
      if do2:
        if do2.objType not in ['PAD', 'PATH', 'SHAPE']:
          return False
        # perform net change
        # if same branch, make new net
        if self._do1.branch != do2.branch:
          cmd = ChangeNetCommand(self._project, self._do1.branch,
              self._do1.branch.net, do2.branch.net)
          self._project.commandHistory.do(cmd)
        else:
          cmd = ChangeNetCommand(self._project, self._do1.branch,
              self._do1.branch.net, None)
          self._project.commandHistory.do(cmd)
        return True
        event.accept()

    return False


def setBranchHighlighted(branch, highlight):
  for do in branch.children:
    gfxItem = DesignView.DesignObjectGraphicsItem.\
        graphicsItemForDesignObject(do)
    gfxItem.setHighlighted(highlight)


class ChangeNetCommand(Command):
  def __init__(self, project, branch, oldNet, newNet):
    self._project = project
    self._branch = branch
    self._oldNet = oldNet
    self._newNet = newNet
    self._createNewNet = (newNet is None)

  def do(self):
    if self._createNewNet:
      self._newNet = Net()
      self._project.design.package.nets.append(self._newNet)

    self._branch.net = self._newNet
    self._project.setDirty()
    # notify all children so they update
    for do in self._branch.children:
      proxy = ObjectProxy.proxyForObject(do)
      proxy.notifyObservers(do, "branch.net")

  def undo(self):
    self._branch.net = self._oldNet
    if self._createNewNet:
      self._project.design.package.nets.remove(self._newNet)
      self._newNet = None

    self._project.setDirty()
    # notify all children so they update
    for do in self._branch.children:
      proxy = ObjectProxy.proxyForObject(do)
      proxy.notifyObservers(do, "branch.net")

  def __str__(self):
    return u"Change net on branch"


class DVDefineRouteAction(DVActionListener):
  def __init__(self, qaction, designView, project):
    self._designView = designView
    self._project = project
    self._qaction = qaction
    self._qaction.setChecked(True)
    self._selectedFirst = False
    self._branch1 = None
    self._layer1 = None
    self._designView.setCursor(Qt.PointingHandCursor)

  def cancel(self):
    if self._branch1:
      setBranchHighlighted(self._branch1, False)
    self._qaction.setChecked(False)
    self._designView.setCursor(Qt.ArrowCursor)
    self._designView._activeAction = None
    self._designView.repaint()

  def next(self):
    self._qaction.setChecked(True)
    self._selectedFirst = False
    self._branch1 = None
    self._layer1 = None
    self._designView.setCursor(Qt.PointingHandCursor)
    if self._branch1:
      setBranchHighlighted(self._branch1, False)
    self._designView.repaint()

  def mouseReleaseEvent(self, designView, design, event):
    ignoreTypes = ["PACKAGE", "DIE", "ROUTEDEFINITION"]
    event.ignore()
    if not self._selectedFirst:
      gfxItem, do = designView.designObjectUnderPoint(event.pos(), ignoreTypes)
      if do:
        if do.objType not in ['PAD', 'PATH', 'SHAPE']:
          return False
        self._selectedFirst = True
        self._branch1 = do.branch
        self._layer1 = do.layer
        setBranchHighlighted(self._branch1, True)
        self._designView.repaint()
        event.accept()
    else:
      gfxItem, do2 = designView.designObjectUnderPoint(event.pos(),
          ignoreTypes)
      # first check that the second branch is different and not the same net
      if do2:
        if do2.objType not in ["PAD", "PATH", "SHAPE"]:
          return False
        branch2 = do2.branch
        if branch2 == self._branch1 or branch2.net != self._branch1.net or\
            len(self._branch1.children) == 0 or len(branch2.children) == 0 or\
                self._layer1 != do2.layer:
          return False
        else:
          # perform route definition
          cmd = DefineRouteCommand(self._project, self._branch1, branch2)
          self._project.commandHistory.do(cmd)
          event.accept()

          self.next()
          return False

    return False


class DefineRouteCommand(Command):
  def __init__(self, project, branch1, branch2):
    self._project = project
    self._design = project.design
    self._branch1 = branch1
    self._branch2 = branch2
    self._routeDef = None

  def do(self):
    self._routeDef = createShortestRouteDefinition(self._branch1,
        self._branch2)
    self._design.routeDefinitions.append(self._routeDef)
    self._project.setDirty()
    self._project.notifications.designHierarchyChanged.emit()

  def undo(self):
    if self._routeDef:
      self._design.routeDefinitions.remove(self._routeDef)
    self._project.setDirty()
    self._project.notifications.designHierarchyChanged.emit()

  def __str__(self):
    return u"Define route"


class DeleteRouteCommand(Command):
  def __init__(self, project, routeDef):
    self._project = project
    self._design = project.design
    self._routeDef = routeDef

  def do(self):
    self._design.routeDefinitions.remove(self._routeDef)
    self._project.setDirty()
    self._project.notifications.designHierarchyChanged.emit()

  def undo(self):
    if self._routeDef:
      self._design.routeDefinitions.append(self._routeDef)
    self._project.setDirty()
    self._project.notifications.designHierarchyChanged.emit()

  def __str__(self):
    return u"Delete route"
