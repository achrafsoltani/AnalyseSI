from PySide6.QtWidgets import (
    QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem,
    QGraphicsLineItem, QGraphicsTextItem, QGraphicsPathItem,
    QStyleOptionGraphicsItem, QWidget
)
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPainterPath
)

from ..models.entity import Entity
from ..models.association import Association
from ..models.link import Link
from ..utils.constants import (
    ENTITY_WIDTH, ENTITY_HEIGHT, ENTITY_COLOR, ENTITY_BORDER,
    ASSOCIATION_WIDTH, ASSOCIATION_HEIGHT, ASSOCIATION_COLOR, ASSOCIATION_BORDER,
    LINK_COLOR, SELECTED_COLOR
)


class EntityItem(QGraphicsItem):
    """Graphical representation of an MCD entity."""

    def __init__(self, entity: Entity, parent=None):
        super().__init__(parent)
        self.entity = entity
        self.setPos(entity.x, entity.y)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCursor(Qt.OpenHandCursor)
        self._width = ENTITY_WIDTH
        self._height = ENTITY_HEIGHT
        self._links: list["LinkItem"] = []

    def boundingRect(self) -> QRectF:
        return QRectF(-self._width / 2, -self._height / 2, self._width, self._height)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        # Draw rounded rectangle
        rect = self.boundingRect()
        path = QPainterPath()
        path.addRoundedRect(rect, 10, 10)

        # Fill
        if self.isSelected():
            painter.setBrush(QBrush(QColor(SELECTED_COLOR).lighter(150)))
            painter.setPen(QPen(QColor(SELECTED_COLOR), 2))
        else:
            painter.setBrush(QBrush(QColor(ENTITY_COLOR)))
            painter.setPen(QPen(QColor(ENTITY_BORDER), 2))

        painter.drawPath(path)

        # Draw entity name
        painter.setPen(Qt.black)
        font = QFont()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, self.entity.name)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Update entity coordinates
            pos = self.pos()
            self.entity.x = pos.x()
            self.entity.y = pos.y()
            # Update connected links
            for link_item in self._links:
                link_item.update_position()
        return super().itemChange(change, value)

    def add_link(self, link_item: "LinkItem"):
        """Register a link item connected to this entity."""
        if link_item not in self._links:
            self._links.append(link_item)

    def remove_link(self, link_item: "LinkItem"):
        """Unregister a link item."""
        if link_item in self._links:
            self._links.remove(link_item)

    def get_center(self) -> QPointF:
        """Get the center point in scene coordinates."""
        return self.scenePos()


class AssociationItem(QGraphicsItem):
    """Graphical representation of an MCD association (rounded octagon/diamond shape)."""

    def __init__(self, association: Association, parent=None):
        super().__init__(parent)
        self.association = association
        self.setPos(association.x, association.y)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCursor(Qt.OpenHandCursor)
        self._width = ASSOCIATION_WIDTH
        self._height = ASSOCIATION_HEIGHT
        self._links: list["LinkItem"] = []

    def boundingRect(self) -> QRectF:
        return QRectF(-self._width / 2, -self._height / 2, self._width, self._height)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        # Create rounded diamond/octagon shape
        rect = self.boundingRect()
        path = QPainterPath()

        # Create a rounded diamond shape
        cx, cy = 0, 0
        w, h = self._width / 2, self._height / 2
        corner = 15  # Corner rounding

        path.moveTo(cx - w + corner, cy)
        path.lineTo(cx, cy - h + corner)
        path.lineTo(cx + w - corner, cy)
        path.lineTo(cx, cy + h - corner)
        path.closeSubpath()

        # Fill
        if self.isSelected():
            painter.setBrush(QBrush(QColor(SELECTED_COLOR).lighter(150)))
            painter.setPen(QPen(QColor(SELECTED_COLOR), 2))
        else:
            painter.setBrush(QBrush(QColor(ASSOCIATION_COLOR)))
            painter.setPen(QPen(QColor(ASSOCIATION_BORDER), 2))

        painter.drawPath(path)

        # Draw association name
        painter.setPen(Qt.black)
        font = QFont()
        font.setItalic(True)
        painter.setFont(font)
        text_rect = QRectF(-self._width / 2 + 5, -15, self._width - 10, 30)
        painter.drawText(text_rect, Qt.AlignCenter, self.association.name)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Update association coordinates
            pos = self.pos()
            self.association.x = pos.x()
            self.association.y = pos.y()
            # Update connected links
            for link_item in self._links:
                link_item.update_position()
        return super().itemChange(change, value)

    def add_link(self, link_item: "LinkItem"):
        """Register a link item connected to this association."""
        if link_item not in self._links:
            self._links.append(link_item)

    def remove_link(self, link_item: "LinkItem"):
        """Unregister a link item."""
        if link_item in self._links:
            self._links.remove(link_item)

    def get_center(self) -> QPointF:
        """Get the center point in scene coordinates."""
        return self.scenePos()


class LinkItem(QGraphicsLineItem):
    """Graphical representation of a link between entity and association."""

    def __init__(
        self,
        link: Link,
        entity_item: EntityItem,
        association_item: AssociationItem,
        parent=None
    ):
        super().__init__(parent)
        self.link = link
        self.entity_item = entity_item
        self.association_item = association_item

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setPen(QPen(QColor(LINK_COLOR), 2))

        # Create cardinality label
        self._card_label = QGraphicsTextItem(self)
        font = QFont()
        font.setBold(True)
        self._card_label.setFont(font)

        # Register with connected items
        entity_item.add_link(self)
        association_item.add_link(self)

        self.update_position()

    def update_position(self):
        """Update line position based on connected items."""
        p1 = self.entity_item.get_center()
        p2 = self.association_item.get_center()
        self.setLine(p1.x(), p1.y(), p2.x(), p2.y())

        # Position cardinality label near entity
        mid_x = (p1.x() + p2.x()) / 2
        mid_y = (p1.y() + p2.y()) / 2
        # Place label closer to entity side
        label_x = p1.x() + (mid_x - p1.x()) * 0.3
        label_y = p1.y() + (mid_y - p1.y()) * 0.3 - 15

        self._card_label.setPlainText(f"({self.link.cardinality})")
        self._card_label.setPos(label_x, label_y)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        if self.isSelected():
            self.setPen(QPen(QColor(SELECTED_COLOR), 3))
        else:
            self.setPen(QPen(QColor(LINK_COLOR), 2))
        super().paint(painter, option, widget)

    def cleanup(self):
        """Remove this link from connected items."""
        self.entity_item.remove_link(self)
        self.association_item.remove_link(self)
