from typing import Any

import time

import cv2

from pynput.mouse import Button, Controller

from .modules.CXB_Logger import log

import src.CXB_Utils as CXB_Utils
import src.configLoader as configLoader

class CXB_Camera():
	def __init__(self, id: str):
		self.cap: cv2.VideoCapture = cv2.VideoCapture(0)
		self.attachedList: list = [
			[ None, "<Error>"]
		]

		self.id: str = id

		self.prevX: int = 0
		self.prevY: int = 0
		self.pinchStartTime: float = 0
		self.lastClickTime: float = 0

		self.pinchActive: bool = False

	def attach(self, elem, id: str):
		self.attachedList.append([elem, id])
		print(self.attachedList)
		log(f"{self.id}: Attached element with ID of: {id}", 3)

	def getAttached(self, id) -> Any:
		if not id:
			return self.attachedList[0][0]

		for subList in self.attachedList:
			print(subList)
			for item in subList:
				if item == id:
					print(subList[0])
					return subList[0]

		return self.attachedList[0][0]

	def run(self):
		while self.cap.isOpened():
			ret, frame = self.cap.read()

			if not ret: break

			# Mirror camera
			frame = cv2.flip(frame, 1)
			rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			result = self.getAttached("main-hands").hands.process(rgb)

			if result.multi_hand_landmarks:
				for handLms in result.multi_hand_landmarks:
					self.getAttached("main-hands").mpDraw.draw_landmarks(
							frame,
							handLms,
							self.getAttached("main-hands").mpHands.HAND_CONNECTIONS
							)

				lm = result.multi_hand_landmarks[0].landmark

				# Cursor data and cursor modifications
				targetX = int(lm[8].x * configLoader.monitorInfo.width)
				targetY = int(lm[8].y * configLoader.monitorInfo.height)

				x = int(configLoader.CSMOOTHING * targetX + (1 - configLoader.CSMOOTHING) * self.prevX)
				y = int(configLoader.CSMOOTHING * targetY + (1 - configLoader.CSMOOTHING) * self.prevY)

				self.prevX = x
				self.prevX = y

				self.getAttached("main-sysController").move(x, y)

				# Pinch detection
				thumbTip = lm[4]
				indexTip = lm[8]

				pinchDistance = CXB_Utils.distance((thumbTip.x, thumbTip.y), (indexTip.x, indexTip.y))
				isPinch = pinchDistance < configLoader.CPINCH_THRESHOLD
				timeNow = time.time()

				# Pinch State Machine
				if isPinch and not self.pinchActive:
					self.pinchActive = True
					self.pinchStartTime = timeNow
				
				elif not isPinch and self.pinchActive:
					self.pinchActive = False
					duration = timeNow - self.pinchStartTime

					if duration < configLoader.CDRAG_TIME:
						if timeNow - self.lastClickTime < configLoader.CDBL_CLICK_TIME:
							self.getAttached("main-sysController").mouseController.click(Button.left, 2)
						
						else:
							self.getAttached("main-sysController").mouseController.click(Button.left)

						self.lastClickTime = timeNow

				if self.pinchActive:
					if timeNow - self.pinchStartTime > configLoader.CDRAG_TIME:
						self.getAttached("main-sysController").mouseController.press(Button.left)

				else: self.getAttached("main-sysController").mouseController.release(Button.left)

			cv2.imshow("CXB Camera", frame)

			if cv2.waitKey(1) & 0xFF == ord('q'): break

		self.cap.release()
		cv2.destroyAllWindows()

