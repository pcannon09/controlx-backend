from screeninfo import get_monitors

for m in get_monitors():
	print(f"W, H: {m.width},{m.height}")

