import mediapipe as mp
import mediapipe.python.solutions.hands as solutions_hands
import mediapipe.python.solutions.drawing_utils as drawing_utils

class CXB_GestureEngine:
	def __init__(self, id: str):
		self.mpHands = solutions_hands
		self.hands = self.mpHands.Hands(
			max_num_hands = 1,
			min_detection_confidence=0.7,
			min_tracking_confidence=0.7
		)

		self.mpDraw = drawing_utils

		self.id: str = id

