from pathlib import Path


def home_dir():
    return str(Path.home())


if __name__ == "__main__":
    print(home_dir())
