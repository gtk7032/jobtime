from __future__ import annotations

import csv
import math
from datetime import datetime as dt
from typing import Any, Tuple

import numpy as np

from util import Util


class Jobnet:

    START_MSG = ["ジョブネットが開始しました。", "Jobnet has started."]
    END_MSG = ["ジョブネットが終了しました。", "Jobnet has ended."]

    def __init__(
        self,
        jobnetid: str,
        innerid: str,
        name: str,
        start: float | None,
        end: float | None,
        isgenuine: bool,
    ):
        self.jobid = jobnetid
        self.inrid = innerid
        self.name = name
        self.start = start
        self.end = end
        self.isgenuine = isgenuine

    def get_duration(self) -> float:
        return self.end - self.start

    @staticmethod
    def extract_xrange(jobnets: dict[str, dict[str, Jobnet]]):
        mn, mx = 24.0, 0.0
        for jn in jobnets.values():
            for j in jn.values():
                mn = min(mn, j.start)
                mx = max(mx, j.end)
        return {"min": mn, "max": mx}

    @staticmethod
    def read_joblog(path: str) -> dict[str, dict[str, Jobnet]]:

        jobnets: dict[str, dict[str, Jobnet]] = {}

        with open(path, "r", encoding="utf-8") as f:

            reader = csv.DictReader(f)

            for row in reader:

                date = Util.cvrt_to_hour(
                    dt.strptime(row["log date"], "%Y/%m/%d %H:%M:%S.%f")
                )
                jobid = row["jobnet id"]
                innerid = row["inner jobnet id"]
                msg = row["message"]
                name = row["jobnet name"]

                if msg in Jobnet.START_MSG:
                    if jobid not in jobnets.keys():
                        jobnets[jobid] = {}
                    jobnets[jobid][innerid] = Jobnet(
                        jobid, innerid, name, date, None, True
                    )

                elif msg in Jobnet.END_MSG:
                    if jobid in jobnets.keys() and innerid in jobnets[jobid].keys():
                        jobnets[jobid][innerid].end = date

        now = Util.cvrt_to_hour(dt.now())
        for joblist in jobnets.values():
            for job in joblist.values():
                if job.end is None:
                    job.end = now

        return Jobnet.sort(jobnets)

    @staticmethod
    def read_schedule(path: str) -> dict[str, dict[str, Jobnet]]:

        schedules: dict[str, dict[str, Jobnet]] = {}

        with open(path, "r", encoding="utf-8") as f:

            reader = csv.DictReader(f)

            for row in reader:
                jobid = row["jobid"]
                inrid = (
                    str(len(schedules[jobid].keys()))
                    if jobid in schedules.keys()
                    else "0"
                )
                jobnm = row["jobnm"]
                start = Util.cvrt_to_hour(dt.strptime(row["start"], "%H:%M:%S"))
                end = Util.cvrt_to_hour(dt.strptime(row["end"], "%H:%M:%S"))

                if jobid not in schedules.keys():
                    schedules[jobid] = {}

                schedules[jobid][inrid] = Jobnet(jobid, inrid, jobnm, start, end, True)

        return Jobnet.sort(schedules)

    @staticmethod
    def format(
        jobnets: dict[str, dict[str, Jobnet]]
    ) -> dict[str, list[dict[str, float]]]:

        max_size = max(len(joblist) for joblist in jobnets.values())
        fmtd = {}

        for jobid, joblist in jobnets.items():
            fmtd[jobid] = [
                {"btm": 0.0, "len": 0.0} for _ in range(max_size - len(joblist))
            ]
            fmtd[jobid].extend(
                [
                    {"btm": job.start, "len": max(job.get_duration(), 5 / 60)}
                    if job.isgenuine
                    else {"btm": 0.0, "len": 0.0}
                    for job in joblist.values()
                ]
            )
        return fmtd

    @staticmethod
    def create_barh(
        fmtd_jobnets: dict[str, list[dict[str, float]]]
    ) -> Tuple[list[list[float]], list[list[float]]]:
        btms = []
        lens = []
        for i in range(len(next(iter(fmtd_jobnets.values())))):
            b, l = [], []
            for jobid in fmtd_jobnets.keys():
                b.append(fmtd_jobnets[jobid][i]["btm"])
                l.append(fmtd_jobnets[jobid][i]["len"])
            btms.append(b)
            lens.append(l)
        return btms, lens

    @staticmethod
    def complement(
        tgt: dict[str, dict[str, Jobnet]], ref: dict[str, dict[str, Jobnet]]
    ) -> dict[str, dict[str, Jobnet]]:

        if not tgt or not ref:
            return tgt

        res = {k: v for k, v in tgt.items() if k in ref.keys()}

        for key in ref.keys():
            if key not in res.keys():
                res[key] = {
                    "0": Jobnet(
                        key, "0", next(iter(ref[key].values())).name, None, None, False
                    )
                }

        return res

    @staticmethod
    def get_order(
        joblogs: dict[str, dict[str, Jobnet]],
    ) -> list[str]:
        s = sorted(joblogs.items(), key=lambda x: next(iter(x[1].values())).start)
        return [i[0] for i in s]

    @staticmethod
    def sortby_givenkeys(
        jobnets: dict[str, dict[str, Jobnet]], keys: list[str]
    ) -> dict[str, dict[str, Jobnet]]:
        if jobnets and keys:
            return {key: jobnets[key] for key in keys}
        else:
            return jobnets

    @staticmethod
    def sort(jobnets: dict[str, dict[str, Jobnet]]) -> dict[str, dict[str, Jobnet]]:

        for jn in jobnets.values():
            sjn = sorted(jn.items(), key=lambda x: x[1].start)
            jn = {jobid: job for jobid, job in sjn}

        jobnets = sorted(
            jobnets.items(),
            key=lambda x: x[1][next(iter(x[1]))].start,
        )
        return {jobid: jobnet for jobid, jobnet in jobnets}

    @staticmethod
    def extract_plotdata(
        jobnets: dict[str, dict[str, Jobnet]],
    ) -> Tuple[list[list[float]], list[list[float]], Any, list[str]]:
        fmtd_jobnets = Jobnet.format(jobnets)
        btms, lens = Jobnet.create_barh(fmtd_jobnets)
        ylbls = [joblist[next(iter(joblist))].name for joblist in jobnets.values()]
        yticks = np.arange(len(jobnets.keys()))
        return btms, lens, yticks, ylbls

    @staticmethod
    def map_bars(
        jbtms: list[list[float]],
        jlens: list[list[float]],
        sbtms: list[list[float]],
        slens: list[list[float]],
    ) -> list[list[int]]:

        max_jx = len(jbtms)
        max_sx = len(sbtms)
        max_y = len(jbtms[0])
        map_x: list[list[int]] = [[-1] * max_y for _ in range(max_jx)]
        map_dist: list[list[float]] = [[24.0] * max_y for _ in range(max_jx)]

        for y in range(max_y):

            for jx in range(max_jx):
                for sx in range(max_sx):
                    jbtm = jbtms[jx][y]
                    sbtm = sbtms[sx][y]
                    jlen = jlens[jx][y]
                    slen = slens[sx][y]
                    dist = math.fabs(jbtm - sbtm) + math.fabs(
                        (jbtm + jlen) - (sbtm + slen)
                    )
                    if dist < map_dist[jx][y]:
                        map_x[jx][y], map_dist[jx][y] = sx, dist

            for jx in range(max_jx - 1):
                if map_x[jx][y] == -1:
                    continue
                for kx in range(jx + 1, max_jx, 1):
                    if map_x[jx][y] != map_x[kx][y]:
                        continue
                    if map_dist[jx][y] > map_dist[kx][y]:
                        map_x[jx][y] = -1
                    else:
                        map_x[kx][y] = -1

        return map_x

    @staticmethod
    def create_colormap(
        jbtms: list[list[float]],
        jlens: list[list[float]],
        sbtms: list[list[float]],
        slens: list[list[float]],
        bar_map: list[list[int]],
    ) -> list[list[str]]:

        max_jx = len(jbtms)
        max_y = len(jbtms[0])
        clrs: list[list[str]] = [["b"] * max_y for _ in range(max_jx)]

        for x, col in enumerate(bar_map):
            for y, tgt in enumerate(col):
                if tgt == -1:
                    continue
                if (
                    jbtms[x][y] >= sbtms[tgt][y]
                    and jbtms[x][y] + jlens[x][y] <= sbtms[tgt][y] + slens[tgt][y]
                ):
                    clrs[x][y] = "b"
                else:
                    clrs[x][y] = "r"

        return clrs

    @staticmethod
    def show(jobnets: dict[str, dict[str, Jobnet]]):
        for joblist in jobnets.values():
            for job in joblist.values():
                print(vars(job))
