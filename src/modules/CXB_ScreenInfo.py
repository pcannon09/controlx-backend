from screeninfo import get_monitors, Monitor

def getAll() -> list[Monitor]:
	return get_monitors()

