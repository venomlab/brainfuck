import glob

from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="brainfuck-venomlab",
    version="0.1.0b1",
    packages=[path for path in glob.glob("brainfuck/**/", recursive=True) if "__pycache__" not in path],
    url="https://github.com/venomlab/brainfuck",
    license="MIT",
    download_url="https://github.com/venomlab/brainfuck/releases/tag/0.1.0",
    author="Dmitry Selishchev",
    author_email="zibertscrem@gmail.com",
    description="Brainfuck parser",
    keywords=["python", "brainfuck"],
    long_description_content_type="text/markdown",
    long_description=long_description,
    classifiers=[
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 4 - Beta",
    ],
    entry_points={
        "console_scripts": ["brainfuck=brainfuck.command_line:main_cli"],
    },
)
