from tap import Tap


def get_pyproject():
    import tomllib
    with open('pyproject.toml', 'rb') as f:
        pyproject = tomllib.load(f)
        return pyproject


class ArgumentParser(Tap):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pyproject = get_pyproject()
        self.description = f"""{pyproject["project"]["name"]} v{pyproject["project"]["version"]}
                            {pyproject["project"]["description"]}
                            """
    hello: bool = False


def main():
    
    args = ArgumentParser().parse_args()
    
    if args.hello:
        print("hello from haptgp!")
        
    while True:
        pass


if __name__ == "__main__":
    main()
