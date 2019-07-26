"""
QT5 _ Matplotlib _ Interactive

Features:
    * Using the navigation toolbar
    * Adding data to the plot
    * Dynamically modifying the plot's properties
    * Processing mpl events
    * Saving the plot to a file from a menu
The main goal is to serve as a basis for developing rich PyQt GUI
applications featuring mpl plots (using the mpl OO API).
"""

import sys
import os
import csv
import numpy as np

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Demo: PyQt with matplotlib')

        self.data = np.zeros((3, 10))
        self.color1 = 'green'
        self.color2 = 'red'

        self.open_csv_file()

        # self.readDataFromFile()

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self.textbox.setText('1 2 3 4')
        self.on_draw()

    def open_csv_file(self):
        path = QFileDialog.getOpenFileName(self, 'Open CSV', os.getenv('HOME'), 'CSV(*.csv)')
        if path[0] != '':
            with open(path[0], newline='') as csv_file:
                my_file = csv.reader(csv_file, delimiter=',', quotechar='|')
                for i, row_data in enumerate(my_file):
                    for j, stuff in enumerate(row_data):
                        self.data[i][j] = int(stuff)
                        # print(column, stuff, type(stuff))

    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"

        path, ext = QFileDialog.getSaveFileName(self,
                                                'Save file', '',
                                                file_choices)
        path = path.encode('utf-8')
        if not path[-4:] == file_choices[-4:].encode('utf-8'):
            path += file_choices[-4:].encode('utf-8')
        print(path)
        if path:
            self.canvas.print_figure(path.decode(), dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)

    def on_about(self):
        msg = """ PyQt with matplotlib:

         * Use the matplotlib navigation bar
         * Add values to the text box and press Enter (or click "Draw")
         * Show or hide the grid
         * Drag the slider to modify the width of the bars
         * Save the plot to a file using the File menu
         * Click on a bar to receive an informative message
        """
        QMessageBox.about(self, "About the demo", msg.strip())

    def on_draw(self):
        """ Redraws the figure
        """
        str = self.textbox.text().encode('utf-8')
        # self.data = [int(s) for s in str.split()]

        # x = range(len(self.data))
        x = self.data[0]
        y = self.data[1]
        z = self.data[2]

        # clear the axes and redraw the plot anew
        #
        self.axes.clear()
        self.axes.grid(self.grid_cb.isChecked())

        self.axes.plot(x, y, color=self.color1, marker='o', linestyle='dashed',
                       label='line 1',
                       linewidth=self.slider.value() / 100.0,
                       picker=5)

        self.axes.plot(x, z, color=self.color2, marker='s',
                       label='line 2',
                       linewidth=self.slider.value() / 100.0,
                       picker=5)

        self.canvas.draw()

    def on_color_picker(self, name):
        color = QColorDialog.getColor()
        if color.isValid():
            # print(color.name())
            if (name == 'button1'):
                self.color1 = color.name()
            else:
                self.color2 = color.name()
            self.on_draw()

    def create_main_frame(self):
        self.main_frame = QWidget()

        # Create the mpl Figure and FigCanvas objects.
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)

        # Since we have only one plot, we can use add_axes
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        self.axes = self.fig.add_subplot(111)

        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        # Other GUI controls
        #
        self.textbox = QLineEdit()
        self.textbox.setMinimumWidth(200)
        self.textbox.editingFinished.connect(self.on_draw)

        self.draw_button = QPushButton("&Draw")
        self.draw_button.clicked.connect(self.on_draw)

        self.color_picker_button1 = QPushButton("Color Picker #1")
        self.color_picker_button1.setToolTip('Opens color dialog')
        self.color_picker_button1.clicked.connect(lambda: self.on_color_picker('button1'))

        self.color_picker_button2 = QPushButton("Color Picker #2")
        self.color_picker_button2.setToolTip('Opens color dialog')
        self.color_picker_button2.clicked.connect(lambda: self.on_color_picker('button2'))

        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        self.grid_cb.stateChanged.connect(self.on_draw)

        slider_label = QLabel('Bar width (%):')
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 100)
        self.slider.setValue(20)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.valueChanged.connect(self.on_draw)

        #
        # Layout with box sizers
        #
        hbox = QHBoxLayout()

        for w in [self.textbox, self.draw_button, self.color_picker_button1, self.color_picker_button2, self.grid_cb,
                  slider_label, self.slider]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)

        # ************12
        # self.fileNameTextBox.valueChanged.connect(self.on_file_name_changed)
        self.textbox.editingFinished.connect(self.on_draw)

        # ************12

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)

        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    def on_data_right_shift(self):
        temp = [y + 1 for y in self.data]
        self.data = temp
        self.on_data_changed_draw()
        # [print (y) for y in self.data]

    def on_data_changed_draw(self):

        x = range(len(self.data))

        # clear the axes and redraw the plot anew
        #
        self.axes.clear()
        self.axes.grid(self.grid_cb.isChecked())

        self.axes.plot(x, self.data, 'go-',
                       label='line 1',
                       linewidth=self.slider.value() / 100.0,
                       picker=5)

        self.axes.plot(x, x, 'rs-',
                       label='line 2',
                       linewidth=self.slider.value() / 100.0,
                       picker=5)

        self.canvas.draw()

    def create_status_bar(self):
        self.status_text = QLabel("This is verion 0.1 and need to be completed")
        self.statusBar().addWidget(self.status_text, 1)

    def create_menu(self):
        self.file_menu = self.menuBar().addMenu("&File")

        load_file_action = self.create_action("&Save plot",
                                              shortcut="Ctrl+S", slot=self.save_plot,
                                              tip="Save the plot")
        quit_action = self.create_action("&Quit", slot=self.close,
                                         shortcut="Ctrl+Q", tip="Close the application")

        self.add_actions(self.file_menu,
                         (load_file_action, None, quit_action))

        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About",
                                          shortcut='F1', slot=self.on_about,
                                          tip='About the demo')

        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(self, text, slot=None, shortcut=None,
                      icon=None, tip=None, checkable=False):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action


def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()
