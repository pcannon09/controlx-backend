from ..configLoader import jsonConfigFile

def log(message: str, level: int = 5):
	if int(jsonConfigFile["system"]["logLevel"]) <= level:
		print(message)

