# Codeforces Tool

Helps you download and test Codeforces problems, so that you can spend more time writing solutions and less time wrangling directories.

## Installation

### Build - Ubuntu

Required: Python 3.x.x
Highly recommended: `virtualenv`

1. `git clone <this repository>`
2. `cd <repository folder>`
3. `virtualenv env`
4. `source env/bin/activate`
5. `pip install -r pip-requirements.txt`
6. `sudo pyinstaller --onefile cf.py`
7. The binary is in the `dist/` folder.

### Use Pre-built Binary

Download `bin/cf` from this repository and put it on your `PATH` or executables directory.  Just on principle (and also it's simple), I would recommend building it yourself.

## Usage

Make the program executable and then run on the command line

`cf download <PROBLEM> <ID>`
