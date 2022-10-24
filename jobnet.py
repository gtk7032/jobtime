from __future__ import annotations

import csv
from datetime import datetime as dt
from typing import Optional

from util import Util


class Jobnet:

    START_MSG = "ジョブネットが開始しました。"
    END_MSG = "ジョブネットが終了しました。"

    def __init__(
        self,
        jobnetid: str,
        innerid: Optional[str],
        name: str,
        start: Optional[dt],
        end: Optional[dt],
    ):
        self.jobid = jobnetid
        self.inrid = innerid
        self.name = name
        self.start = start
        self.end = end

    def is_genuine(self) -> bool:
        return bool(self.start and self.end)

    def get_duration(self) -> float:
        return Util.cvrt_to_hour(self.end) - Util.cvrt_to_hour(self.start)

    @staticmethod
    def read_joblog(path: str) -> dict[str, dict[str, Jobnet]]:

        jobnets: dict[str, dict[str, Jobnet]] = {}

        with open(path, "r", encoding="utf-8") as f:

            reader = csv.DictReader(f)

            for row in reader:
                date = dt.strptime(row["log date"], "%Y/%m/%d %H:%M:%S.%f")
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

        now = dt.now()
        for joblist in jobnets.values():
            for job in joblist.values():
                if job.end is None:
                    job.end = now

        return Jobnet.align_order(jobnets)

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
                start = dt.strptime(row["start"], "%H:%M:%S")
                end = dt.strptime(row["end"], "%H:%M:%S")

                if jobid not in schedules.keys():
                    schedules[jobid] = {}

                schedules[jobid][inrid] = Jobnet(jobid, inrid, jobnm, start, end)

        return Jobnet.align_order(schedules)

    @staticmethod
    def align_order(
        jobnets: dict[str, dict[str, Jobnet]]
    ) -> dict[str, dict[str, Jobnet]]:

        for jn in jobnets.values():
            sjn = sorted(jn.items(), key=lambda x: Util.cvrt_to_hour(x[1].start))
            jn = {jobid: job for jobid, job in sjn}

        jobnets = sorted(
            jobnets.items(),
            key=lambda x: Util.cvrt_to_hour(x[1][next(iter(x[1]))].start),
        )
        return {jobid: jobnet for jobid, jobnet in jobnets}

    @staticmethod
    def show(jobnets: dict[str, dict[str, Jobnet]]):
        for joblist in jobnets.values():
            for job in joblist.values():
                print(vars(job))
