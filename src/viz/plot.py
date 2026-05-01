"""Matplotlib-based visualization for simulation data."""

from typing import List, Optional, Tuple
import time


class PlotView:
    """Real-time plot visualization using matplotlib."""

    def __init__(self, title: str = "Embedded Simulation", max_points: int = 500):
        self._title = title
        self._max_points = max_points
        self._data_series: List[dict] = []
        self._fig = None
        self._ax = None
        self._running = False

    def add_series(self, name: str, color: str = 'blue'):
        self._data_series.append({
            'name': name,
            'color': color,
            't': [],
            'y': [],
        })

    def push_data(self, series_index: int, y: float):
        if series_index >= len(self._data_series):
            return
        s = self._data_series[series_index]
        t = len(s['t'])
        s['t'].append(t)
        s['y'].append(y)
        if len(s['t']) > self._max_points:
            s['t'].pop(0)
            s['y'].pop(0)

    def show(self, block: bool = True):
        try:
            import matplotlib.pyplot as plt
            self._fig, self._ax = plt.subplots()
            self._ax.set_title(self._title)
            self._ax.set_xlabel('Sample')
            self._ax.set_ylabel('Value')
            self._ax.grid(True, alpha=0.3)

            lines = []
            for s in self._data_series:
                line, = self._ax.plot([], [], label=s['name'], color=s['color'])
                lines.append(line)
            self._ax.legend(loc='upper right')
            plt.ion()
            plt.show(block=block)
        except ImportError:
            print("[PlotView] matplotlib not available, skipping plot.")

    def update(self):
        if self._fig is None:
            return
        try:
            import matplotlib.pyplot as plt
            lines = self._ax.get_lines()
            for i, s in enumerate(self._data_series):
                if i < len(lines):
                    lines[i].set_data(s['t'], s['y'])
            self._ax.relim()
            self._ax.autoscale_view()
            self._fig.canvas.draw()
            self._fig.canvas.flush_events()
        except Exception:
            pass

    def save(self, filename: str):
        if self._fig:
            self._fig.savefig(filename, dpi=150, bbox_inches='tight')
