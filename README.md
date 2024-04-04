# GdMath: a fast math library for game development

[![Codegen](https://github.com/shBLOCK/GdMath/actions/workflows/codegen.yml/badge.svg)](https://github.com/shBLOCK/GdMath/actions/workflows/codegen.yml)
[![Tests](https://github.com/shBLOCK/GdMath/actions/workflows/tests.yml/badge.svg)](https://github.com/shBLOCK/GdMath/actions/workflows/tests.yml)
[![Release](https://github.com/shBLOCK/GdMath/actions/workflows/release.yml/badge.svg)](https://github.com/shBLOCK/GdMath/actions/workflows/release.yml)

## Main features
- 100% Cython implementation (~30x speedup from pure python on average)
  - Codegen based
- Linear Algebra
  - [Vector](https://github.com/shBLOCK/GdMath/wiki#vectors)
    - Pythonic and GLSL-like
    - Operators +, -, *, /, @(dot), ^(cross), |(distance) ...
    - Fast swizzling (e.g. `Vec3(1, 2, 3).zxy`)
    - Flexible constructor (e.g. `Vec3(Vec2(1, 2), 3)`)
    - Iterating and unpacking (e.g. `x, y, z = Vec3(1, 2, 3)`)
  - Transform
    - [Transform2D](https://github.com/shBLOCK/GdMath/wiki#transform2d) & [Transform3D](https://github.com/shBLOCK/GdMath/wiki#transform3d)
    - Godot and GLSL like api
- Stubs for better IDE support

Please refer to the [wiki](https://github.com/shBLOCK/GdMath/wiki) for more details

## Implementation details
**This library uses code generation.**   
Every swizzle pattern and constructor are implemented as individual methods and properties (For performance reasons).   
As a result, code generation is required so that I don't have to maintain 50,000+ lines of code by hand...   
Besides, it also has the convenience that vector classes of every dimension and type (e.g. Vec2 Vec3 Vec2i Vec3i) are generated from the same template, so a lot of repetitive code is avoided.

## Notes
- This library was initially inspired by [Godot](https://godotengine.org/)'s math library. (pun intended)   
- FYI, when I was coding this, I didn't know about `Cython.Tempita` until it's too late. It'd probably be a lot easier if I knew it from the beginning and don't have to write as much codegen by myself... But I'd still need to do things like overloading by myself anyway, so it's not a big deal.