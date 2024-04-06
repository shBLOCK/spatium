import codegen_helper as codegen
import vector_codegen


if __name__ == '__main__':
    codegen.step_generate("_gdmath.pyx", write_file=True, _globals=globals())
    # exit()
    codegen.step_gen_stub("_gdmath.pyx", "_gdmath.pyi")

    import os
    if os.getenv("CI") != "true":
        codegen.step_move_to_dest("../src/gdmath/", "_gdmath", ".pyx")
        codegen.step_move_to_dest("../src/gdmath/", "_gdmath", ".pyi")

        import sys
        import subprocess
        print("#"*15 + "pip uninstall gdmath -y" + "#"*15)
        subprocess.call(f"{sys.executable} -m pip uninstall gdmath -y", stdout=sys.stdout)
        print("#"*15 + "pip install -v -v -v .." + "#"*15)
        subprocess.call(f"{sys.executable} -m pip install -v -v -v ..", stdout=sys.stdout, stderr=sys.stdout)
    else:
        print("Running in CI platform!")
