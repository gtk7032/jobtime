from __future__ import annotations

import math

from job import Status


class Bar:
    def __init__(
        self, bottom: float, length: float, color: str, is_genuine: bool, status: Status
    ) -> None:
        self.bottom = bottom
        self.length = length
        self.color = color
        self.is_genuine = is_genuine
        self.status = status

    def is_within(self, bar: Bar) -> bool:
        return (
            self.bottom >= bar.bottom
            and self.bottom + self.length <= bar.bottom + bar.length
        )

    def dist_to(self, bar: Bar) -> float:
        return math.fabs(self.bottom - bar.bottom) + math.fabs(
            (self.bottom + self.length) - (bar.bottom + bar.length)
        )

    @staticmethod
    def dummy() -> Bar:
        return Bar(0.0, 0.0, "", False, Status.DEFAULT)

    @staticmethod
    def padding(bars: dict[str, list[Bar]]) -> dict[str, list[Bar]]:
        max_size = max(len(bar) for bar in bars.values())
        return {
            id: bar + [Bar.dummy() for _ in range(max_size - len(bar))]
            for id, bar in bars.items()
        }

    @staticmethod
    def transpose(bars: dict[str, list[Bar]]) -> list[list[Bar]]:
        max_x = len(next(iter(bars.values())))
        max_y = len(bars)
        t_bars: list[list[Bar]] = [[Bar.dummy()] * max_y for _ in range(max_x)]
        for y, bar in enumerate(bars.values()):
            for x, b in enumerate(bar):
                t_bars[x][y] = b
        return t_bars

    @staticmethod
    def map_bars(
        jbars: list[list[Bar]],
        sbars: list[list[Bar]],
    ) -> list[list[int]]:

        max_jx = len(jbars)
        max_sx = len(sbars)
        max_y = len(jbars[0])
        pair_x = [[-1] * max_y for _ in range(max_jx)]
        pair_dist = [[24.0] * max_y for _ in range(max_jx)]
        secured = [
            [not jbars[x][y].is_genuine for y in range(max_y)] for x in range(max_sx)
        ]

        def keep_mapping(y: int) -> bool:
            return bool(
                sum(not secured[sx][y] for sx in range(max_sx))
                and sum(pair_x[jx][y] == -1 for jx in range(max_jx))
            )

        for y in range(max_y):

            while keep_mapping(y):

                for jx in range(max_jx):
                    if pair_x[jx][y] != -1:
                        continue
                    for sx in range(max_sx):
                        if secured[sx][y]:
                            continue
                        d = jbars[jx][y].dist_to(sbars[sx][y])
                        if d < pair_dist[jx][y]:
                            pair_x[jx][y], pair_dist[jx][y] = sx, d

                for jx in range(max_jx):
                    if pair_x[jx][y] == -1:
                        continue
                    for kx in range(min(jx + 1, max_jx - 1), max_jx, 1):
                        if kx == jx or pair_x[jx][y] != pair_x[kx][y]:
                            continue
                        if pair_dist[jx][y] > pair_dist[kx][y]:
                            pair_x[jx][y] = -1
                        else:
                            pair_x[kx][y] = -1
                    if pair_x[jx][y] != -1:
                        secured[pair_x[jx][y]][y] = True

        return pair_x

    @staticmethod
    def colorize_with_schedule(
        jbars: list[list[Bar]],
        sbars: list[list[Bar]],
    ) -> list[list[Bar]]:
        pairs = Bar.map_bars(jbars, sbars)
        for x, col in enumerate(pairs):
            for y, tgt in enumerate(col):
                if tgt == -1:
                    continue
                if jbars[x][y].status not in [Status.RUNNING, Status.SUCCEED]:
                    continue
                if jbars[x][y].is_within(sbars[tgt][y]):
                    jbars[x][y].status = Status.IN_TIME
                else:
                    jbars[x][y].status = Status.OVERTIME
                jbars[x][y].color = Status.color(jbars[x][y].status)
        return jbars
