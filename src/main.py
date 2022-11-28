import argparse
import os
import pathlib
from typing import Any

from bar import Bar
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

    jbars, yticks, ylbls = joblogs.extract_plotdata()

    plotter = Plotter()
    plotter.set_canvas(yticks, ylbls, xrange, args["figsize"])

    if not schedules.is_empty():
        schedules.complement_with(joblogs)
        schedules.sort_by_keys(joblogs.get_order())
        sbars, _, _ = schedules.extract_plotdata()
        plotter.plot_barh(yticks + 0.2, sbars, {"g": "scheduled"})
        plotter.plot_barh(
            yticks - 0.2,
            Bar.colorize_with_schedule(jbars, sbars),
            {"b": "executed(in time)/executing", "r": "executed(overtime/error)"},
        )
    else:
        plotter.plot_barh(
            yticks, jbars, {"b": "executed/executing", "r": "executed(error)"}
        )

    plotter.save(args["output"], args["show"])


if __name__ == "__main__":
    main()
