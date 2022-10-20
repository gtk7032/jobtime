from datetime import datetime as dt


class Util:
    @staticmethod
    def cvrt_to_hour(dt: dt) -> float:
        """hh:mm:ss → hh"""
        return dt.hour + dt.minute / 60 + dt.second / 3600
