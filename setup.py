from setuptools import setup, Extension, find_packages


setup(
    ext_modules=[
        Extension("gdmath._gdmath", ["src/gdmath/_gdmath.pyx"]),
    ],
    packages=find_packages(
        where="src",
        exclude=["tests"]
    ),
    package_dir={'': 'src'},
)
