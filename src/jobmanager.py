from __future__ import annotations

from csv import DictReader
from datetime import datetime as dt

from bar import Bar
from job import Job, Status
from jobnet import Jobnet
from util import Util


class JobnetManager:
    def __init__(self) -> None:
        self.jobnets: dict[str, Jobnet] = {}

    def has(self, jnid: str) -> bool:
        return jnid in self.jobnets

    def add(self, jobnet: Jobnet) -> None:
        self.jobnets[jobnet.id] = jobnet

    def is_empty(self) -> bool:
        return not bool(self.jobnets)

    def sort(self) -> None:
        for jobnet in self.jobnets.values():
            jobnet.sort()
        self.jobnets = {
            jobnetid: jobnet
            for jobnetid, jobnet in sorted(
                self.jobnets.items(), key=lambda jobnet: jobnet[1].head().start
            )
        }

    def xrange(self) -> tuple[float, float]:
        _min, _max = 24.0, 0.0
        for jn in self.jobnets.values():
            mn, mx = jn.xrange()
            _min = min(_min, mn)
            _max = max(_max, mx)
        return _min, _max

    @staticmethod
    def read_joblog(path: str) -> JobnetManager:

        manager = JobnetManager()

        with open(path, "r", encoding="utf-8") as f:

            reader = DictReader(f)

            for row in reader:

                date = Util.datetime_to_hour(
                    dt.strptime(row["log date"], "%Y/%m/%d %H:%M:%S.%f")
                )
                jobnetid = row["jobnet id"]
                innerid = row["inner jobnet id"]
                msg = row["message"]
                name = row["jobnet name"]

                if msg in Job.START_MSG:
                    if not manager.has(jobnetid):
                        manager.add(Jobnet(jobnetid, name))
                    if not manager.jobnets[jobnetid].has(innerid):
                        manager.jobnets[jobnetid].add(Job(innerid, True, date))
                    continue

                if msg in Job.SUCCESSFUL_MSG:
                    status = Status.SUCCEED
                elif msg in Job.ERROR_MSG:
                    status = Status.FAILED
                else:
                    continue

                if manager.has(jobnetid) and manager.jobnets[jobnetid].has(innerid):
                    manager.jobnets[jobnetid].jobs[innerid].end = date
                    manager.jobnets[jobnetid].jobs[innerid].status = status

        now = Util.datetime_to_hour(dt.now())
        for jobnet in manager.jobnets.values():
            for job in jobnet.jobs.values():
                if not job.end:
                    job.end = now
                if job.status == Status.DEFAULT:
                    job.status = Status.RUNNING

        manager.sort()
        return manager

    @staticmethod
    def read_schedule(path: str) -> JobnetManager:

        manager = JobnetManager()

        with open(path, "r", encoding="utf-8") as f:

            reader = DictReader(f)

            for row in reader:
                jobid = row["jobid"]
                inrid = (
                    str(len(manager.jobnets[jobid].jobs)) if manager.has(jobid) else "0"
                )
                jobnm = row["jobnm"]
                start = Util.datetime_to_hour(dt.strptime(row["start"], "%H:%M:%S"))
                end = Util.datetime_to_hour(dt.strptime(row["end"], "%H:%M:%S"))

                if not manager.has(jobid):
                    manager.add(Jobnet(jobid, jobnm))

                manager.jobnets[jobid].add(Job(inrid, True, start, end))

        manager.sort()
        return manager

    def to_bars(self) -> dict[str, list[Bar]]:
        return {
            jobnetid: [job.to_bar() for job in jobnet.jobs.values()]
            for jobnetid, jobnet in self.jobnets.items()
        }

    def complement_with(self, ref: JobnetManager) -> None:

        if self.is_empty() or ref.is_empty():
            return

        # delete if not exists in ref
        self.jobnets = {k: v for k, v in self.jobnets.items() if ref.has(k)}

        # drain ref
        self.jobnets.update(
            {k: Jobnet(k, ref.jobnets[k].name) for k in ref.jobnets if not self.has(k)},
        )

    def get_order(self) -> list[str]:
        return [s for s in self.jobnets]

    def sort_by_keys(self, keys: list[str]) -> None:
        if self.jobnets and keys:
            self.jobnets = {key: self.jobnets[key] for key in keys}

    def extract_bars(self) -> list[list[Bar]]:
        return Bar.transpose(Bar.padding(self.to_bars()))

    def extract_ylabels(self) -> list[str]:
        return [jobnet.name for jobnet in self.jobnets.values()]

    def extract_yticks(self) -> list[int]:
        return list(range(len(self.jobnets)))

    def mapping(self, schedule: JobnetManager) -> dict[str, list[int]]:

        pair_x = {jn.id: [-1] * jn.size() for jn in self.jobnets.values()}
        pair_dist = {jn.id: [24.0] * jn.size() for jn in self.jobnets.values()}
        secured = {
            jn.id: [not job.is_genuine for job in jn.jobs.values()]
            for jn in schedule.jobnets.values()
        }

        def clear(jobnetid: str, x: int) -> None:
            pair_x[jobnetid][x] = -1
            pair_dist[jobnetid][x] = 24.0

        def keep_mapping(jobnetid: str) -> bool:
            return bool(
                sum(not col for col in secured[jobnetid])
                and sum(
                    pair_x[jobnetid][jx] == -1
                    for jx in range(self.jobnets[jobnetid].size())
                )
            )

        for jobnet in self.jobnets.values():

            if schedule.jobnets[jobnet.id].is_empty():
                continue

            while keep_mapping(jobnet.id):

                for jx, job in enumerate(jobnet.jobs.values()):
                    if pair_x[jobnet.id][jx] != -1:
                        continue
                    for sx, sch in enumerate(schedule.jobnets[jobnet.id].jobs.values()):
                        if secured[jobnet.id][sx]:
                            continue
                        d = job.dist_to(sch)
                        if d < pair_dist[jobnet.id][jx]:
                            pair_x[jobnet.id][jx], pair_dist[jobnet.id][jx] = sx, d

                for jx, job in enumerate(jobnet.jobs.values()):
                    if pair_x[jobnet.id][jx] == -1:
                        continue
                    for kx in range(min(jx + 1, jobnet.size() - 1), jobnet.size(), 1):
                        if jx == kx or pair_x[jobnet.id][jx] != pair_x[jobnet.id][kx]:
                            continue
                        if pair_dist[jobnet.id][jx] > pair_dist[jobnet.id][kx]:
                            clear(jobnet.id, jx)
                        else:
                            clear(jobnet.id, kx)
                    if pair_x[jobnet.id][jx] != -1:
                        secured[jobnet.id][pair_x[jobnet.id][jx]] = True

        return pair_x

    def set_status_by_schedule(self, schedules: JobnetManager) -> None:

        pair_x = self.mapping(schedules)

        for jobnet in self.jobnets.values():
            for x, job in enumerate(jobnet.jobs.values()):
                if pair_x[jobnet.id][x] == -1:
                    continue
                if job.status != Status.SUCCEED:
                    continue
                if job.is_within(
                    schedules.jobnets[jobnet.id].jobs[
                        schedules.jobnets[jobnet.id].index_to_key(pair_x[jobnet.id][x])
                    ]
                ):
                    job.status = Status.INTIME
                else:
                    job.status = Status.OVERTIME
