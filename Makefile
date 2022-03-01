


all:
	python setup.py build_ext install

clean:
	rm -rf build
	rm -rf dist
	rm -f sleep/*.so
	rm -f sleep/*.cpp
