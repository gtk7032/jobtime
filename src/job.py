from enum import Flag, auto

from bar import Bar


class Status(Flag):
    RUNNING = auto()
    SUCCEED = auto()
    FAILED = auto()
    IN_TIME = auto()
    OVERTIME = auto()
    DEFAULT = auto()

    __BLUE = [RUNNING, SUCCEED, IN_TIME]
    __RED = [FAILED, OVERTIME]
    __GREEN = [DEFAULT]

    @classmethod
    def color(cls, status) -> str:
        if status in cls.__BLUE:
            return "b"
        elif status in cls.__RED:
            return "r"
        else:
            return "b"


class Job:

    START_MSG = ["ジョブネットが開始しました。", "Jobnet has started."]
    SUCCESSFUL_MSG = ["ジョブネットが終了しました。", "Jobnet has ended."]
    ERROR_MSG = ["ジョブが異常終了しました。", "Job failed."]

    def __init__(
        self,
        id: str,
        is_genuine: bool,
        start: float = 0.0,
        end: float = 0.0,
    ):
        self.inrid = id
        self.is_genuine = is_genuine
        self.start = start
        self.end = end
        self.status = Status.DEFAULT

    def duration(self) -> float:
        return self.end - self.start

    def to_bar(self) -> Bar:
        return (
            Bar(
                self.start,
                max(self.duration(), 5 / 60),
                Status.color(self.status),
                True,
                self.status,
            )
            if self.is_genuine
            else Bar.dummy()
        )
