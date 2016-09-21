
.PHONY:

develop:
	# Hard to bootstrap these setup-requirements from setup.py unless we
	#  are happy to use easy_install. Lets pip them-
	pip install pytest-runner setupext-pip~=1.0.5
	python setup.py requirements --install-test-requirements --install-extra-requirements documentation
	python setup.py develop

test:
	python setup.py test

distclean:
	rm -r dist

dist:
	python setup.py sdist bdist_wheel
