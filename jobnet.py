from __future__ import annotations

import csv
from datetime import datetime as dt


class Jobnet:

    START_MSG = "ジョブネットが開始しました。"
    END_MSG = "ジョブネットが終了しました。"

    def __init__(self, id: str, name: str, start: dt = None, end: dt = None):
        self.id = id
        self.name = name
        self.start = start
        self.end = end

    @staticmethod
    def read_joblog(path: str) -> dict[str, list[Jobnet]]:

        jobnets: dict[str, list[Jobnet]] = {}

        with open(path, "r", encoding="utf-8") as f:

            reader = csv.DictReader(f)

            for row in reader:
                date = dt.strptime(row["log date"], "%Y/%m/%d %H:%M:%S.%f")
                jobid = row["jobnet id"]
                msg = row["message"]
                name = row["jobnet name"]
                jobnet = Jobnet(jobid, name, date)

                if msg == Jobnet.START_MSG:
                    if jobid in jobnets.keys():
                        jobnets[jobid].append(jobnet)
                    else:
                        jobnets[jobid] = [jobnet]

                elif msg == Jobnet.END_MSG:
                    if jobid in jobnets.keys():
                        jobnets[jobid][-1].end = date
                    else:
                        pass

        now = dt.now()
        for joblist in jobnets.values():
            for job in joblist:
                if job.end is None:
                    job.end = now

        jobnets = sorted(jobnets.items(), key=lambda j: j[1][0].start)
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
                jobnet = Jobnet(jobid, jobnm, start, end)
                if jobid in schedules:
                    schedules[jobid].append(jobnet)
                else:
                    schedules[jobid] = [jobnet]

        return schedules

    @staticmethod
    def show_joblog(jobnets: dict[str, list[Jobnet]]):
        for joblist in jobnets.values():
            for job in joblist:
                print(vars(job))

    @staticmethod
    def show_schedule(jobnets: dict[str, list[Jobnet]]):
        for joblist in jobnets.values():
            for job in joblist:
                print(vars(job))
