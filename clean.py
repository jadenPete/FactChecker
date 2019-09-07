#!/usr/bin/env python3

import os

os.chdir("input")

for source in ("huffpost", "theblaze"):
	for name in os.listdir(source):
		path = os.path.join(source, name)

		with open(path, "r") as file:
			if sum(1 for line in file) == 0:
				os.remove(path)
				print("Deleted", path)
