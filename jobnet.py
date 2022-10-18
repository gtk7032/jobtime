from __future__ import annotations

import csv
from datetime import datetime as dt
from typing import Optional


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

        jobnets = sorted(jobnets.items(), key=lambda j: j[1][next(iter(j[1]))].start)

        return {jobid: jobnet for jobid, jobnet in jobnets}

    @staticmethod
    def read_schedule(path: str) -> dict[str, list[Jobnet]]:

        schedules: dict[str, list[Jobnet]] = {}

        with open(path, "r", encoding="utf-8") as f:

            reader = csv.DictReader(f)

            for row in reader:
                jobid = row["jobid"]
                jobnm = row["jobnm"]
                start = dt.strptime(row["start"], "%H:%M:%S")
                end = dt.strptime(row["end"], "%H:%M:%S")
                jobnet = Jobnet(jobid, None, jobnm, start, end)

                if jobid in schedules.keys():
                    schedules[jobid].append(jobnet)
                else:
                    schedules[jobid] = [jobnet]

        for slist in schedules.values():
            slist = sorted(slist, key=lambda x: x.start)

        return schedules

    @staticmethod
    def show_joblog(jobnets: dict[str, dict[str, Jobnet]]):
        for joblist in jobnets.values():
            for job in joblist.values():
                print(vars(job))

    @staticmethod
    def show_schedule(jobnets: dict[str, list[Jobnet]]):
        for joblist in jobnets.values():
            for job in joblist:
                print(vars(job))
