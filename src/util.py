import math
from datetime import datetime as dt

from chardet import detect


class Util:
    @staticmethod
    def datetime_to_hour(dt: dt) -> float:
        """hh:mm:ss → hh"""
        return dt.hour + dt.minute / 60 + dt.second / 3600

    @staticmethod
    def merge_range(*xranges: tuple[float, float]) -> tuple[float, float]:
        mn, mx = 24.0, 0.0
        for rng in xranges:
            if not rng:
                continue
            mn = min(mn, rng[0])
            mx = max(mx, rng[1])
        return mn, mx

    @staticmethod
    def integerize_range(xrange: tuple[float, float]) -> tuple[int, int]:
        return math.floor(xrange[0]), math.ceil(xrange[1])

    @staticmethod
    def detect_enc(path) -> str | None:
        with open(path, "rb") as f:
            b = f.read()
            e = detect(b)
            return e["encoding"]
