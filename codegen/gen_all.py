import codegen_helper as codegen
import vector_codegen


if __name__ == '__main__':
    vector_codegen.run()
    codegen.step_generate("transform_2d.pyx")
    # codegen.step_generate("transform_3d.pyx")

    import os
    if os.getenv("CI") != "true":
        codegen.step_move_to_dest("../src/gdmath/", "vector", ".pyx")
        codegen.step_move_to_dest("../src/gdmath/", "transform_2d", ".pyx")
