


all:
	python setup.py build_ext install --prefix=$WORK/sleep

clean:
	rm -rf build
	rm -rf dist
	rm -f sleep/*.so
	rm -f sleep/*.cpp
