import sys
import time

import numpy as np

from matplotlib.backends.qt_compat import QtWidgets, QtCore
from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from multiprocessing import Process, Queue

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self, monitor):
        super().__init__()

        self.monitor = monitor

        self.sample_rate = 2e9
        
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        
        layout = QtWidgets.QVBoxLayout(self._main)
        
        self.samples = np.array([0 for i in range(4096)])

        self.time_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        # Ideally one would use self.addToolBar here, but it is slightly
        # incompatible between PyQt6 and other bindings, so we just add the
        # toolbar as a plain widget instead.
        layout.addWidget(NavigationToolbar(self.time_canvas, self))
        layout.addWidget(self.time_canvas)

        self.freq_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(self.freq_canvas)
        layout.addWidget(NavigationToolbar(self.freq_canvas, self))

        self.IQ_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(self.IQ_canvas)
        layout.addWidget(NavigationToolbar(self.IQ_canvas, self))
        
        self._time_ax = self.time_canvas.figure.subplots()
        self._time_ax.set_ylim([-1,1])
        self._real_plot, = self._time_ax.plot(self.t, np.real(self.samples))
        self._imag_plot, = self._time_ax.plot(self.t, np.imag(self.samples))

        self._time_ax.grid(True)
        
        self._freq_ax = self.freq_canvas.figure.subplots()
        self._freq_ax.set_ylim([-60,0])

        self._freq_ax.grid(True)

        
        self._iq_ax = self.IQ_canvas.figure.subplots()
        self._iq_ax.set_xlim([-1,1])
        self._iq_ax.set_ylim([-1,1])

        self._iq_ax.grid(True)
        
        # Set up a Line2D.
        self._spectrum, = self._freq_ax.plot(self.f, self.dB)

        self._iq, = self._iq_ax.plot(np.real(self.samples), np.imag(self.samples), marker='.', ls='')
        
        self._timer = self.freq_canvas.new_timer(50)
        self._timer.add_callback(self._update)
        self._timer.start()

    @property
    def samples(self):
        return self._samples

    @samples.setter
    def samples(self, v):
        self._samples = v
        self.N = len(v)
        self.t = np.arange(0, self.N) / self.sample_rate
        self.f = np.fft.fftshift(np.fft.fftfreq(self.N)) * self.sample_rate
        self.fft = np.abs(np.fft.fftshift(np.fft.fft(v))) / self.N

        self.fft[self.fft == 0] = 1e-100
        
        self.dB = np.nan_to_num(10 * np.log10(self.fft), nan=-100, posinf=100, neginf=-100)
        
    def _update(self):
        while not self.monitor.queue.empty():
            self.samples = self.monitor.queue.get()

        self._spectrum.set_data(self.f, self.dB)
        self.freq_canvas.draw()
        
        self._time_ax.set_xlim((0, self.t[-1]))
        self._real_plot.set_data(self.t, np.real(self.samples))
        self._imag_plot.set_data(self.t, np.imag(self.samples))
        self.time_canvas.draw()

        self._iq.set_data(np.real(self.samples), np.imag(self.samples))
        self.IQ_canvas.draw()
        
class MonitorApplication:
    def __init__(self, queue):
        self.queue = queue
        self.qapp = QtWidgets.QApplication([])
        app = ApplicationWindow(self)
        app.show()
        app.activateWindow()
        app.raise_()
        self.qapp.exec()
        
class Monitor:
    def __init__(self):
        self.queue = Queue()
        self.p = Process(target=MonitorApplication, args=(self.queue,), daemon=True)
        self.p.start()

    def send(self, data):
        self.queue.put(data)
