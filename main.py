import sys

from src.CXB_Camera import CXB_Camera
from src.CXB_GestureEngine import CXB_GestureEngine
from src.CXB_SysController import CXB_SysController 
from src.modules.CXB_Logger import log

def main() -> int:
	gestureEngine: CXB_GestureEngine = CXB_GestureEngine("gestureEngine")
	sysController : CXB_SysController = CXB_SysController("sysController")
	cam = CXB_Camera("controlx_backend-camera")
	cam.attach(gestureEngine, "main-hands")
	cam.attach(sysController, "main-sysController")

	log(f"Camera initialized with ID of: {cam.id}", 4)

	cam.run()

	return 0

if __name__ == "__main__":
	sys.exit(main())

