import argparse
import os
from typing import Any

from jobnet import Jobnet
from plotter import Plotter


def parse_arguments() -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--joblog", required=True, type=str)
    parser.add_argument("--schedule", type=str, default="schdule.csv")
    parser.add_argument("--output", type=str)
    parser.add_argument("--xrange", type=str)
    args = parser.parse_args()

    return {
        "joblog": os.path.join("resources", args.joblog),
        "schedule": os.path.join("resources", args.schedule),
        "output": os.path.join(
            "resources",
            args.output
            if args.output is not None
            else args.joblog.split(".")[-2] + ".png",
        ),
        "xrange": (
            dict(zip(["min", "max"], args.xrange.split("-")))
            if args.xrange is not None
            else None
        ),
    }


def main():
    args = parse_arguments()
    jobnets = Jobnet.read_joblog(args["joblog"])
    # Jobnet.show(jobnets)
    # print("\n")
    schedule = Jobnet.read_schedule(args["schedule"])
    # Jobnet.show(schedule)
    Plotter.plot(jobnets, schedule, args["output"], args["xrange"])


if __name__ == "__main__":
    main()
