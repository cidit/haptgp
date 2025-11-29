from dotenv import load_dotenv
from calib import calibrate_light
from cmdl import get_pyproject, ArgumentParser
from app import app


def main():
    pyproject = get_pyproject()
    args = ArgumentParser(pyproject["project"]).parse_args()
    load_dotenv(args.env_file)
    

    if args.hello:
        print("hello from haptgp!")
    if args.calibrate == "light":
        calibrate_light()
        return

    app()


if __name__ == "__main__":
    main()
