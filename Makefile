
.PHONY:

develop:
	pip install pipenv
	pipenv install --dev --deploy
	python setup.py develop

test:
	python setup.py test

distclean:
	rm -r dist

dist:
	python setup.py sdist bdist_wheel
