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
    joblogs = Jobnet.read_joblog(args["joblog"])
    schedule = Jobnet.read_schedule(args["schedule"]) if args["schedule"] else {}
    xrange = Util.integerize_xrange(
        Util.merge_xrange(
            Jobnet.extract_xrange(joblogs),
            Jobnet.extract_xrange(schedule),
        )
    )

    Jobnet.complete(joblogs, schedule)
    sortedkeys = Jobnet.get_order(joblogs, schedule)
    jbtms, jlens, y, lbls = Jobnet.extract_plotdata(joblogs, sortedkeys)

    plotter = Plotter()
    plotter.set_canvas(y, lbls, xrange)
    if schedule:
        sbtms, slens, _, _ = Jobnet.extract_plotdata(schedule, sortedkeys)
        plotter.plot_barh(y + 0.4, slens, sbtms, "g", "予定時間")
    plotter.plot_barh(y, jlens, jbtms, "b", "実行時間")
    plotter.save(args["output"])


if __name__ == "__main__":
    main()
