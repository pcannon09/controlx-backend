import json
from typing import Any, cast

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

monitorInfo = getAll()[0]

