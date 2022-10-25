from datetime import datetime as dt


class Util:
    @staticmethod
    def cvrt_to_hour(dt: dt) -> float:
        """hh:mm:ss → hh"""
        return dt.hour + dt.minute / 60 + dt.second / 3600

    @staticmethod
    def merge_xrange(fst: dict[str, float], scd: dict[str, float]):
        if not fst and not scd:
            return None
        elif not fst:
            return scd
        elif not scd:
            return fst
        else:
            return {
                "min": min(fst["min"], scd["min"]),
                "max": max(fst["max"], scd["max"]),
            }
