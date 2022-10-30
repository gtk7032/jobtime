import numpy as np
from matplotlib import pyplot as plt


class Plotter:
    def set_canvas(
        self, yticks: list[float], ylbls: list[str], xrange: dict[str, float]
    ) -> None:
        plt.figure(figsize=(12.0, 9.0))
        plt.yticks(yticks, ylbls)
        plt.xlim([xrange["min"], xrange["max"]])
        plt.xticks(np.arange(xrange["min"], xrange["max"] + 1, 1))
        plt.grid(color="gray", alpha=0.5)
        plt.rcParams["font.family"] = "IPAexGothic"

    def plot_barh(
        self,
        y: list[float],
        lens: list[list[float]],
        btms: list[list[float]],
        clr: str,
        lbl: list[str],
    ) -> None:

        for b, l in zip(btms, lens):
            plt.barh(y, l, left=b, height=0.3, color=clr, label=lbl)

    def save(self, output: str) -> None:
        plt.legend()
        plt.savefig(output, bbox_inches="tight")
        plt.show()
