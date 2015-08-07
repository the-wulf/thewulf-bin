import os.path
from setuptools import setup, find_packages

def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as _f:
        contents = _f.read()
    return contents

setup(
    name="thewulf-bin",
    version="0.1",
    author="andrew young",
    author_email="ayoung@thewulf.org",
    description="commandline utilities for automating archive related tasks",
    keywords="backlight",
    long_description=read("README.md"),
    packages=find_packages(exclude=["tests", "tests.*"]),
    test_suite="tests",
    entry_points={
        "console_scripts": [
            "join_video = thewulf_bin.scripts.join_video:run",
            "transfer_video = thewulf_bin.scripts.transfer_video:run"
            "check_card = thewulf_bin.scripts.parse_card:run"
        ]
    }
)
