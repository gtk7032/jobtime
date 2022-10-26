from typing import Optional, Tuple

import numpy as np
from matplotlib import pyplot as plt

from jobnet import Jobnet


class Plotter:
    @staticmethod
    def format(
        jobnets: dict[str, dict[str, Jobnet]]
    ) -> dict[str, list[dict[str, float]]]:

        max_size = max(len(joblist) for joblist in jobnets.values())
        fmtd = {}

        for jobid, joblist in jobnets.items():

            fmtd[jobid] = [
                {"min": 0.0, "len": 0.0} for _ in range(max_size - len(joblist))
            ]
            fmtd[jobid].extend(
                [
                    {
                        "min": job.start if job.is_genuine() else 0.0,
                        "len": max(job.get_duration(), 5 / 60)
                        if job.is_genuine()
                        else 0.0,
                    }
                    for job in joblist.values()
                ]
            )
        return fmtd

    @staticmethod
    def create_barh(
        fmtd_jobnets: dict[str, list[dict[str, float]]]
    ) -> Tuple[list[float], list[float]]:
        btms = []
        lens = []
        for i in range(len(next(iter(fmtd_jobnets.values())))):
            for jobid in fmtd_jobnets.keys():
                btms.append(fmtd_jobnets[jobid][i]["min"])
                lens.append(fmtd_jobnets[jobid][i]["len"])
        return btms, lens

    @staticmethod
    def complete(
        target: dict[str, dict[str, Jobnet]], another: dict[str, dict[str, Jobnet]]
    ):
        for aid, aval in another.items():
            if aid not in target.keys():
                target[aid] = {
                    "0": Jobnet(aid, "0", next(iter(aval.values())).name, None, None)
                }

    @staticmethod
    def get_order(
        jobnets: dict[str, dict[str, Jobnet]], schedule: dict[str, dict[str, Jobnet]]
    ) -> list[str]:
        s = sorted(
            jobnets.items(),
            key=lambda x: next(iter(x[1].values())).start
            or next(iter(schedule[x[0]].values())).start,
        )
        return [i[0] for i in s]

    @staticmethod
    def align_order(target: dict[str, dict[str, Jobnet]], orderedkeys: list[str]):
        return {key: target[key] for key in orderedkeys}

    @staticmethod
    def plot(
        jobnets: dict[str, dict[str, Jobnet]],
        schedule: dict[str, dict[str, Jobnet]],
        output: Optional[str],
        xrange: Optional[dict[str, float]],
    ):

        Plotter.complete(jobnets, schedule)
        Plotter.complete(schedule, jobnets)

        orderedkeys = Plotter.get_order(jobnets, schedule)
        jobnets = Plotter.align_order(jobnets, orderedkeys)
        schedule = Plotter.align_order(schedule, orderedkeys)

        fmtd_jobnets = Plotter.format(jobnets)
        fmtd_schedule = Plotter.format(schedule)

        jbtms, jlens = Plotter.create_barh(fmtd_jobnets)
        sbtms, slens = Plotter.create_barh(fmtd_schedule)

        lbls = [joblist[next(iter(joblist))].name for joblist in jobnets.values()]
        y = np.arange(len(jobnets.keys()))

        plt.figure(figsize=(8.0, 6.0))
        plt.barh(y + 0.4, slens, left=sbtms, height=0.3, color="g", label="予定時間")
        plt.barh(y, jlens, left=jbtms, height=0.3, color="b", label="実行時間")
        plt.legend()
        plt.yticks(y, lbls)
        plt.xlim([0, 9])
        plt.xticks(np.arange(0, 9 + 1, 1))
        plt.grid(color="gray", alpha=0.5)
        plt.rcParams["font.family"] = "IPAexGothic"
        plt.savefig(output, bbox_inches="tight")
        plt.show()
