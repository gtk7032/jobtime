import argparse


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--joblog", required=True, type=str)
    parser.add_argument("--schedule", type=str, default="schdule.csv")
    parser.add_argument("--output", type=str)
    return parser.parse_args()


def main():
    args = parse_arguments()
    print(args.output)


if __name__ == "__main__":
    main()
