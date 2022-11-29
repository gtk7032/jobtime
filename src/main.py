import argparse
import os
import pathlib
from typing import Any

from jobmanager import JobnetManager
from plotter import Plotter
from util import Util


def parse_arguments() -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--joblog", required=True, type=str)
    parser.add_argument("--schedule", type=str)
    parser.add_argument("--output", type=str)
    parser.add_argument("--figsize", type=str)
    parser.add_argument("--show", type=str, default="false")
    args = parser.parse_args()
    return {
        "joblog": os.path.join("resources", args.joblog),
        "schedule": os.path.join("resources", args.schedule) if args.schedule else None,
        "output": os.path.join(
            "output",
            args.output or pathlib.Path(args.joblog).with_suffix(".svg"),
        ),
        "show": args.show.upper() == "TRUE",
        "figsize": tuple(int(fs) for fs in args.figsize.split(":"))
        if args.figsize
        else (16, 9),
    }


def main():
    args = parse_arguments()
    joblogs = JobnetManager.read_joblog(args["joblog"])
    schedules = (
        JobnetManager.read_schedule(args["schedule"])
        if args["schedule"]
        else JobnetManager()
    )
    xrange = Util.integerize_xrange(
        Util.merge_xrange(
            joblogs.xrange(),
            schedules.xrange(),
        )
    )

    yticks, ylbls = joblogs.extract_yticks(), joblogs.extract_ylabels()

    plotter = Plotter()
    plotter.set_canvas(yticks, ylbls, xrange, args["figsize"])

    if schedules.is_empty():
        plotter.plot_barh(
            yticks,
            joblogs.extract_bars(),
            {"b": "executed/executing", "r": "executed(error)"},
        )

    else:
        joblogs.set_status_by_schedule(schedules)
        schedules.complement_with(joblogs)
        schedules.sort_by_keys(joblogs.get_order())
        plotter.plot_barh(yticks + 0.2, schedules.extract_bars(), {"g": "scheduled"})
        plotter.plot_barh(
            yticks - 0.2,
            joblogs.extract_bars(),
            {"b": "executed(in time)/executing", "r": "executed(overtime/error)"},
        )

    plotter.save(args["output"], args["show"])


if __name__ == "__main__":
    main()
