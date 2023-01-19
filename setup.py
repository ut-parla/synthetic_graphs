from Cython.Build import cythonize
from setuptools import setup, find_packages
from setuptools.extension import Extension
import os


cuda_flag = os.getenv("ENABLE_CUDA", None)
nvtx_include = os.getenv("NVTX_INCLUDE", None)

nvtx_flag = False

if nvtx_include is not None:
    nvtx_flag = True
    os.environ["CC"] = 'nvcc_wrapper'
    os.environ["CXX"] = 'nvcc_wrapper'

if cuda_flag is not None:
    cuda_flag = True
else:
    cuda_flag = False


def scandir(dir, files=[]):
    for file in os.listdir(dir):
        path = os.path.join(dir, file)
        if os.path.isfile(path) and path.endswith(".pyx"):
            files.append(path.replace(os.path.sep, ".")[:-4])
        elif os.path.isdir(path):
            scandir(path, files)
    return files

compile_args =["-std=c++11","-ldl", "-fno-stack-protector"]

if nvtx_flag:
    include_dirs = [nvtx_include]
    compile_args += ["-DNVTX_ENABLE"]
    print("BUILDING WITH NVTX SUPPORT")
else:
    include_dirs = []

if cuda_flag:
    compile_args += ["-DCUDA_ENABLE"]
    compile_args += ["--expt-extended-lambda", "-Xcudafe","--diag_suppress=esa_on_defaulted_function_ignored"]

def makeExtension(extName):
    extPath = extName.replace(".", os.path.sep)+".pyx"
    return Extension(
        extName,
        [extPath],
        language='c++',
        include_dirs=include_dirs,
        extra_compile_args=compile_args
    )


extNames = scandir("sleep")
extensions = [makeExtension(name) for name in extNames]

setup(
    setup_requires=['setuptools>=18.0', 'wheel', 'Cython'],
    name="sleep",
    packages=["sleep"],
    ext_modules=cythonize(extensions),
    package_data={
        '':['*.pxd']
    },
    zip_safe=False,
    include_package_data=True,
    )



