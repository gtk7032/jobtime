from __future__ import annotations

import csv
import math
from datetime import datetime as dt
from enum import Flag, auto
from typing import Any, Tuple

import numpy as np

from plotter import Plotter
from util import Util


class Status(Flag):
    RUNNING = auto()
    SUCCEED = auto()
    FAILED = auto()
    DEFAULT = auto()


class Jobnet:

    START_MSG = ["ジョブネットが開始しました。", "Jobnet has started."]
    SUCCESSFUL_MSG = ["ジョブネットが終了しました。", "Jobnet has ended."]
    ERROR_MSG = ["ジョブが異常終了しました。", "Job failed."]

    def __init__(
        self,
        jobnetid: str,
        innerid: str,
        name: str,
        start: float | None,
        end: float | None,
        isgenuine: bool,
        status: Status,
    ):
        self.jobid = jobnetid
        self.inrid = innerid
        self.name = name
        self.start = start
        self.end = end
        self.isgenuine = isgenuine
        self.status = status

    def get_duration(self) -> float:
        return self.end - self.start

    @staticmethod
    def extract_xrange(jobnets: dict[str, dict[str, Jobnet]]) -> dict[str, float]:
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

                date = Util.datetime_to_hour(
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
                        jobid, innerid, name, date, None, True, Status.DEFAULT
                    )
                    continue

                if msg in Jobnet.SUCCESSFUL_MSG:
                    status = Status.SUCCEED
                elif msg in Jobnet.ERROR_MSG:
                    status = Status.FAILED
                else:
                    continue

                if jobid in jobnets.keys() and innerid in jobnets[jobid].keys():
                    jobnets[jobid][innerid].end = date
                    jobnets[jobid][innerid].status = status

        now = Util.datetime_to_hour(dt.now())
        for joblist in jobnets.values():
            for job in joblist.values():
                if job.end is None:
                    job.end = now
                if job.status == Status.DEFAULT:
                    job.status = Status.RUNNING

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
                start = Util.datetime_to_hour(dt.strptime(row["start"], "%H:%M:%S"))
                end = Util.datetime_to_hour(dt.strptime(row["end"], "%H:%M:%S"))

                if jobid not in schedules.keys():
                    schedules[jobid] = {}

                schedules[jobid][inrid] = Jobnet(
                    jobid, inrid, jobnm, start, end, True, Status.DEFAULT
                )

        return Jobnet.sort(schedules)

    @staticmethod
    def format(
        jobnets: dict[str, dict[str, Jobnet]]
    ) -> dict[str, list[dict[str, float]]]:

        max_size = max(len(joblist) for joblist in jobnets.values())
        fmtd = {}

        for jobid, joblist in jobnets.items():
            fmtd[jobid] = [
                {"btm": job.start, "len": max(job.get_duration(), 5 / 60)}
                if job.isgenuine
                else {"btm": 0.0, "len": 0.0}
                for job in joblist.values()
            ]
            fmtd[jobid].extend(
                [{"btm": 0.0, "len": 0.0} for _ in range(max_size - len(joblist))]
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
                        key,
                        "0",
                        next(iter(ref[key].values())).name,
                        None,
                        None,
                        False,
                        Status.DEFAULT,
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
        jobnets: dict[str, dict[str, Jobnet]], basecolor: str
    ) -> Tuple[list[list[float]], list[list[float]], Any, list[str], list[list[str]]]:
        fmtd_jobnets = Jobnet.format(jobnets)
        btms, lens = Jobnet.create_barh(fmtd_jobnets)
        ylbls = [joblist[next(iter(joblist))].name for joblist in jobnets.values()]
        yticks = np.arange(len(jobnets.keys()))
        clrmap = Jobnet.create_colormap_with_status(jobnets, basecolor)
        return btms, lens, yticks, ylbls, clrmap

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
        secured: list[list[bool]] = [[False] * max_y for _ in range(max_sx)]

        def dist(jx: int, sx: int, y: int) -> float:
            return math.fabs(jbtms[jx][y] - sbtms[sx][y]) + math.fabs(
                (jbtms[jx][y] + jlens[jx][y]) - (sbtms[sx][y] + slens[sx][y])
            )

        def keep_mapping(y: int) -> bool:
            return bool(
                len([secured[sx][y] for sx in range(max_sx) if not secured[sx][y]])
                and len([map_x[jx][y] for jx in range(max_jx) if map_x == -1])
            )

        for y in range(max_y):

            while keep_mapping(y):

                for jx in range(max_jx):
                    if map_x[jx][y] != -1:
                        continue
                    for sx in range(max_sx):
                        if secured[sx][y]:
                            continue
                        d = dist(jx, sx, y)
                        if d < map_dist[jx][y]:
                            map_x[jx][y], map_dist[jx][y] = sx, d

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
    def create_colormap_with_schedule(
        jbtms: list[list[float]],
        jlens: list[list[float]],
        sbtms: list[list[float]],
        slens: list[list[float]],
        bar_map: list[list[int]],
    ) -> list[list[str]]:

        max_jx = len(jbtms)
        max_y = len(jbtms[0])
        clrs: list[list[str]] = Plotter.create_single_colormap(max_jx, max_y, "b")

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
    def create_colormap_with_status(
        jobnets: dict[str, dict[str, Jobnet]], basecolor: str
    ) -> list[list[str]]:

        size_y = len(jobnets)
        size_x = max(len(jn) for jn in jobnets.values())
        clrmap = Plotter.create_single_colormap(size_x, size_y, basecolor)
        for y, jobnet in enumerate(jobnets.values()):
            for x, jn in enumerate(jobnet.values()):
                if jn.status == Status.FAILED:
                    clrmap[x][y] = "r"
        return clrmap

    @staticmethod
    def merge_colormap(fst: list[list[str]], snd: list[list[str]]) -> list[list[str]]:
        return [
            [f if f == "r" else s for f, s in zip(fcol, scol)]
            for fcol, scol in zip(fst, snd)
        ]

    @staticmethod
    def show(jobnets: dict[str, dict[str, Jobnet]]):
        for joblist in jobnets.values():
            for job in joblist.values():
                print(vars(job))
