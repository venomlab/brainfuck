import glob

from setuptools import setup

setup(
    name="brainfuck",
    version="0.1.0",
    packages=[path for path in glob.glob("brainfuck/**/", recursive=True) if "__pycache__" not in path],
    url="https://github.com/venomlab/brainfuck",
    license="MIT",
    author="Dmitry Selishchev",
    author_email="zibertscrem@gmail.com",
    description="Brainfuck parser",
    keywords=["python", "brainfuck"],
    classifiers=[
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 4 - Beta",
    ],
    entry_points={
        "console_scripts": ["brainfuck=brainfuck.command_line:main_cli"],
    },
)
