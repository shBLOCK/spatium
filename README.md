# 🚀Spatium: a fast spatial math library

[![PyPI Version](https://img.shields.io/pypi/v/spatium?label=PyPI)](https://pypi.org/project/spatium)
[![Python Version](https://img.shields.io/pypi/pyversions/spatium?label=Python)](https://pypi.org/project/spatium)
<br>
![Language](https://img.shields.io/badge/Language-Cython-FEDF5B)
![Python Implementation](https://img.shields.io/badge/Impl-Cython_|_PyPy-blue)
<br>
[![Codegen](https://github.com/shBLOCK/spatium/actions/workflows/codegen.yml/badge.svg)](https://github.com/shBLOCK/spatium/actions/workflows/codegen.yml)
[![Tests](https://github.com/shBLOCK/spatium/actions/workflows/tests.yml/badge.svg)](https://github.com/shBLOCK/spatium/actions/workflows/tests.yml)
[![Release](https://github.com/shBLOCK/spatium/actions/workflows/release.yml/badge.svg)](https://github.com/shBLOCK/spatium/actions/workflows/release.yml)

## ⚙️Main features
- Fast Pure Cython Implementation
  - ~***20x*** speedup from pure python(3.12) impl on average
  - Based on custom code generation
  - Almost all static dispatch
- Spatial Math
  - [Vector](https://github.com/shBLOCK/spatium/wiki#vectors)
    - Operators +, -, *, /, @(dot), ^(cross), |(distance) ...
    - Fast (compile time) swizzling (e.g. `Vec3(1, 2, 3).zxy`)
    - Flexible constructor (e.g. `Vec3(Vec2(1, 2), 3)`)
    - Iterating and unpacking (e.g. `x, y, z = Vec3(1, 2, 3)`)
    - Works with other libraries (pygame, numpy, ...)
  - Transform
    - [Transform2D](https://github.com/shBLOCK/spatium/wiki#transform2d) & [Transform3D](https://github.com/shBLOCK/spatium/wiki#transform3d)
- All floats are double-precision
- Full pythonic interface & GLSL-like API
- Stubs for better IDE support

Please refer to the [wiki](https://github.com/shBLOCK/spatium/wiki) for more details

## 📈Benchmark
[![Benchmark Results](https://github.com/shBLOCK/spatium/raw/master/benchmark/chart.png)](https://github.com/shBLOCK/spatium/tree/master/benchmark/chart.png)

## 🔧Implementation details
- **Codegen!**  
  Custom code generation is used throughout this library.<br>
  Every swizzle pattern and constructor are implemented as individual methods and properties (For performance reasons).<br>
  As a result, code generation is required so that I don't have to maintain 50,000+ lines of code by hand...<br>
  Besides, it also handles vector classes of every dimension and type (e.g. Vec2 Vec3 Vec2i Vec3i) are generated from the same template, so a lot of repetitive code is avoided.<br>
  There's also a stub generator.

## Credits
- This library is partially inspired by [Godot](https://godotengine.org/)'s math library.

## Notes
- This library was originally named GdMath, as I originally used this to bridge Python and Godot and focus on gamedev.
<br>
As development went on,
I realized that it has become a versatile spatial math library which is also one of the fastest,
I also found it useful in many projects.
<br>
Thus, I've decided to rename it to Spatium (since Spatial was taken), before it (possibly) gets used by more people.
