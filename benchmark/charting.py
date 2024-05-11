from typing import Iterable

from benchmarking import BenchmarkResult, Subject, TestCaseResult, numerize
import matplotlib.pyplot as plt
from matplotlib import patches, transforms

def get_runtime(result: TestCaseResult) -> int:
    return result.runtime

_TEXT = "#e6edf3"

class BackgroundFancyBboxPatch(patches.FancyBboxPatch):


    def __init__(self, **kwargs):
        super().__init__((0, 0), 1, 1, **kwargs)

    # noinspection PyUnresolvedReferences
    def draw(self, renderer):
        if not self.get_visible():
            return

        self.set_x(0)
        self.set_y(0)
        self.set_width(self.figure.get_figwidth() * self.figure.dpi)
        self.set_height(self.figure.get_figheight() * self.figure.dpi)

        # Don't apply any transforms
        self._draw_paths_with_artist_properties(
            renderer,
            [(self.get_path(), transforms.IdentityTransform(),
              # Work around a bug in the PDF and SVG renderers, which
              # do not draw the hatches if the facecolor is fully
              # transparent, but do if it is None.
              self._facecolor if self._facecolor[3] else None)])


def chart(result: BenchmarkResult, baseline: Subject, *, fig_height=5, subtitles: Iterable[str] = ()) -> plt.Figure:
    fig: plt.Figure
    ax: plt.Axes
    fig, ax = plt.subplots(
        figsize=(len(tuple(result.benchmarks)) * 0.9 + 1, fig_height)
    )

    # Plot Background
    ax.set_facecolor("#21262d")

    # Background
    bg_edge = 2
    bg = BackgroundFancyBboxPatch(
        facecolor="#161b22",
        linewidth=bg_edge,
        edgecolor="#30363d",
        figure=fig
    )
    bg.set_boxstyle("round", pad=-bg_edge / 2, rounding_size=fig.dpi * 0.5)
    fig.patch = bg

    # Title
    ax.set_title(f"Benchmark - {baseline.name} Implementation as Baseline\n"
                 f"Operations Per Second"
                 + (("\n" + "\n".join(subtitles)) if subtitles else ""),
                 color=_TEXT)

    ax.margins(x=0.01)

    ax.axhline(
        y=1,
        color=baseline.color,
        linestyle="--",
        label="Baseline"
    )

    highest = 0
    x_pos = 0
    x_ticks = []
    for benchmark in result.benchmarks:
        subject_ops_per_sec: dict[Subject, float] = {}
        for testcase in benchmark.testcases.values():
            min_runtime = min(r.runtime for r in result.get_results(testcase=testcase))
            subject_ops_per_sec[testcase.subject] = testcase.number / (min_runtime / 1e9)

        begin_pos = x_pos

        for subject, ops_per_sec in sorted(
                subject_ops_per_sec.items(),
                key=lambda pair: pair[0].sort
        ):
            height = ops_per_sec / (subject_ops_per_sec[baseline])
            highest = max(height, highest)
            rect = ax.bar(
                x=x_pos,
                height=height,
                width=1,
                label=subject.name,
                color=subject.color
            )
            ax.bar_label(
                rect,
                padding=3,
                labels=[numerize(ops_per_sec, decimals=1)],
                fontsize=10,
                rotation=90,
                color=_TEXT
            )
            x_pos += 1

        end_pos = x_pos - 1
        x_ticks.append(((begin_pos + end_pos) / 2, benchmark.name))

        x_pos += 1.5

    ax.margins(y=18 / highest / fig_height)

    ax.set_xticks(
        *zip(*x_ticks),
        rotation=15,
        color=_TEXT
    )

    [s.set_color("#ced0d6") for s in ax.spines.values()]
    ax.yaxis.set_major_formatter(lambda x, pos: f"{x}x")
    ax.tick_params(axis="x", colors="#ced0d6")
    ax.tick_params(axis="y", colors="#ced0d6")

    # Legend
    handles, labels = ax.get_legend_handles_labels()
    temp = {k: v for k, v in zip(labels, handles)}
    legend = ax.legend(
        temp.values(), temp.keys(),
        loc="upper left",
        labelcolor=_TEXT,
        facecolor="#3d3f42",
        edgecolor="#3d3f42",
        fancybox = True,
        framealpha = 0.5
    )
    legend.legendPatch.set_boxstyle("round", rounding_size=0.5)

    fig.tight_layout(pad=1)

    return fig
