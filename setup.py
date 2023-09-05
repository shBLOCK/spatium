from setuptools import setup, Extension, find_packages

setup(
    ext_modules=[
        Extension("gdmath.vector", ["src/gdmath/vector.pyx", "src/gdmath/vector.c"])
    ],
    packages=find_packages(
        where="src",
        exclude=["tests"]
    ),
    package_dir={'': 'src'},
)
