test:
	python runtests.py

testc:
	coverage run runtests.py
	coverage report -m
