
import pathlib
from setuptools import find_packages, setup

import graph_crdt

HERE = pathlib.Path(__file__).parent
README = (HERE / 'README.md').read_text()

setup(
    name="graph_crdt",
    version="1.0.0",
    description="A portable on-memory conflict-free replicated graph database",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/vndee/grpah-crdt",
    author="Duy Huynh",
    author_email="vndee.huynh@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=("example", "test", "graph_crdt")),
    include_package_data=True,
    install_requires=['requests'],
)
