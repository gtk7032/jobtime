import argparse
import os
import pathlib
from typing import Any

from jobnet import Jobnet
from plotter import Plotter
from util import Util


def parse_arguments() -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--joblog", required=True, type=str)
    parser.add_argument("--schedule", type=str)
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    return {
        "joblog": os.path.join("resources", args.joblog),
        "schedule": os.path.join("resources", args.schedule) if args.schedule else None,
        "output": os.path.join(
            "output",
            args.output or pathlib.Path(args.joblog).with_suffix(".png"),
        ),
    }


def main():
    args = parse_arguments()
    jobnets = Jobnet.read_joblog(args["joblog"])
    schedule = Jobnet.read_schedule(args["schedule"]) if args["schedule"] else {}
    xrange = Util.integerize_xrange(
        Util.merge_xrange(
            Jobnet.extract_xrange(jobnets),
            Jobnet.extract_xrange(schedule),
        )
    )
    if schedule:
        Plotter.plot_with_schedule(
            jobnets,
            schedule,
            args["output"],
            xrange,
        )
    else:
        Plotter.plot(
            jobnets,
            args["output"],
            xrange,
        )


if __name__ == "__main__":
    main()
