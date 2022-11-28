from __future__ import annotations

from typing import Tuple

from job import Job


class Jobnet:
    def __init__(self, jobnetid: str, name: str):
        self.id = jobnetid
        self.name = name
        self.jobs: dict[str, Job] = {}

    def xrange(self) -> Tuple[float, float]:
        mn, mx = 24.0, 0.0
        for job in self.jobs.values():
            mn = min(mn, job.start)
            mx = max(mx, job.end)
        return mn, mx

    def add(self, job: Job) -> None:
        self.jobs[job.inrid] = job

    def has(self, key: str) -> bool:
        return key in self.jobs.keys()

    def sort_jobs(self) -> None:
        self.jobs = {
            id: job
            for id, job in sorted(
                self.jobs.items(),
                key=lambda job: job[1].start,
            )
        }

    def head(self) -> Job:
        return next(iter(self.jobs.values()))

    def size(self) -> int:
        return len(self.jobs)

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
