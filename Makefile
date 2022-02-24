


all:
	python setup.py install

clean:
	rm -rf build
	rm -f sleep/*.so
	rm -f sleep/*.cpp
