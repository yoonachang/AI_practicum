install:
	pip install -r requirements.txt

zip:
	rm -f jocalf.zip
	zip -r checkers.zip *