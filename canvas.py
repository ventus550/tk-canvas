import tkinter as tk
import threading
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from itertools import chain


class Canvas(threading.Thread):
	def __init__(self, width=1200, height=1200):
		threading.Thread.__init__(self)
		self.lock = threading.RLock()
		self.start()

		self.width = width
		self.height = height
		self.history = []
		self.color = "black"
		self.lock.acquire()
	
	def callback(self):
		self.root.quit()

	def run(self):
		self.lock.acquire()
		self.root = tk.Tk()
		self.root.protocol("WM_DELETE_WINDOW", self.callback)

		self.canvas = tk.Canvas(self.root, bg="white", width=self.width, height=self.height)
		self.canvas.pack(expand=1, fill=tk.BOTH)

		self.lock.release()
		self.root.mainloop()

	def clear(self):
		self.canvas.delete("all")
	
	def flush(self):
		self.history.clear()

	def reset(self):
		self.clear()
		self.flush()

	def line(self, x0: float, y0: float, x1: float, y1: float, width = 10):
		self.canvas.create_line(
			x0, y0, x1, y1,
			width=width,
			capstyle="round",
			joinstyle="round",
			smooth=True
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

	def point(self, x: float, y: float, size = 10):
		self.canvas.create_oval(
			x, y, x, y,
			fill=self.color,
			outline=self.color,
			width=size
		)
	
	def register_mouse_move(self, f):
		self.canvas.bind('<B1-Motion>', f)

	def register_mouse_press(self, f):
		self.canvas.bind('<ButtonPress-1>', f)

	def register_mouse_release(self, f):
		self.canvas.bind('<ButtonRelease-1>', f)

	def capture(self, size = (70, 70)):
		if not len(self.history): return
		image = Image.new("RGB", size, (255, 255, 255))
		size = np.array(size)
		

		xy, XY = self._get_working_region()
		print(xy, XY)

		dXY = XY - xy
		scale = size / dXY
		points = [ (p - xy) * scale for p in self.history ]

		def line(x0, y0, x1, y1):
			ImageDraw.Draw(image).line((x0, y0, x1, y1), (0,0,0), width=5)
		
		self.line, line = line, self.line
		self.curve(points[-1])
		line, self.line = self.line, line
		image.save("uwu.png")



	def _get_working_region(self):
		if not self.history:
			return np.array((0,0)), np.array((self.width, self.height))
		points = np.array(list(chain(*self.history)))
		return np.min(points, axis=0), np.max(points, axis=0)

	def _draw_bezier_curve(self, points, n = 64):
		def B(P, t):
			if len(P) == 1: return P[0]
			return (1-t)*B(P[:-1], t) + t*B(P[1:], t)

		p = points[0]
		for t in np.linspace(0, 1, n):
			p, q = B(points, t), p
			self.line(*q, *p)
