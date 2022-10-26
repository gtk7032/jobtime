from __future__ import annotations

import csv
from datetime import datetime as dt

from util import Util


class Jobnet:

    START_MSG = "ジョブネットが開始しました。"
    END_MSG = "ジョブネットが終了しました。"

    def __init__(
        self,
        jobnetid: str,
        innerid: str | None,
        name: str,
        start: float | None,
        end: float | None,
    ):
        self.jobid = jobnetid
        self.inrid = innerid
        self.name = name
        self.start = start
        self.end = end

    def is_genuine(self) -> bool:
        return self.start is not None and self.end is not None

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
                    jobnets[jobid][innerid] = Jobnet(jobid, innerid, name, date, None)

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

                schedules[jobid][inrid] = Jobnet(jobid, inrid, jobnm, start, end)

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
    def show(jobnets: dict[str, dict[str, Jobnet]]):
        for joblist in jobnets.values():
            for job in joblist.values():
                print(vars(job))
