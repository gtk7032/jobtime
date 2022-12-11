from __future__ import annotations

from typing import Tuple

from bar import Bar
from job import Job


class Jobnet:
    def __init__(self, jobnetid: str, name: str):
        self.id = jobnetid
        self.name = name
        self.jobs: dict[str, Job] = {}

    def range(self) -> Tuple[float, float]:
        mn, mx = 24.0, 0.0
        for job in self.jobs.values():
            mn = min(mn, job.start)
            mx = max(mx, job.end)
        return mn, mx

    def add(self, job: Job) -> None:
        self.jobs[job.inrid] = job

    def has(self, key: str) -> bool:
        return key in self.jobs.keys()

    def is_empty(self) -> bool:
        return not bool(self.jobs)

    def index_to_key(self, index: int) -> str:
        for i, job in enumerate(self.jobs.values()):
            if i == index:
                return job.inrid
        return ""

    def sort(self) -> None:
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

    def to_bars(self) -> list[Bar]:
        return [job.to_bar() for job in self.jobs.values()]

    def show(self):
        for jn in self.jobs.values():
            print(vars(jn))
