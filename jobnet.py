from __future__ import annotations

import csv
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
    def complete(
        fst: dict[str, dict[str, Jobnet]], scd: dict[str, dict[str, Jobnet]]
    ) -> None:

        if not fst or not scd:
            return

        keys = fst.keys() | scd.keys()
        for key in keys:
            if key not in fst.keys():
                fst[key] = {
                    "0": Jobnet(
                        key, "0", next(iter(scd[key].values())).name, None, None, False
                    )
                }
            elif key not in scd.keys():
                scd[key] = {
                    "0": Jobnet(
                        key, "0", next(iter(fst[key].values())).name, None, None, False
                    )
                }

    @staticmethod
    def get_order(
        joblogs: dict[str, dict[str, Jobnet]],
        schedule: dict[str, dict[str, Jobnet]],
    ) -> list[str]:
        s = sorted(
            joblogs.items(),
            key=lambda x: next(iter(x[1].values())).start
            if next(iter(x[1].values())).isgenuine
            else next(iter(schedule[x[0]].values())).start,
        )
        return [i[0] for i in s]

    @staticmethod
    def sortby_givenkeys(
        jobnets: dict[str, dict[str, Jobnet]], keys: list[str]
    ) -> dict[str, dict[str, Jobnet]]:
        if keys:
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
        jobnets,
    ) -> Tuple[list[list[float]], list[list[float]], Any, list[str]]:
        fmtd_jobnets = Jobnet.format(jobnets)
        btms, lens = Jobnet.create_barh(fmtd_jobnets)
        ylbls = [joblist[next(iter(joblist))].name for joblist in jobnets.values()]
        yticks = np.arange(len(jobnets.keys()))
        return btms, lens, yticks, ylbls

    @staticmethod
    def show(jobnets: dict[str, dict[str, Jobnet]]):
        for joblist in jobnets.values():
            for job in joblist.values():
                print(vars(job))
