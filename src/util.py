import math
from datetime import datetime as dt


class Util:
    @staticmethod
    def datetime_to_hour(dt: dt) -> float:
        """hh:mm:ss → hh"""
        return dt.hour + dt.minute / 60 + dt.second / 3600

    @staticmethod
    def merge_xrange(*xranges: dict[str, float]) -> dict[str, float]:
        mn, mx = 24.0, 0.0
        for rng in xranges:
            if not rng:
                continue
            mn = min(mn, rng["min"])
            mx = max(mx, rng["max"])
        return {"min": mn, "max": mx}

    @staticmethod
    def integerize_xrange(xrange: dict[str, float]) -> dict[str, float]:
        return {"min": math.floor(xrange["min"]), "max": math.ceil(xrange["max"])}
