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
                    # fix
                    {
                        "min": Util.cvrt_to_hour(job.start)
                        if job.start is not None and job.end is not None
                        else 0.0,
                        "len": Util.cvrt_to_hour(job.end) - Util.cvrt_to_hour(job.start)
                        if job.start is None and job.end is not None) and Util.cvrt_to_hour(job.end) - Util.cvrt_to_hour(job.start)
                        > (5 / 60)
                        elif (job.start is not None and job.end is not None) and Util.cvrt_to_hour(job.end) - Util.cvrt_to_hour(job.start) <= (5/60) (5 / 60)
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
            if next(iter(x[1].values())).start is not None
            else next(iter(schedule[x[0]].values())).start,
        )
        return [i[0] for i in s]

    @staticmethod
    def align_order(target: dict[str, dict[str, Jobnet]], orderedkeys: list[str]):
        return {key: target[key] for key in orderedkeys}

    @staticmethod
    def plot(
        jobnets: dict[str, dict[str, Jobnet]],
        schedule: dict[str, dict[str, Jobnet]],
        output: str,
        xrange: dict[str, str],
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

        # jobnetが存在しない時もsheduleを表示する
        # range
        # sae image
