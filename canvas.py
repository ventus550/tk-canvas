import tkinter as tk
import threading
import numpy as np
from PIL import Image, ImageDraw
from itertools import chain

class Canvas(threading.Thread):
	def __init__(self, width=1200, height=1200):
		threading.Thread.__init__(self)
		self.lock = threading.RLock()
		self.start()

		self.width = width
		self.height = height
		self.history = []
		self.stroke_color = "black"
		self.stroke_width = 10
		self.lock.acquire()
	
	def callback(self):
		self.root.quit()

	def run(self):
		self.lock.acquire()
		self.root = tk.Tk()
		self.root.protocol("WM_DELETE_WINDOW", self.callback)

		self.canvas = tk.Canvas(self.root, bg="white", width=self.width, height=self.height)
		self.canvas.pack(expand=1, fill=tk.BOTH)
		self.context = self._make_context()

		self.lock.release()
		self.root.mainloop()

	def clear(self):
		self.canvas.delete("all")
		self.context = self._make_context()
	
	def flush(self):
		self.history.clear()

	def reset(self):
		self.clear()
		self.flush()

	def line(self, x0: float, y0: float, x1: float, y1: float):
		self.canvas.create_line(
			x0, y0, x1, y1,
			width=self.stroke_width,
			capstyle="round",
			joinstyle="round",
			smooth=True
		)
		ImageDraw.Draw(self.context).line(
			(x0, y0, x1, y1),
			self.stroke_color,
			self.stroke_width,
			joint='curve'
		)
		sz = self.stroke_width / 2
		ImageDraw.Draw(self.context).ellipse(
			(x0 - sz,y0 - sz,x1 + sz,y1 + sz),
			self.stroke_color
		)

	def curve(self, points: list[tuple[float, float]], spline=True):
		points = list(np.array(points))
		self.history.append(points)

		if not spline:
			self._draw_bezier_curve(points)

		for i in range(4, len(points), 3):
			points[i-1] = (points[i-2] + points[i]) / 2

		for i in range(0, len(points), 3):
			j = min(i+4, len(points))
			self._draw_bezier_curve(points[i:j])

	def point(self, x: float, y: float):
		self.canvas.create_oval(
			x, y, x, y,
			fill=self.stroke_color,
			outline=self.stroke_color,
			width=self.stroke_width
		)
	
	def register_mouse_move(self, f):
		self.canvas.bind('<B1-Motion>', f)

	def register_mouse_press(self, f):
		self.canvas.bind('<ButtonPress-1>', f)

	def register_mouse_release(self, f):
		self.canvas.bind('<ButtonRelease-1>', f)

	def capture(self, margin = None):
		margin = margin or self.stroke_width*2
		xy, XY = self._get_working_region()
		size = (self.width, self.height)
		xy = np.clip(xy - margin, 0, size)
		XY = np.clip(XY + margin, 0, size)
		img = self.context.crop((*xy, *XY))
		return img, xy

	def _make_context(self):
		return Image.new("RGB", (self.width, self.height), (255, 255, 255))

	def _get_working_region(self):
		if not self.history:
			return np.array((0,0)), np.array((self.width, self.height))
		points = np.array(list(chain(*self.history)))
		return np.min(points, axis=0), np.max(points, axis=0)

	def _draw_bezier_curve(self, points, n = 32):
		def B(P, t):
			if len(P) == 1: return P[0]
			return (1-t)*B(P[:-1], t) + t*B(P[1:], t)

		p = points[0]
		for t in np.linspace(0, 1, n):
			p, q = B(points, t), p
			self.line(*q, *p)
