from canvas import Canvas

class DrawingCanvas(Canvas):
	def __init__(self, width=1200, height=1200):
		super().__init__(width, height)
		self.points = []
		self.register_mouse_press(self.on_click)
		self.register_mouse_move(self.on_move)

	def on_click(self, e):
		self.points.clear()

	def on_move(self, e):
		self.clear()
		self.points.append((e.x, e.y))
		self.color = "black"
		self.curve(self.points)

canvas = DrawingCanvas()
