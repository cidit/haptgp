from tap import Tap
import tomllib
import asyncio
from dotenv import load_dotenv

def get_pyproject():
    with open("pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)
        return pyproject


class ArgumentParser(Tap):
    hello: bool = False
    env_file: str = ".env"

    def __init__(self, 
                 name: str, 
                 version: str, 
                 description: str, 
                 *args, 
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.description = f"""
            {name} v{version}
            {description}
        """

async def main():
    pyproject = get_pyproject()
    args = ArgumentParser(
        name=pyproject["project"]["name"],
        version=pyproject["project"]["version"],
        description=pyproject["project"]["description"],
    ).parse_args()
    
    load_dotenv(args.env_file)

    if args.hello:
        print("hello from haptgp!")
    
    while True:
        pass


if __name__ == "__main__":
    asyncio.run(main())
