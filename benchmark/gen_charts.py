import datetime
import os
import shutil

import charting
from benchmarking import load_result, clear_env, Path, Subject, log, indent_log, CI

RESULTS = Path("results" if CI else "results_local")
CHARTS = Path("charts" if CI else "charts_local")
CHARTS.mkdir(parents=True, exist_ok=True)

files = [Path(f) for f in os.listdir(RESULTS) if f.endswith(".dat")]
# Latest to earliest
files.sort(reverse=True, key=lambda f: datetime.datetime.strptime(f.stem, "%Y%m%d_%H-%M-%S"))

for file in files:
    log(f"{file}:")
    with indent_log():
        result = load_result(RESULTS / file)
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
        chart.savefig(CHARTS / file.with_suffix(".svg"))
        clear_env()

log()
log(f"Latest: {files[0]}")
shutil.copyfile(CHARTS / files[0].with_suffix(".svg"), CHARTS / "latest.svg")

log()
log("Generating README.md")
with open(CHARTS / "README.md", "w") as f:
    f.write("# All Benchmarks (Reverse Chronological Order)\n")
    f.write("---\n")
    f.write("\n")
    for file in files:
        f.write(f"[![{file.stem}](./{file.with_suffix(".svg")})](./{file.with_suffix(".svg")})\n")
