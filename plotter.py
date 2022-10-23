from typing import Tuple

import numpy as np
from matplotlib import pyplot as plt

from jobnet import Jobnet
from util import Util


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
                        "min": Util.cvrt_to_hour(job.start),
                        "len": Util.cvrt_to_hour(job.end) - Util.cvrt_to_hour(job.start)
                        if Util.cvrt_to_hour(job.end) - Util.cvrt_to_hour(job.start)
                        > (5 / 60)
                        else (5 / 60),
                    }
                    for job in joblist.values()
                ]
            )
        return fmtd

    @staticmethod
    def create_jobnet_barh(
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
    def create_schedule_barh(
        fmtd_schedule: dict[str, list[dict[str, float]]], joblogids: list[str]
    ) -> Tuple[list[float], list[float]]:
        btms = []
        lens = []
        for i in range(len(next(iter(fmtd_schedule.values())))):
            for jobid in joblogids:
                btms.append(
                    fmtd_schedule[jobid][i]["min"]
                    if jobid in fmtd_schedule.keys()
                    else 0.0
                )
                lens.append(
                    fmtd_schedule[jobid][i]["len"]
                    if jobid in fmtd_schedule.keys()
                    else 0.0
                )
        return btms, lens

    @staticmethod
    def plot(
        jobnets: dict[str, dict[str, Jobnet]],
        schedule: dict[str, dict[str, Jobnet]],
        output: str,
        xrange: dict[str, str],
    ):
        fmtd_jobnets = Plotter.format(jobnets)
        # print(fmt_jobnets)
        fmtd_schedule = Plotter.format(schedule)
        # print(fmt_schedule)

        jbtms, jlens = Plotter.create_jobnet_barh(fmtd_jobnets)
        sbtms, slens = Plotter.create_schedule_barh(
            fmtd_schedule, list(fmtd_jobnets.keys())
        )

        lbls = [joblist[next(iter(joblist))].name for joblist in jobnets.values()]

        y = np.arange(len(fmtd_jobnets.keys()))

        plt.figure(figsize=(8.0, 6.0))
        plt.barh(y, jlens, left=jbtms, height=0.3, color="b", label="実行時間")
        plt.barh(y + 0.4, slens, left=sbtms, height=0.3, color="g", label="予定時間")
        plt.legend()
        plt.yticks(y, lbls)
        plt.xlim([0, 9])
        plt.xticks(np.arange(0, 9 + 1, 1))

        plt.grid(color="gray", alpha=0.5)
        plt.rcParams["font.family"] = "IPAexGothic"
        # plt.savefig(_path.with_suffix(".png"), bbox_inches="tight")
        plt.show()

        # print(btms)
        # print("\n")
        # print(lens)
        # print("\n")
        # print(lbls)
