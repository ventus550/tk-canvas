from canvas import Canvas, Event
from time import sleep
from random import choice

class DrawingCanvas(Canvas):
	def __init__(self, width=1200, height=1200):
		super().__init__(width=width, height=height, daemon=False)
		self.points = []

	@Event("<B1-Motion>")
	def on_mouse_move(self, event):
		self.reset()
		self.points.append((event.x, event.y))
		self.curve(self.points)

	@Event("<ButtonPress-1>")
	def on_mouse_press(self, event):
		self.points.clear()

	@Event("<ButtonRelease-1>")
	def on_mouse_release(self, event):
		print(f"Mouse released at: {event.x}, {event.y}")

if __name__ == "__main__":
	canvas = DrawingCanvas()
	while not sleep(1):
		canvas.stroke_color = choice(["red", "green", "blue"])
	canvas.join()