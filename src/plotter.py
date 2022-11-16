from typing import Any, Tuple

import numpy as np
from matplotlib import pyplot as plt


class Plotter:
    def set_canvas(
        self,
        yticks: list[float],
        ylbls: list[str],
        xrange: dict[str, float],
        figsize: Tuple[int, int],
    ) -> None:
        plt.figure(figsize=figsize)
        plt.yticks(yticks, ylbls)
        plt.xlim([xrange["min"], xrange["max"]])
        plt.xticks(np.arange(xrange["min"], xrange["max"] + 1, 1))
        plt.grid(color="gray", alpha=0.5)
        plt.rcParams["font.family"] = "IPAexGothic"
        plt.rc("svg", fonttype="none")

    @staticmethod
    def create_single_colormap(sizex: int, sizey: int, color: str) -> list[list[str]]:
        return [[color] * sizey for _ in range(sizex)]

    def plot_barh(
        self,
        yticks: Any,
        lens: list[list[float]],
        btms: list[list[float]],
        clrs: list[list[str]],
        lbls: dict[str, str],
    ) -> None:

        clr_set = {c for clr in clrs for c in clr}
        dmy_clr = [0.0 for _ in range(len(yticks))]
        for c in clr_set:
            plt.barh(yticks, dmy_clr, left=dmy_clr, color=c, label=lbls[c])
        for btm, ln, clr in zip(btms, lens, clrs):
            plt.barh(yticks, ln, left=btm, height=0.3, color=clr)

    def save(self, output: str, show: bool = False) -> None:
        plt.legend()
        plt.savefig(output, bbox_inches="tight")
        if show:
            plt.show()
