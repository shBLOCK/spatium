# GdMath: a fast math library for game development

## Main features
- 100% Cython implementation (~30x speedup from pure python on average)
- Linear Algebra
  - Vector
    - Pythonic and GLSL-like
    - +, -, *, /, @(dot), ^(cross) ...
    - Fast swizzling (e.g. `Vec3(1, 2, 3).zxy`)
    - Flexible constructor (e.g. `Vec3(Vec2(1, 2), 3)`)
    - Iterating and unpacking (e.g. `x, y, z = Vec3(1, 2, 3)`)
  - Transform
    - W.I.P

## Implementation detiles
**This library uses code generation.**   
Every swizzle pattern and constructor are implemented as individual methods and properties (For performance reasons).   
As a result, code generation is required so that I don't have to maintain 50,000+ lines of code by hand...   
Besides, it also has the convenience that vector classes of every dimension and type (e.g. Vec2 Vec3 Vec2i Vec3i) are generated from the same template, so a lot of repetitive code is avoided.

## Notes
- This library was initially inspired by [Godot](https://godotengine.org/)'s math library. (pun intended)   
- FYI, when I was coding this, I didn't know about `Cython.Tempita` until it's too late. It'd probably be a lot easier if I knew it from the beginning and don't have to write as much codegen by myself... But I'd still need to do things like overloading by myself anyway, so it's not a big deal.