import math
from datetime import datetime as dt


class Util:
    @staticmethod
    def datetime_to_hour(dt: dt) -> float:
        """hh:mm:ss → hh"""
        return dt.hour + dt.minute / 60 + dt.second / 3600

    @staticmethod
    def merge_xrange(*xranges: tuple[float, float]) -> tuple[float, float]:
        mn, mx = 24.0, 0.0
        for rng in xranges:
            if not rng:
                continue
            mn = min(mn, rng[0])
            mx = max(mx, rng[1])
        return mn, mx

    @staticmethod
    def integerize_xrange(xrange: tuple[float, float]) -> tuple[int, int]:
        return math.floor(xrange[0]), math.ceil(xrange[1])
