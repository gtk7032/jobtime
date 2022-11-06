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
        clrs: Union[str, list[list[str]]],
        lbl: str,
    ) -> None:

        if isinstance(clrs, str):
            for i, (btm, ln) in enumerate(zip(btms, lens)):
                if not i:
                    plt.barh(yticks, ln, left=btm, height=0.3, color=clrs, label=lbl)
                else:
                    plt.barh(yticks, ln, left=btm, height=0.3, color=clrs)

        else:

            max_id = 0
            for clr in clrs:
                max_id = max(max_id, len(set(clr)))

            for i, (btm, ln, clr) in enumerate(zip(btms, lens, clrs)):
                if i == max_id:
                    plt.barh(yticks, ln, left=btm, height=0.3, color=clr, label=lbl)
                else:
                    plt.barh(yticks, ln, left=btm, height=0.3, color=clr)

    def save(self, output: str, show: bool = False) -> None:
        plt.legend()
        plt.savefig(output, bbox_inches="tight")
        if show:
            plt.show()
