from PyQt4 import QtCore, QtGui, uic
import math

class CodeUIEdgeItem(QtGui.QGraphicsItem):
	def __init__(self, srcUniqueName, tarUniqueName, dbRef = None, parent = None, scene = None):
		super(CodeUIEdgeItem, self).__init__(parent, scene)
		#self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
		self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
		self.setAcceptHoverEvents(True)
		#self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable)
		self.srcUniqueName = srcUniqueName
		self.tarUniqueName = tarUniqueName
		self.setZValue(-1)
		self.path = None
		self.pathShape = None
		self.pathPnt = None
		self.buildPath()

		self.file = ''
		self.line = -1
		self.column = -1
		if dbRef:
			self.file = dbRef.file().longname()
			self.line = dbRef.line()
			self.column = dbRef.column()

		self.isHover = False

	def getNodePos(self):
		from UIManager import UIManager
		scene = UIManager.instance().getScene()
		srcNode = scene.getNode(self.srcUniqueName)
		tarNode = scene.getNode(self.tarUniqueName)
		if not srcNode or not tarNode:
			return QtCore.QPointF(), QtCore.QPointF()
		srcPos = srcNode.pos()
		tarPos = tarNode.pos()
		sign = 1 if tarPos.x() > srcPos.x() else -1
		sr = srcNode.getRadius()
		tr = tarNode.getRadius()
		return srcPos + QtCore.QPointF(sr*sign,0), tarPos - QtCore.QPointF(tr*sign, 0)

	def getMiddlePos(self):
		from UIManager import UIManager
		scene = UIManager.instance().getScene()
		srcNode = scene.getNode(self.srcUniqueName)
		tarNode = scene.getNode(self.tarUniqueName)
		if not srcNode or not tarNode:
			return QtCore.QPointF()
		return (srcNode.pos() + tarNode.pos()) * 0.5

	def boundingRect(self):
		srcPos, tarPos = self.getNodePos()
		#print(srcPos, tarPos)
		minPnt = (min(srcPos.x(), tarPos.x()), min(srcPos.y(), tarPos.y()))
		maxPnt = (max(srcPos.x(), tarPos.x()), max(srcPos.y(), tarPos.y()))

		return QtCore.QRectF(minPnt[0], minPnt[1], maxPnt[0]-minPnt[0], maxPnt[1]- minPnt[1])

	def buildPath(self):
		srcPos, tarPos = self.getNodePos()
		if self.pathPnt and (self.pathPnt[0]-srcPos).manhattanLength() < 0.05 and (self.pathPnt[1]-tarPos).manhattanLength() < 0.05:
			return self.path
		#print('build path', self.pathPnt, srcPos, tarPos)
		self.pathPnt = (srcPos, tarPos)
		path = QtGui.QPainterPath()
		path.moveTo(srcPos)
		dx = tarPos.x() - srcPos.x()
		p1 = srcPos + QtCore.QPointF(dx*0.5, 0)
		p2 = tarPos + QtCore.QPointF(-dx*0.7, 0)
		path.cubicTo(p1,p2,tarPos)
		self.path = path

		from PyQt4.QtGui import QPainterPathStroker
		stroker = QPainterPathStroker()
		stroker.setWidth(10.0)
		self.pathShape = stroker.createStroke(self.path)
		return path

	def shape(self):
		#srcPos, tarPos = self.getNodePos()
		#path = QtGui.QPainterPath()
		# path.moveTo(srcPos)
		# path.lineTo(tarPos)
		#path.addRect(self.boundingRect())
		#return path
		return self.pathShape

	def paint(self, painter, styleOptionGraphicsItem, widget_widget=None):
		painter.setRenderHint(QtGui.QPainter.Antialiasing)
		clr = QtCore.Qt.darkGray if self.isSelected() else QtCore.Qt.lightGray

		if self.isSelected() or self.isHover:
			clr = QtGui.QColor(255,127,39)
		else:
			clr = QtGui.QColor(180,180,180)
		painter.setPen(QtGui.QPen(clr, 2.0))

		srcPos, tarPos = self.getNodePos()
		#midPos = (srcPos + tarPos) * 0.5
		midPos = tarPos
		#d = [tarPos.x() - srcPos.x(), tarPos.y() - srcPos.y()]
		d = [tarPos.x() - srcPos.x(), 0]
		dirLength = math.sqrt(d[0]*d[0] + d[1]*d[1])
		d[0] /= (dirLength + 1e-5)
		d[1] /= (dirLength + 1e-5)

		ld = (-d[1],d[0])
		back = -10
		side = 4
		leftPos  = QtCore.QPointF(midPos.x() + d[0]*back + ld[0]*side, midPos.y() + d[1]*back + ld[1]*side)
		rightPos = QtCore.QPointF(midPos.x() + d[0]*back + ld[0]*-side, midPos.y() + d[1]*back + ld[1]*-side)

		#painter.drawLines([srcPos, tarPos, leftPos, midPos, rightPos, midPos])
		painter.drawLines([leftPos, midPos, rightPos, midPos])
		painter.drawPath(self.path)

	def hoverLeaveEvent(self, QGraphicsSceneHoverEvent):
		super(CodeUIEdgeItem, self).hoverLeaveEvent(QGraphicsSceneHoverEvent)
		self.isHover = False

	def hoverEnterEvent(self, QGraphicsSceneHoverEvent):
		super(CodeUIEdgeItem, self).hoverEnterEvent(QGraphicsSceneHoverEvent)
		self.isHover = True

	def mouseDoubleClickEvent(self, event):
		super(CodeUIEdgeItem, self).mouseDoubleClickEvent(event)

		from UIManager import UIManager
		scene = UIManager.instance().getScene()
		if scene:
			scene.showInEditor()