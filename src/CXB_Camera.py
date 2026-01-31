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

				# OPEN HAND = RIGHT CLICK
				openFingers = [
					CXB_Utils.fingerOpen(lm[8], lm[5]),		# index
					CXB_Utils.fingerOpen(lm[12], lm[9]),  	# middle
					CXB_Utils.fingerOpen(lm[16], lm[13]), 	# ring
					CXB_Utils.fingerOpen(lm[20], lm[17])  	# pinky
				]

				isOpenHand = all(openFingers) and not isPinch

				isRightClick = not isOpenHand and timeNow - self.lastClickTime > configLoader.CDBL_CLICK_TIME
				isLeftClick = self.pinchActive and not self.dragging

				# Drag activation
				if isLeftClick and not isRightClick:
					if timeNow - self.pinchStartTime > configLoader.CDRAG_TIME:
						mc.press(Button.left)

						self.dragging = True

				else: mc.release(Button.left)

				# if isRightClick:
				# 	mc.click(Button.right)
				#
				# 	self.lastClickTime = timeNow
				#
				# else: mc.release(Button.right)

				# Visual feedback
				handsEngine.mpDraw.draw_landmarks(frame, result.multi_hand_landmarks[0], handsEngine.mpHands.HAND_CONNECTIONS)

				if isPinch:
					cv2.circle(frame, (int(lm[8].x * frame.shape[1]), int(lm[8].y * frame.shape[0])), 15, (0,255,0), -1)
				elif isOpenHand: cv2.putText(frame, "Right Click", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

			cv2.imshow("CXB Camera", frame)

			if cv2.waitKey(1) & 0xFF == ord('q'):
				break

		self.cap.release()
		cv2.destroyAllWindows()


