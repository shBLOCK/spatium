from setuptools import setup, Extension, find_packages
from Cython.Compiler import Options

Options.docstrings = True
# Options.annotate = True

setup(
    ext_modules=[
        Extension(
            "gdmath._gdmath",
            ["src/gdmath/_gdmath.pyx"],
            # extra_compile_args=["-std=c++20", "/std:c++20"],
        ),
    ],
    packages=find_packages(
        where="src",
        exclude=["tests", "gdmath/*.c", "gdmath/*.cpp"]
    ),
    package_dir={'': 'src'},
)
