import argparse

from jobnet import Jobnet


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--joblog", required=True, type=str)
    parser.add_argument("--schedule", type=str, default="schdule.csv")
    parser.add_argument("--output", type=str)
    return parser.parse_args()


def main():
    args = parse_arguments()
    jobnets = Jobnet.read_joblog(args.joblog)
    Jobnet.show_joblog(jobnets)
    print("\n")
    schedule = Jobnet.read_schedule(args.schedule)
    Jobnet.show_schedule(schedule)


if __name__ == "__main__":
    main()
