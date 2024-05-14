from setuptools import setup, Extension, find_packages
from Cython.Compiler import Options

Options.docstrings = True
# Options.annotate = True

setup(
    ext_modules=[
        Extension(
            "spatium._spatium",
            ["src/spatium/_spatium.pyx"],
            # extra_compile_args=["-std=c++20", "/std:c++20"],
        ),
    ],
    packages=find_packages(
        where="src", exclude=["tests", "spatium/*.c", "spatium/*.cpp"]
    ),
    package_dir={"": "src"},
)
