import asyncio
from dotenv import load_dotenv
from reaktiv import Computed, Signal, Effect
import pandas as p
import calibrations
from cmdl import get_pyproject, ArgumentParser
from views import render_task

from app import app

def main():
    pyproject = get_pyproject()
    args = ArgumentParser(pyproject["project"]).parse_args()

    load_dotenv(args.env_file)

    if args.hello:
        print("hello from haptgp!")

    if args.calibrate == "light":
        calibrations.calibrate_light()
        return
    app()


if __name__ == "__main__":
    main()
