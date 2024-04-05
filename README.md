# GdMath: a lightning fast spatial math library for gamedev

[![Codegen](https://github.com/shBLOCK/GdMath/actions/workflows/codegen.yml/badge.svg)](https://github.com/shBLOCK/GdMath/actions/workflows/codegen.yml)
[![Tests](https://github.com/shBLOCK/GdMath/actions/workflows/tests.yml/badge.svg)](https://github.com/shBLOCK/GdMath/actions/workflows/tests.yml)
[![Release](https://github.com/shBLOCK/GdMath/actions/workflows/release.yml/badge.svg)](https://github.com/shBLOCK/GdMath/actions/workflows/release.yml)

## Main features
- Fast Pure Cython Implementation
  - ~20x speedup from pure python(3.12) impl on average
  - Based on custom code generation
- Spatial Math
  - [Vector](https://github.com/shBLOCK/GdMath/wiki#vectors)
    - Operators +, -, *, /, @(dot), ^(cross), |(distance) ...
    - Fast (compile time) swizzling (e.g. `Vec3(1, 2, 3).zxy`)
    - Flexible constructor (e.g. `Vec3(Vec2(1, 2), 3)`)
    - Iterating and unpacking (e.g. `x, y, z = Vec3(1, 2, 3)`)
    - Works with other libraries (pygame, numpy, ...)
  - Transform
    - [Transform2D](https://github.com/shBLOCK/GdMath/wiki#transform2d) & [Transform3D](https://github.com/shBLOCK/GdMath/wiki#transform3d)
- All floats are double-precision
- Full pythonic interface & GLSL-like API
- Stubs for better IDE support

Please refer to the [wiki](https://github.com/shBLOCK/GdMath/wiki) for more details

## Benchmark
[![Benchmark Results](https://github.com/shBLOCK/GdMath/tree/master/benchmark/chart.png)](https://github.com/shBLOCK/GdMath/tree/master/benchmark/chart.png)

## Implementation details
- **Codegen!**  
  Custom code generation is used throughout this library.  
  Every swizzle pattern and constructor are implemented as individual methods and properties (For performance reasons).   
  As a result, code generation is required so that I don't have to maintain 50,000+ lines of code by hand...   
  Besides, it also handles vector classes of every dimension and type (e.g. Vec2 Vec3 Vec2i Vec3i) are generated from the same template, so a lot of repetitive code is avoided.
  There's also a stub generator.

## Notes
- This library was initially inspired by [Godot](https://godotengine.org/)'s math library. Pun intended :)