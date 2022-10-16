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
    def read_joblog(path: str) -> list[Jobnet]:

        jobnets = {}

        with open(path, "r", encoding="utf-8") as f:

            reader = csv.DictReader(f)

            for row in reader:
                date = dt.strptime(row["log date"], "%Y/%m/%d %H:%M:%S.%f")
                dictid = row["inner jobnet main id"]
                jobid = row["jobnet id"]
                msg = row["message"]
                name = row["jobnet name"]

                if msg == Jobnet.START_MSG:
                    jobnets[dictid] = Jobnet(jobid, name, date)

                elif msg == Jobnet.END_MSG and dictid in jobnets.keys():
                    jobnets[dictid].end = date

        now = dt.now()
        for job in jobnets.values():
            if job.end is None:
                job.end = now

        return sorted(list(jobnets.values()), key=lambda j: j.start)

    @staticmethod
    def read_schedule(path: str) -> dict[str, Jobnet]:

        schedules = {}

        with open(path, "r", encoding="utf-8") as f:

            reader = csv.DictReader(f)

            for row in reader:
                jobid = row["jobid"]
                jobnm = row["jobnm"]
                start = dt.strptime(row["start"], "%H:%M:%S")
                end = dt.strptime(row["end"], "%H:%M:%S")
                schedules[jobid] = Jobnet(jobid, jobnm, start, end)

        return schedules

    @staticmethod
    def show_joblog(jobnets: list[Jobnet]):
        for job in jobnets:
            print(vars(job))

    @staticmethod
    def show_schedule(jobnets: dict[str, Jobnet]):
        for job in jobnets.values():
            print(vars(job))
