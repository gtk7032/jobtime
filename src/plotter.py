from typing import Tuple

from bar import Bar
from matplotlib import pyplot as plt


class Plotter:
    def set_canvas(
        self,
        yticks: list[int],
        ylbls: list[str],
        xrange: tuple[int, int],
        figsize: Tuple[int, int],
    ) -> None:
        plt.figure(figsize=figsize)
        plt.yticks(yticks, ylbls)
        plt.xlim([xrange[0], xrange[1]])
        plt.xticks(range(xrange[0], xrange[1] + 1, 1))
        plt.grid(color="gray", alpha=0.5)
        plt.rcParams["font.family"] = "IPAexGothic"
        plt.rc("svg", fonttype="none")

    def plot_barh(
        self,
        yticks: list[float],
        bars: list[list[Bar]],
        lbls: dict[str, str],
    ) -> None:
        clr_set = {bar.color for col in bars for bar in col if bar.color}
        dmy_clr = [0.0 for _ in range(len(yticks))]
        for c in clr_set:
            plt.barh(yticks, dmy_clr, left=dmy_clr, color=c, label=lbls[c])
        for col in bars:
            plt.barh(
                yticks,
                [bar.length for bar in col],
                left=[bar.bottom for bar in col],
                height=0.3,
                # if bar is dummy, set any color
                color=[bar.color if bar.color else "g" for bar in col],
            )

    def save(self, output: str, show: bool = False) -> None:
        plt.legend(loc="upper left")
        plt.savefig(output, bbox_inches="tight")
        if show:
            plt.show()
