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

	def fingersUp(self, lm):
		# Returns list of bools: [thumb, index, middle, ring, pinky]
		tips = [4, 8, 12, 16, 20]
		pip = [3, 6, 10, 14, 18]

		fingers = []

		# Right hand
		if configLoader.CDEFAULT_HAND == "right":
			fingers.append(lm[tips[0]].x < lm[pip[0]].x)

		# Left hand
		else: fingers.append(lm[tips[0]].x > lm[pip[0]].x)

		# Other fingers: y comparison
		for i in range(1, 5):
			fingers.append(lm[tips[i]].y < lm[pip[i]].y)

		return fingers

	def run(self):
		mc = self.getAttached("main-sysController").mouseController
		handsEngine = self.getAttached("main-hands")

		TRIPLE_CLICK_WINDOW = 0.7  # seconds

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
					frame, handLms, handsEngine.mpHands.HAND_CONNECTIONS
				)

				lm = handLms.landmark

				fingers = self.fingersUp(lm)
				isV = fingers[1] and fingers[2] and not fingers[0] and not fingers[3] and not fingers[4]

				# Cursor movement
				ix = (lm[8].x + lm[8].x) / 2
				iy = (lm[8].y + lm[8].y) / 2

				targetX = max(0, min(int(ix * configLoader.monitorInfo.width), configLoader.monitorInfo.width - 1))
				targetY = max(0, min(int(iy * configLoader.monitorInfo.height), configLoader.monitorInfo.height - 1))

				alpha = configLoader.CSMOOTHING
				x = int(self.prevX + alpha * (targetX - self.prevX))
				y = int(self.prevY + alpha * (targetY - self.prevY))

				self.prevX, self.prevY = x, y

				# Two-finger V scroll
				if isV:
					currentX = (lm[8].x + lm[12].x) / 2 * configLoader.monitorInfo.width
					currentY = (lm[8].y + lm[12].y) / 2 * configLoader.monitorInfo.height

					if hasattr(self, 'prevScrollX') and hasattr(self, 'prevScrollY') and self.prevScrollX is not None:
						deltaX = currentX - self.prevScrollX
						deltaY = currentY - self.prevScrollY

						# Use scrollSpeed multiplier from config
						mc.scroll(int(-deltaY * configLoader.CSCROLL_SPEED), int(deltaX * configLoader.CSCROLL_SPEED))

					self.prevScrollX = currentX
					self.prevScrollY = currentY

				else:
					self.prevScrollX = None
					self.prevScrollY = None

				# Update cursor only if not scrolling
				if not isV and fingers:
					mc.position = (x, y)

				# Pinch detection
				thumbTip = lm[4]
				indexTip = lm[8]

				pinchDistance = CXB_Utils.distance(
					(thumbTip.x, thumbTip.y),
					(indexTip.x, indexTip.y)
				)

				isPinch = pinchDistance < configLoader.CPINCH_THRESHOLD

				if isPinch and not self.pinchActive:
					self.pinchActive = True
					self.pinchStartTime = timeNow

				elif not isPinch and self.pinchActive:
					self.pinchActive = False
					duration = timeNow - self.pinchStartTime

					if duration >= configLoader.CDRAG_TIME and self.dragging:
						mc.release(Button.left)
						self.dragging = False
						continue

					if timeNow - self.lastAirClickTime > TRIPLE_CLICK_WINDOW:
						self.airClickCount = 0

					self.airClickCount += 1
					self.lastAirClickTime = timeNow

					if self.airClickCount == 3:
						mc.click(Button.right)
						self.airClickCount = 0

						continue

					elif self.airClickCount == 2:
						mc.click(Button.left, 2)

						continue

					elif self.airClickCount == 1:
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

