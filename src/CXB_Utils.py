from typing import Any
import numpy as np

def distance(a: tuple, b: tuple) -> np.floating[Any]:
	return np.linalg.norm(np.array(a) - np.array(b))

def fingerOpen(tip, mcp) -> float:
	return tip.y - mcp.y

