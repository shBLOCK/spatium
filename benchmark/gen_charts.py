import datetime
import os
import shutil

import charting
from benchmarking import load_result, clear_env, Path, Subject, log, indent_log


files = [f[:-5] for f in os.listdir("results") if f.endswith(".json")]
# Latest to earliest
files.sort(reverse=True, key=lambda f: datetime.datetime.strptime(f, "%Y%m%d_%H-%M-%S"))

for file in files:
    log(f"{file}:")
    with indent_log():
        try:
            result = load_result(Path(f"results/{file}.json"))
            log("Generating chart...")
            chart = charting.chart(
                result,
                Subject.get_instance("pure_python"),
                fig_height=5,
                subtitles=(
                    f"{result.datetime.strftime("%Y/%d/%m-%H:%M")} · "
                    f"{result.metadata.py_impl} {result.metadata.py_ver} · "
                    f"{result.metadata.system} · "
                    f"{result.metadata.cpu}"
                    + ("  (GitHub Actions)" if result.metadata.ci else "")
                    ,
                )
            )
            chart.savefig(f"charts/{file}.svg")
        except Exception as e:
            log(f"Failed to generate chart for {file}.json: {repr(e)}")
        clear_env()

log()
log(f"Latest: {files[0]}")
shutil.copyfile(f"charts/{files[0]}.svg", f"charts/latest.svg")

log()
log("Generating README.md")
with open("charts/README.md", "w") as f:
    f.write("# All Benchmarks (Reverse Chronological Order)\n")
    f.write("---\n")
    f.write("\n")
    for file in files:
        f.write(f"[![{file}](./{file}.svg)](./{file}.svg)\n")
