# This Python file uses the following encoding: utf-8
import sys
from PyQt5 import QtWidgets, QtCore
import numpy as np
import pyqtgraph as pg
import warnings


class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        # default values
        self.b = float(1) * 1.E-6  # slit width
        self.lamda = float(400) * 1.E-9  # wavelength
        self.d = float(10) * 1.E-2  # distance of the screen
        self.m = 1  # width of view (count of one side maximums with distance 100 cm)
        self.sampling = 1000  # count of calculating points
        self.fx_l = []  # list of function values
        self.x_l = []  # list of function arguments

        # calculating bounds and step
        self.xmin = np.float64(-self.m * self.lamda / self.b)        # left bound
        self.xmax = np.float64(self.m * self.lamda / self.b)         # right bound
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.step = np.float64((self.xmax - self.xmin) / self.sampling)    # value of step for next point

        # save arguments in list
        for i in range(self.sampling):
            x = self.xmin + i * self.step
            self.x_l.append(x)

        # window adjustment
        self.setWindowTitle("Fraunhofer Diffraction")
        self.setMinimumSize(900, 600)
        self.center()

        # creating main layout and add two sublayouts to it (left and right)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)
        self.view_layout = QtWidgets.QVBoxLayout()
        self.preferences_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.view_layout)
        self.main_layout.addLayout(self.preferences_layout)

        # creating left (view) layout and add plot to it
        self.graphWidget = pg.PlotWidget()
        self.view_layout.addWidget(self.graphWidget)

        # creating right (preferences) layout
        self.item_layouts = [QtWidgets.QVBoxLayout() for _ in range(3)]      # layouts for each preference
        self.item_titles = [QtWidgets.QLabel("Slit width (microns):"),       # titles of preferences
                            QtWidgets.QLabel("Wave length (nanometers):"),
                            QtWidgets.QLabel("Distance of the screen (centimeters):")]
        self.value_layouts = [QtWidgets.QHBoxLayout() for _ in range(3)]            # layouts for pair label-slider
        self.label_values = [QtWidgets.QLabel("0") for _ in range(3)]               # value labels for sliders
        self.sliders = [QtWidgets.QSlider(QtCore.Qt.Horizontal) for _ in range(3)]  # sliders

        # set range for sliders
        self.sliders[0].setRange(1, 10)
        self.sliders[1].setRange(400, 700)
        self.sliders[2].setRange(10, 100)

        # add preferences items in right layout
        for i in range(3):
            self.value_layouts[i].addWidget(self.label_values[i])
            self.value_layouts[i].addWidget(self.sliders[i])
            self.item_layouts[i].addWidget(self.item_titles[i])
            self.item_layouts[i].addLayout(self.value_layouts[i])
            self.preferences_layout.addLayout(self.item_layouts[i])
            self.preferences_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 50))
        self.preferences_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 200))

        # add slots to signals and update class values
        for i in range(3):
            self.sliders[i].valueChanged.connect(self.update_values)
        self.update_values()

    def update_values(self):
        # get values from each slider
        values = []
        for i in range(3):
            values.append(int(self.sliders[i].value()))

        # update data in  labels on screen
        for i in range(3):
            self.label_values[i].setText(str(values[i]))

        # update data in class members and redraw plot
        self.b = values[0] * 1.E-6
        self.lamda = values[1] * 1.E-9
        self.d = values[2] * 1.E-2
        self.calculate()
        self.plot_redraw()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def calculate(self):
        self.fx_l.clear()
        for i in range(self.sampling):
            x = self.x_l[i]
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fx = (np.sin((np.pi * self.b * x) / (self.lamda * self.d)) / ((np.pi * self.b * x) / (self.lamda * self.d))) ** 2
            self.fx_l.append(fx)

    def plot_redraw(self):
        r, g, b = self.wave_length_to_rgb(self.lamda)

        pen = pg.mkPen(color=(r, g, b))
        self.graphWidget.clear()
        self.graphWidget.plot(self.x_l, self.fx_l, pen=pen)

    @staticmethod
    def wave_length_to_rgb(wavelength, gamma=0.8):
        wavelength = float(wavelength) * 1.E+9
        if 380 <= wavelength <= 440:
            attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
            r = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
            g = 0.0
            b = (1.0 * attenuation) ** gamma
        elif 440 <= wavelength <= 490:
            r = 0.0
            g = ((wavelength - 440) / (490 - 440)) ** gamma
            b = 1.0
        elif 490 <= wavelength <= 510:
            r = 0.0
            g = 1.0
            b = (-(wavelength - 510) / (510 - 490)) ** gamma
        elif 510 <= wavelength <= 580:
            r = ((wavelength - 510) / (580 - 510)) ** gamma
            g = 1.0
            b = 0.0
        elif 580 <= wavelength <= 645:
            r = 1.0
            g = (-(wavelength - 645) / (645 - 580)) ** gamma
            b = 0.0
        elif 645 <= wavelength <= 750:
            attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
            r = (1.0 * attenuation) ** gamma
            g = 0.0
            b = 0.0
        else:
            r = 0.0
            g = 0.0
            b = 0.0
        r *= 255
        g *= 255
        b *= 255
        return int(r), int(g), int(b)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
