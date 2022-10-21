from jobnet import Jobnet
from util import Util


class Plotter:
    @staticmethod
    def format(
        jobnets: dict[str, dict[str, Jobnet]]
    ) -> dict[str, list[dict[str, float]]]:

        max_size = max(len(joblist) for joblist in jobnets.values())
        fmtd = {}

        for jobid, joblist in jobnets.items():

            fmtd[jobid] = [
                {"min": 0.0, "len": 0.0} for _ in range(max_size - len(joblist))
            ]
            fmtd[jobid].extend(
                [
                    {
                        "min": Util.cvrt_to_hour(job.start),
                        "len": Util.cvrt_to_hour(job.end) - Util.cvrt_to_hour(job.start)
                        if Util.cvrt_to_hour(job.end) - Util.cvrt_to_hour(job.start)
                        > (5 / 60)
                        else (5 / 60),
                    }
                    for job in joblist.values()
                ]
            )
        return fmtd

    @staticmethod
    def plot(
        jobnets: dict[str, dict[str, Jobnet]],
        schedule: dict[str, dict[str, Jobnet]],
        output: str,
        xrange: dict[str, str],
    ):
        fmt_jobnets = Plotter.format(jobnets)
        # print(fmt_jobnets)
        fmt_schedule = Plotter.format(schedule)
        # print(fmt_schedule)

        for i in range(len(next(iter(fmt_jobnets.values())))):
            btms = []
            lens = []
            y = []
            labels = []

            for jobid in fmt_jobnets.keys():
                btms.append(fmt_jobnets[jobid][i]["min"])
                lens.append(fmt_jobnets[jobid][i]["len"])
                labels.append(next(iter(jobnets[jobid].values())).name)

            print(btms)
            print("\n")
            print(lens)
            print("\n")
            print(labels)
