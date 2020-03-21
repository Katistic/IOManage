import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="iomanage",
    version="1.0.1",
    description="Manages IO operations of a single file",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Katistic/IOManage",
    author="Katistic",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["iomanage"],
    include_package_data=True,
)
