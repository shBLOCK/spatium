import codegen_helper as codegen


def main():
    import vector_codegen

    codegen.step_generate(
        "_spatium.pyx",
        write_file=True,
        _globals={vector_codegen.__name__: vector_codegen},
    )
    codegen.step_gen_stub("_spatium.pyx", "_spatium.pyi")

    import sys

    if "--install" in sys.argv:
        print("#" * 15 + " Install " + "#" * 15)
        codegen.step_move_to_dest("../src/spatium/", "_spatium", ".pyx")
        codegen.step_move_to_dest("../src/spatium/", "_spatium", ".pyi")

        import sys
        import subprocess

        print("#" * 15 + " pip uninstall spatium -y " + "#" * 15)
        subprocess.call(
            f"{sys.executable} -m pip uninstall spatium -y", stdout=sys.stdout
        )
        print("#" * 15 + " pip install -v -v -v .. " + "#" * 15)
        subprocess.call(
            f"{sys.executable} -m pip install -v -v -v ..",
            stdout=sys.stdout,
            stderr=sys.stdout,
        )


if __name__ == "__main__":
    main()
