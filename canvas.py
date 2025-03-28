import tkinter as tk
import threading
import numpy as np
from typing import Callable, TypeAlias
from dataclasses import dataclass
from functools import partial


point: TypeAlias = tuple[float, float]


@dataclass
class Event:
    event_name: str
    callback: Callable
    parent = None

    def __get__(self, obj, objtype=None):
        self.parent = obj
        return self

    def __new__(cls, *args):
        if len(args) >= 2:
            return super().__new__(cls)
        return partial(cls, *args)

    def __call__(self, *args, **kwds):
        self.callback(self.parent, *args, **kwds)

    def detach(self):
        self.parent.unbind(self.event_name)


class Canvas(threading.Thread):
    daemon: bool = True
    width: int = 1200
    height: int = 1200
    stroke_color: str = "black"
    stroke_width: int = 5

    def __init__(self, **properties):
        threading.Thread.__init__(self)
        self.lock = threading.RLock()
        self.start()
        for k, v in self.__class__.__annotations__.items():
            setattr(self, k, properties.get(k, v))
        self.lock.acquire()

    def run(self):
        self.lock.acquire()
        self.root = tk.Tk()

        self.canvas = tk.Canvas(
            self.root, bg="white", width=self.width, height=self.height
        )
        self.canvas.pack(expand=1, fill=tk.BOTH)

        for attr_name in dir(self):
            event = getattr(self, attr_name)
            if isinstance(event, Event):
                setattr(self, attr_name, event)
                self.canvas.bind(event.event_name, event)

        self.lock.release()
        self.root.mainloop()

    def reset(self):
        self.canvas.delete("all")

    def line(self, point1: point, point2: point):
        self.canvas.create_line(
            *point1,
            *point2,
            width=self.stroke_width,
            fill=self.stroke_color,
            capstyle="round",
            joinstyle="round",
            smooth=True,
        )

    def curve(self, points: list[point], spline=True):
        points = list(np.array(points))

        if not spline:
            self._draw_bezier_curve(points)

        for i in range(4, len(points), 3):
            points[i - 1] = (points[i - 2] + points[i]) / 2

        for i in range(0, len(points), 3):
            j = min(i + 4, len(points))
            self._draw_bezier_curve(points[i:j])

    def point(self, point: point):
        self.canvas.create_oval(
            *point,
            *point,
            fill=self.stroke_color,
            outline=self.stroke_color,
            width=self.stroke_width,
        )

    def _draw_bezier_curve(self, points, n=32):
        def B(P, t):
            if len(P) == 1:
                return P[0]
            return (1 - t) * B(P[:-1], t) + t * B(P[1:], t)

        p = points[0]
        for t in np.linspace(0, 1, n):
            p, q = B(points, t), p
            self.line(q, p)
