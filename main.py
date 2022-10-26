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
    parser.add_argument("--schedule", type=str, default="schdule.csv")
    parser.add_argument("--output", type=str)
    parser.add_argument("--xrange", type=str)
    args = parser.parse_args()

    mn, mx = args.xrange.split("-") if args.xrange else None, None
    rng = {"min": float(mn), "max": float(mx)} if mn and mx else None

    return {
        "joblog": os.path.join("resources", args.joblog),
        "schedule": os.path.join("resources", args.schedule),
        "output": os.path.join(
            "output",
            args.output or pathlib.Path(args.joblog).with_suffix(".png"),
        ),
        "xrange": (dict(zip(["min", "max"], rng)) if rng else None),
    }


def main():
    args = parse_arguments()
    jobnets = Jobnet.read_joblog(args["joblog"])
    schedule = Jobnet.read_schedule(args["schedule"])
    xrange = Util.integerize_xrange(
        Util.merge_xrange(
            Jobnet.extract_xrange(jobnets),
            Jobnet.extract_xrange(schedule),
            args["xrange"],
        )
    )

    Plotter.plot(
        jobnets,
        schedule,
        args["output"],
        xrange,
    )


if __name__ == "__main__":
    main()
