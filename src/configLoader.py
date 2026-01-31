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

CSMOOTHING = int(jsonConfigFile["smoothing"])
CPINCH_THRESHOLD = int(jsonConfigFile["pinchThreshold"])
CDRAG_TIME = int(jsonConfigFile["dragTime"])
CDBL_CLICK_TIME = int(jsonConfigFile["doubleClickTime"])

monitorInfo = getAll()[0]

