from canvas import Canvas

class DrawingCanvas(Canvas):
	def __init__(self, width=1200, height=1200):
		super().__init__(width, height)
		self.points = []
		self.register_mouse_press(self.on_click)
		self.register_mouse_move(self.on_move)
		self.register_mouse_release(self.on_release)

	def on_click(self, _):
		self.points.clear()

	def on_move(self, e):
		self.reset()
		self.points.append((e.x, e.y))
		self.stroke_color = "black"
		self.curve(self.points)

	def on_release(self, _):
		img, _ = self.capture()
		img.save("capture.png")


canvas = DrawingCanvas()
