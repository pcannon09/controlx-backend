import json
from typing import Any

from .modules.CXB_ScreenInfo import *

def getJSON(path: str) -> tuple[Any, bool]:
	try:
		with open(path, 'r') as file:
			data = json.load(file)

			return data, True
		
	except Exception as E:
		return E, False

jsonConfigFile = getJSON(".private/config/main.json")[0]

CSMOOTHING = float(jsonConfigFile["smoothing"])
CPINCH_THRESHOLD = float(jsonConfigFile["pinchThreshold"])
CDRAG_TIME = float(jsonConfigFile["dragTime"])
CDBL_CLICK_TIME = float(jsonConfigFile["doubleClickTime"])
CSCROLL_SPEED = float(jsonConfigFile["scrollSpeed"])
CDEFAULT_HAND = str(jsonConfigFile["hand"])

monitorInfo = getAll()[0]

