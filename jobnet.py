from __future__ import annotations

import csv
from datetime import datetime as dt
from typing import Tuple

import numpy as np

from util import Util


class Jobnet:

    START_MSG = "ジョブネットが開始しました。"
    END_MSG = "ジョブネットが終了しました。"

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

                if msg == Jobnet.START_MSG:
                    if jobid not in jobnets.keys():
                        jobnets[jobid] = {}
                    jobnets[jobid][innerid] = Jobnet(
                        jobid, innerid, name, date, None, True
                    )

                elif msg == Jobnet.END_MSG:
                    if jobid in jobnets.keys():
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
    def get_ordr(
        jobnets: dict[str, dict[str, Jobnet]],
    ) -> list[str]:
        s = sorted(jobnets.items(), key=lambda x: next(iter(x[1].values())).start)
        return [i[0] for i in s]

    @staticmethod
    def align_order(target: dict[str, dict[str, Jobnet]], orderedkeys: list[str]):
        return {key: target[key] for key in orderedkeys}

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
                        "min": job.start if job.isgenuine else 0.0,
                        "len": max(job.get_duration(), 5 / 60)
                        if job.isgenuine
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
                    "0": Jobnet(
                        aid, "0", next(iter(aval.values())).name, None, None, False
                    )
                }

    @staticmethod
    def get_glbordr(
        jobnets: dict[str, dict[str, Jobnet]],
        schedule: dict[str, dict[str, Jobnet]],
    ) -> list[str]:
        s = sorted(
            jobnets.items(),
            key=lambda x: next(iter(x[1].values())).start
            or next(iter(schedule[x[0]].values())).start,
        )
        return [i[0] for i in s]

    @staticmethod
    def extract_plotdata(jobnets):
        orderedkeys = Jobnet.get_ordr(jobnets)
        jobnets = Jobnet.align_order(jobnets, orderedkeys)
        fmtd_jobnets = Jobnet.format(jobnets)
        jbtms, jlens = Jobnet.create_barh(fmtd_jobnets)
        lbls = [joblist[next(iter(joblist))].name for joblist in jobnets.values()]
        y = np.arange(len(jobnets.keys()))
        return jbtms, jlens, y, lbls

    @staticmethod
    def extract_plotdata_with_schedule(jobnets, schedule):
        Jobnet.complete(jobnets, schedule)
        Jobnet.complete(schedule, jobnets)
        orderedkeys = Jobnet.get_glbordr(jobnets, schedule)
        jobnets = Jobnet.align_order(jobnets, orderedkeys)
        schedule = Jobnet.align_order(schedule, orderedkeys)
        fmtd_jobnets = Jobnet.format(jobnets)
        fmtd_schedule = Jobnet.format(schedule)
        jbtms, jlens = Jobnet.create_barh(fmtd_jobnets)
        s
        lbls = [joblist[next(iter(joblist))].name for joblist in jobnets.values()]
        y = np.arange(len(jobnets.keys()))
        return jbtms, jlens, y, lbls

    @staticmethod
    def show(jobnets: dict[str, dict[str, Jobnet]]):
        for joblist in jobnets.values():
            for job in joblist.values():
                print(vars(job))
