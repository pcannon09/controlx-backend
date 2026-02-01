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

		self.prevX = 0
		self.prevY = 0

		self.pinchActive = False
		self.pinchStartTime = 0
		self.lastClickTime = 0
		self.dragging = False

		self.rightClickActive = False
		self.rightClickStartTime = 0
		self.lastRightClickTime = 0

		self.airClickCount = 0
		self.lastAirClickTime = 0

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

		# (X) seconds to complete 3 clicks
		# TODO: Add it in config
		TRIPLE_CLICK_WINDOW = 0.7

		while self.cap.isOpened():
			ret, frame = self.cap.read()
			if not ret:
				break

			frame = cv2.flip(frame, 1)
			rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			result = handsEngine.hands.process(rgb)
			timeNow = time.time()

			if result.multi_hand_landmarks:
				handLms = result.multi_hand_landmarks[0]
				handsEngine.mpDraw.draw_landmarks(
					frame,
					handLms,
					handsEngine.mpHands.HAND_CONNECTIONS
				)

				lm = handLms.landmark

				# Cursor movement
				ix = (lm[5].x + lm[8].x) / 2
				iy = (lm[5].y + lm[8].y) / 2

				targetX = int(ix * configLoader.monitorInfo.width)
				targetY = int(iy * configLoader.monitorInfo.height)

				alpha = configLoader.CSMOOTHING
				x = int(self.prevX + alpha * (targetX - self.prevX))
				y = int(self.prevY + alpha * (targetY - self.prevY))

				self.prevX, self.prevY = x, y
				mc.position = (x, y)

				# Pinch detection
				thumbTip = lm[4]
				indexTip = lm[8]

				pinchDistance = CXB_Utils.distance(
					(thumbTip.x, thumbTip.y),
					(indexTip.x, indexTip.y)
				)

				isPinch = pinchDistance < configLoader.CPINCH_THRESHOLD

				# Pinch start
				if isPinch and not self.pinchActive:
					self.pinchActive = True
					self.pinchStartTime = timeNow

				# Pinch release (click logic)
				elif not isPinch and self.pinchActive:
					self.pinchActive = False
					duration = timeNow - self.pinchStartTime

					# Long pinch is drag end
					if duration >= configLoader.CDRAG_TIME:
						if self.dragging:
							mc.release(Button.left)
							self.dragging = False
						continue

					# Short pinch is air click
					if timeNow - self.lastAirClickTime > TRIPLE_CLICK_WINDOW:
						self.airClickCount = 0

					self.airClickCount += 1
					self.lastAirClickTime = timeNow

					# Triple click; RIGHT CLICK
					if self.airClickCount == 3:
						mc.click(Button.right)
						self.airClickCount = 0
						continue

					# Double click; double left
					if self.airClickCount == 2:
						mc.click(Button.left, 2)
						continue

					# Single click; left click
					if self.airClickCount == 1:
						mc.click(Button.left)

				# Drag activation
				if self.pinchActive and not self.dragging:
					if timeNow - self.pinchStartTime > configLoader.CDRAG_TIME:
						mc.press(Button.left)
						self.dragging = True

				# Visual feedback
				if self.pinchActive:
					cv2.circle(
						frame,
						(int(lm[8].x * frame.shape[1]), int(lm[8].y * frame.shape[0])),
						15,
						(0, 255, 0),
						-1
					)

				if self.airClickCount > 0:
					cv2.putText(
						frame,
						f"Clicks: {self.airClickCount}",
						(50, 50),
						cv2.FONT_HERSHEY_SIMPLEX,
						1,
						(255, 255, 0),
						2
					)

			cv2.imshow("CXB Camera", frame)

			if cv2.waitKey(1) & 0xFF == ord('q'):
				break

		self.cap.release()
		cv2.destroyAllWindows()

