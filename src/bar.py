from __future__ import annotations

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
