


all:
	pip install . --verbose

clean:
	rm -rf build
	rm -rf dist
	rm -f sleep/*.so
	rm -f sleep/*.cpp
	rm -rf _skbuild
