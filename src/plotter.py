from typing import Any, Tuple

import numpy as np
from matplotlib import pyplot as plt

from bar import Bar


class Plotter:
    def set_canvas(
        self,
        yticks: list[float],
        ylbls: list[str],
        xrange: tuple[float, float],
        figsize: Tuple[int, int],
    ) -> None:
        plt.figure(figsize=figsize)
        plt.yticks(yticks, ylbls)
        plt.xlim([xrange[0], xrange[1]])
        plt.xticks(np.arange(xrange[0], xrange[1] + 1, 1))
        plt.grid(color="gray", alpha=0.5)
        plt.rcParams["font.family"] = "IPAexGothic"
        plt.rc("svg", fonttype="none")

    def plot_barh(
        self,
        yticks: Any,
        bars: list[list[Bar]],
        lbls: dict[str, str],
    ) -> None:

        clr_set = {bar.color for col in bars for bar in col}
        dmy_clr = [0.0 for _ in range(len(yticks))]
        for c in clr_set:
            plt.barh(yticks, dmy_clr, left=dmy_clr, color=c, label=lbls[c])
        for col in bars:
            plt.barh(
                yticks,
                [bar.length for bar in col],
                left=[bar.bottom for bar in col],
                height=0.3,
                color=[bar.color for bar in col],
            )

    def save(self, output: str, show: bool = False) -> None:
        plt.legend()
        plt.savefig(output, bbox_inches="tight")
        if show:
            plt.show()
