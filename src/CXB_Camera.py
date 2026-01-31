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

		self.prevX: float = 0
		self.prevY: float = 0
		self.pinchStartTime: float = 0
		self.lastClickTime: float = 0

		self.pinchActive: bool = False

	def attach(self, elem, id: str):
		self.attachedList.append([elem, id])
		log(f"{self.id}: Attached element with ID of: {id}", 3)

	def getAttached(self, id) -> Any:
		if not id:
			return self.attachedList[0][0]

		for subList in self.attachedList:
			for item in subList:
				if item == id: return subList[0]

		return self.attachedList[0][0]

	def run(self):
		mc = self.getAttached("main-sysController").mouseController
		handsEngine = self.getAttached("main-hands")

		self.dragging = False

		while self.cap.isOpened():
			ret, frame = self.cap.read()
			if not ret:
				break

			# Mirror camera
			frame = cv2.flip(frame, 1)
			rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			result = handsEngine.hands.process(rgb)

			if result.multi_hand_landmarks:
				for handLms in result.multi_hand_landmarks:
					handsEngine.mpDraw.draw_landmarks(
						frame,
						handLms,
						handsEngine.mpHands.HAND_CONNECTIONS
					)

				lm = result.multi_hand_landmarks[0].landmark

				# Finger position
				ix = (lm[5].x + lm[8].x) / 2
				iy = (lm[5].y + lm[8].y) / 2

				targetX = int(ix * configLoader.monitorInfo.width)
				targetY = int(iy * configLoader.monitorInfo.height)

				# EMA smoothing
				alpha = configLoader.CSMOOTHING

				x = int(self.prevX + alpha * (targetX - self.prevX))
				y = int(self.prevY + alpha * (targetY - self.prevY))

				self.prevX, self.prevY = x, y

				# Absolute cursor move
				mc.position = (x, y)

				# Pinch detection
				thumbTip = lm[4]
				indexTip = lm[8]

				pinchDistance = CXB_Utils.distance(
					(thumbTip.x, thumbTip.y),
					(indexTip.x, indexTip.y)
				)

				isPinch = pinchDistance < configLoader.CPINCH_THRESHOLD
				timeNow = time.time()

				# Pinch start
				if isPinch and not self.pinchActive:
					self.pinchActive = True
					self.pinchStartTime = timeNow

				# Pinch release
				elif not isPinch and self.pinchActive:
					self.pinchActive = False

					duration = timeNow - self.pinchStartTime

					if self.dragging:
						mc.release(Button.left)

						self.dragging = False

					elif duration < configLoader.CDRAG_TIME:
						if timeNow - self.lastClickTime < configLoader.CDBL_CLICK_TIME:
							mc.click(Button.left, 2)
						else: mc.click(Button.left)

						self.lastClickTime = timeNow

				# Drag activation
				if self.pinchActive and not self.dragging:
					if timeNow - self.pinchStartTime > configLoader.CDRAG_TIME:
						mc.press(Button.left)
						self.dragging = True

			cv2.imshow("CXB Camera", frame)

			if cv2.waitKey(1) & 0xFF == ord('q'):
				break

		self.cap.release()
		cv2.destroyAllWindows()


