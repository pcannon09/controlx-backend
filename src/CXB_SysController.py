from enum import Enum

from pynput.mouse import Button, Controller

class CXB_SysController:
	def __init__(self, id: str):
		self.mouseController: Controller = Controller()

		self.lastMousePos: tuple = ( -1, -1 )
		self.currentMousePos: tuple = self.mouseController.position

		self.id = id

	def move(self, x: int, y: int):
		self.mouseController.move(x, y)

		if self.lastMousePos != (x, y):
			self.lastMousePos = (x, y)
	
	def click(self, type: Button, count: int = 1):
		self.mouseController.click(type, count)

	def getLastPos(self) -> tuple: return self.lastMousePos

