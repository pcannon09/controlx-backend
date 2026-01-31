import time

from enum import Enum

from pynput.mouse import Button, Controller

class SysController:
	def __init__(self):
		self.mouseController: Controller = Controller()

		self.lastMousePos: tuple = ( -1, -1 )
		self.currentMousePos: tuple = self.mouseController.position

	def move(self, x: int, y: int):
		self.mouseController.move(x, y)

		if self.lastMousePos != (x, y):
			self.lastMousePos = (x, y)
	
	def click(self, type: Button):
		self.mouseController.click(type)

	def getLastPos(self) -> tuple: return self.lastMousePos

def mainTest():
	cont = SysController()
	print(cont.getLastPos())
	cont.move(40, 90)
	time.sleep(0.3)
	print(cont.getLastPos())
	time.sleep(0.3)
	cont.move(70, 100)
	print(cont.getLastPos())

if __name__ == "__main__":
	mainTest()

