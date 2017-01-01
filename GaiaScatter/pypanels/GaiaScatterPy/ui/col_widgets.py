import hou
import sys
import os
import tempfile

from PySide import QtGui
from PySide import QtCore
import toolutils

from ..icons.icon import get_icon
from GaiaCommon import nodeInfos

from . import widgets
reload(widgets)

class CollectionInstanceWidget(QtGui.QWidget):
    """ Widget used in the layer widget, when object are dropped from the collection
        to the scatter tool.
    """
    def __init__(self, node=None, idx=0, parent=None):
        super(CollectionInstanceWidget, self).__init__(parent=parent)

        self.idx = idx
        self.node = node
        self.path = self.node.evalParm("path_" + str(idx))
        self.influence = self.node.evalParm("influence_" + str(idx))
        self.thumbnail_binary = None
        with open("D:/test.jpg", 'rb') as f:
            self.thumbnail_binary = f.read()

        # states
        self.displayed = True
        self.display_mode = 0

        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)

        self.btn_layout = QtGui.QHBoxLayout()
        self.btn_layout.setContentsMargins(0,0,0,0)
        self.btn_layout.setSpacing(1)

        self.show_toggle_btn = QtGui.QPushButton("")
        self.show_toggle_btn.setToolTip("Hide / Show object")
        self.show_toggle_btn.setIcon(get_icon("eye_open", 24))
        self.show_toggle_btn.setFixedWidth(22)
        self.show_toggle_btn.setFixedHeight(22)
        self.show_toggle_btn.setFlat(True)
        self.show_toggle_btn.clicked.connect(self.show_object)
        self.btn_layout.addWidget(self.show_toggle_btn)

        self.display_mode_btn = QtGui.QPushButton("")
        self.display_mode_btn.setIcon(get_icon("tree", 24))
        self.display_mode_btn.setFixedWidth(22)
        self.display_mode_btn.setFixedHeight(22)
        self.display_mode_btn.setFlat(True)
        self.btn_layout.addWidget(self.display_mode_btn)

        self.delete_btn = QtGui.QPushButton("")
        self.delete_btn.setIcon(get_icon("close", 24))
        self.delete_btn.setFixedWidth(22)
        self.delete_btn.setFixedHeight(22)
        self.delete_btn.setFlat(True)
        self.btn_layout.addWidget(self.delete_btn)
        
        self.main_layout.addItem(self.btn_layout)

        self.thumbnail = QtGui.QLabel()
        self.thumbnail.setFixedWidth(90)
        self.thumbnail.setFixedHeight(90)
        self.pixmap = QtGui.QPixmap(90,90)
        self.pixmap.loadFromData(self.thumbnail_binary)
        self.thumbnail.setPixmap(self.pixmap)
        self.thumbnail.setStyleSheet("""QLabel{border: 1px solid black}""")
        self.main_layout.addWidget(self.thumbnail)

        self.influence_base = InfluenceBarWidget(value = self.influence)
        self.main_layout.addWidget(self.influence_base)

        self.setLayout(self.main_layout)

    def show_object(self):

        pass

class InfluenceBarWidget(QtGui.QWidget):
    """ Special custom slider used in the collection thumbnail widget
        to set the influence of the given props in the instance scattering
    """
    def __init__(self, value=50.0, w=91, h=15, idx=0, callback=None, parent=None):
        
        super(InfluenceBarWidget, self).__init__(parent=parent)
        
        self.main_layout = QtGui.QHBoxLayout()

        self.callback = callback
        self.idx = idx
        self._value = value
        self._w = w
        self._h = h
        self.setContentsMargins(0, 0, 0, 0)

        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(QtCore.Qt.AlignLeft)
        
        self.setFixedWidth(w)
        self.setFixedHeight(h)
        
        self.slider = QtGui.QSlider()
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(value)
        self.slider.setFixedWidth(w-25)
        self.slider.setFixedHeight(h)
        self.slider.setStyleSheet(self._slider_styleSheet())
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.valueChanged.connect(self._update_from_slider)
        self.slider.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.slider)

        self.numeric_input = QtGui.QSpinBox()
        self.numeric_input.setFixedWidth(25)
        self.numeric_input.setFixedHeight(h)
        self.numeric_input.setMinimum(0)
        self.numeric_input.setMaximum(100)
        self.numeric_input.setValue(value)
        self.numeric_input.setStyleSheet(self._numeric_input_stylesheet())
        nb = QtGui.QAbstractSpinBox.ButtonSymbols.NoButtons
        self.numeric_input.setButtonSymbols(nb)
        self.numeric_input.setContentsMargins(0, 0, 0, 0)
        self.numeric_input.valueChanged.connect(self._update_from_numeric)
        self.main_layout.addWidget(self.numeric_input)

        self.setLayout(self.main_layout)

    def _update_from_numeric(self):

        self._value = self.numeric_input.value()
        self.slider.setValue(self._value)

    def _update_from_slider(self):

        self._value = self.slider.value()
        self.numeric_input.setValue(self._value)

        if self.callback:
            self.callback(self.idx, self._value)

    def _numeric_input_stylesheet(self):
        
        return ''' QSpinBox{background-color: #474b5e;
                            border: 0px;}'''

    def _slider_styleSheet(self):

        return '''
                QSlider::handle{
                    margin-top: -9px;
                    margin-bottom: -9px;
                    background-color: #002bcb;
                    height ''' + str(self._h) + ''';
                    width: 6px;
                    border: 1px solid #001f92;
                }

                QSlider::sub-page:horizontal {
                    margin-top: -9px;
                    margin-bottom: -9px;
                    background: qlineargradient(x1: 0, y1: 0,
                                                x2: 0, y2: 1,
                        stop: 0 #3a60f1, stop: 1 #002bcb);
                    background: qlineargradient(x1: 0, y1: 0.2,
                                                x2: 1, y2: 1,
                        stop: 0 #3a60f1, stop: 1 #002bcb);
                    height: ''' + str(self._h) + '''px;
                }

                QSlider::add-page:horizontal {
                    margin-top: -9px;
                    margin-bottom: -9px;
                    background: #585e76;
                    height: ''' + str(self._h) + '''px;
                }'''
        
    def get_value(self):

        return self._value

    def set_value(self, value):

        if value > 100:
            value = 100

        elif value < 0:
            value = 0

        self._value = value
        self.slider.setValue(value)
        self.numeric_input.setValue(value)