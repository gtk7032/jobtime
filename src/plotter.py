from typing import Any, Tuple, Union

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

    def plot_barh(
        self,
        yticks: Any,
        lens: list[list[float]],
        btms: list[list[float]],
        clrs: list[list[str]],
        lbls: dict[str, str],
    ) -> None:

        clr_set = {c for clr in clrs for c in clr}
        dmyv = [0.0 for _ in range(len(yticks))]
        if "g" in clr_set:
            plt.barh(yticks, dmyv, left=dmyv, color="g", label=lbls["g"])
        if "b" in clr_set:
            plt.barh(yticks, dmyv, left=dmyv, color="b", label=lbls["b"])
        if "r" in clr_set:
            plt.barh(yticks, dmyv, left=dmyv, color="r", label=lbls["r"])
        for btm, ln, clr in zip(btms, lens, clrs):
            plt.barh(yticks, ln, left=btm, height=0.3, color=clr)

    def save(self, output: str, show: bool = False) -> None:
        plt.legend()
        plt.savefig(output, bbox_inches="tight")
        if show:
            plt.show()
