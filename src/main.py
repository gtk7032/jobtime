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
    joblogs = Jobnet.read_joblog(args["joblog"])
    schedule = Jobnet.read_schedule(args["schedule"]) if args["schedule"] else {}
    xrange = Util.integerize_xrange(
        Util.merge_xrange(
            Jobnet.extract_xrange(joblogs),
            Jobnet.extract_xrange(schedule),
        )
    )

    jbtms, jlens, yticks, ylbls, jclrs = Jobnet.extract_plotdata(joblogs, "b")

    plotter = Plotter()
    plotter.set_canvas(yticks, ylbls, xrange, args["figsize"])

    if schedule:
        schedule = Jobnet.complement(schedule, joblogs)
        schedule = Jobnet.sortby_givenkeys(schedule, Jobnet.get_order(joblogs))
        sbtms, slens, _, _, sclrs = Jobnet.extract_plotdata(schedule, "g")
        plotter.plot_barh(yticks + 0.2, slens, sbtms, sclrs, {"g": "scheduled"})

    plotter.plot_barh(
        yticks - 0.2 if schedule else yticks,
        jlens,
        jbtms,
        Jobnet.merge_colormap(
            jclrs,
            Jobnet.create_colormap_with_schedule(
                jbtms, jlens, sbtms, slens, Jobnet.map_bars(jbtms, jlens, sbtms, slens)
            ),
        )
        if schedule
        else jclrs,
        {"b": "executed(in time)/executing", "r": "executed(overtime/error)"}
        if schedule
        else {"b": "executed/executing", "r": "executed(error)"},
    )
    plotter.save(args["output"], args["show"])


if __name__ == "__main__":
    main()
