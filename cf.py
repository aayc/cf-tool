import sys
import argparse
import requests
import bs4
import os
import webbrowser
import subprocess
import csv
from langref import getMultilineBeginComment, getMultilineEndComment
from cf_dl import CFDownloader

'''
Todo
Make support for google code jam
'''
NOTES_BEGIN_TOKEN = "----"

class CF:
	def __init__ (self):
		self.VERSION = 0.3
		parser = argparse.ArgumentParser(description="Codeforces Tool")
		parser.add_argument('command', help="subcommand to run")

		args = parser.parse_args(sys.argv[1:2])
		if not hasattr(self, args.command):
			print('Unrecognized command:', args.command)
			parser.print_help()
			exit(1)

		getattr(self, args.command)()

	def browse (self):
		parser = argparse.ArgumentParser(description="View Codeforces Problems")
		parser.add_argument("--div", help="Filter out other problems except this division")
		parser.add_argument("--tags", help="Filter out other tags except including these tags")
		parser.add_argument("--min-difficulty", type=int, help="Specify minimum difficulty - only applies to problems with a listed problem rating")
		parser.add_argument("--max-difficulty", type=int, help="Specify maximum difficulty - only applies to problems with a listed problem rating")
		args = parser.parse_args(sys.argv[2:])

		res = requests.get('http://codeforces.com/api/problemset.problems').json()
		if res["status"] != "OK":
			print("Unable to make request")
			exit(1)

		raw_problems = res["result"]["problems"]

		if args.tags:
			raw_problems = filter(lambda x: all([t.strip() in x["tags"] for t in args.tags.split(",")]), raw_problems)

		if args.div:
			raw_problems = filter(lambda x: x["index"] == args.div, raw_problems)

		if args.min_difficulty or args.max_difficulty:
			csv_data = requests.get("https://raw.githubusercontent.com/yjiao/codeforces-api/master/ui/problem_ratings.csv").content.decode("UTF-8")
			difficulty_ratings = list(csv.reader(csv_data.splitlines(), delimiter = ","))[1:]
			ratings = { (str(r[0]) + r[1]) : int(r[2]) for r in difficulty_ratings }

			if args.min_difficulty:	
				raw_problems = filter(lambda p: ratings.get(str(p["contestId"]) + p["index"], args.min_difficulty + 1) > args.min_difficulty, raw_problems)

			if args.max_difficulty:
				raw_problems = filter(lambda p: ratings.get(str(p["contestId"]) + p["index"], args.max_difficulty - 1) < args.max_difficulty, raw_problems)

		problems = list(raw_problems)
		choices = [p["name"] + " (" + str(p["contestId"]) + "/" + p["index"] + ") [" + ", ".join(p["tags"]) + "]" for p in problems]
		print("\n".join([str(i) + ": " + choices[i] for i in range(0, 10)]))

	def download (self):
		parser = argparse.ArgumentParser(description="Download a Codeforces problem")
		parser.add_argument("contestId", help="A number denoting the contest, e.g. '1011'")
		parser.add_argument("problemId", help="Also known as the division, e.g. 'A', 'B'")
		parser.add_argument("--lang", help="Preferred solution language", default="py")
		parser.add_argument("--web", nargs="?", help="Open in web browser?", const=True, default=False)
		parser.add_argument("--sol", help="Filename of solution file to create", default="solution")
		args = parser.parse_args(sys.argv[2:])

		downloader = CFDownloader()
		problem = downloader.download_problem(str(args.contestId), args.problemId)
		fpath = os.path.join(os.getcwd(), problem.id)

		if not os.path.isdir(fpath):
			os.makedirs(fpath)
			sol_fname = args.sol + "." + args.lang
			with open(os.path.join(fpath, sol_fname), "w+") as f:
				f.write(getMultilineBeginComment(args.lang) + "\n")
				f.write(problem.title + "\n\n")
				f.write(problem.statement + "\n\n")
				f.write(problem.input_spec + "\n\n")
				f.write(problem.output_spec + "\n\n")
				f.write("Tests\n")
				f.write("(In this directory), 'cf test " + problem.contest + " " + problem.division + " " + sol_fname + "'")
				f.write("\n" + getMultilineEndComment(args.lang))

			with open(os.path.join(fpath, "tests.in"), "w+") as f:
				for inputs, outputs in problem.test_cases:
					f.write("\n".join(inputs))
					f.write("\n\n")
				f.write(NOTES_BEGIN_TOKEN + "\n")
				f.write(problem.test_notes)

			with open(os.path.join(fpath, "tests.out"), "w+") as f:
				for inputs, outputs in problem.test_cases:
					f.write("\n".join(outputs))
					f.write("\n\n")
				f.write(NOTES_BEGIN_TOKEN + "\n")
				f.write(problem.test_notes)
		else:
			print("Folder " + fpath + " already exists. Aborting")
			exit(1)

		if args.web:
			webbrowser.open_new_tab("http://codeforces.com/problemset/problem/" + problem.contest + "/" + problem.division)

	def open(self):
		parser = argparse.ArgumentParser(description="Download a Codeforces problem")
		parser.add_argument("contestId", help="A number denoting the contest, e.g. '1011'")
		parser.add_argument("problemId", help="Also known as the division, e.g. 'A', 'B'")
		args = parser.parse_args(sys.argv[2:])

		webbrowser.open_new_tab("http://codeforces.com/problemset/problem/" + args.contestId + "/" + args.problemId)


	def test (self):
		parser = argparse.ArgumentParser(description="Download a Codeforces problem")
		parser.add_argument("--file", help="Solution filename'", default="solution.py")
		args = parser.parse_args(sys.argv[2:])

		fpath = os.path.join(os.getcwd(), args.file)
		ext = os.path.splitext(fpath)[1]

		with open("tests.in") as f:
			inputs = cullNotesFromTests([s.split("\n") for s in f.read().split("\n\n")])
		with open("tests.out") as f:
			outputs = cullNotesFromTests([s.split("\n") for s in f.read().split("\n\n")])

		test_cases = list(zip(inputs, outputs))
		test_results = []
		for i in range(0, len(test_cases)):
			test_case = test_cases[i]
			print(enhance_text("header", "---- TEST " + str(i) + " ----\n"))

			if ext == ".py":
				test_input = '\n'.join(test_case[0])
				test_output = '\n'.join(test_case[1])
				run_result = subprocess.run(['python', 'solution.py'], stdout=subprocess.PIPE, input=test_input.encode("utf-8"))
				output = run_result.stdout.decode("utf-8").strip()
				passed = output == test_output

				print("INPUT:\n" + test_input)
				print("OUTPUT EXPECTED:\n" + test_output)
				print("YOUR OUTPUT:\n" + output)
				print("PASS? " + (enhance_text("bold green", "YES!") if passed else enhance_text("bold fail", "NO")) + "\n")
				test_results.append(passed)
			else:
				print("Unsupported solution language :-/.  Aborting")
				exit(1)

		results_formatted = [enhance_text("bold green", s) if s == "PASS" else enhance_text("bold fail", s) for s in ["PASS" if r else "FAIL" for r in test_results]]
		print("RESULTS: " + ", ".join(results_formatted))

	def version (self):
		print("Version", self.VERSION)
		exit(1)


def enhance_text (c, s):
	endc = '\033[0m'
	enhancers = {
		"header" : '\033[95m',
		"blue" : '\033[94m',
		"green" : '\033[92m',
		"warning" : '\033[93m',
		"fail" : '\033[91m',
		"bold" :'\033[1m',
		"underline": '\033[4m'
	}
	return "".join([enhancers[color] for color in c.split(" ")]) + s + endc

def cullNotesFromTests (ls):
	for i in range(0, len(ls)):
		print(ls[i][0])
		if ls[i][0] == NOTES_BEGIN_TOKEN:
			return ls[0:i]

if __name__ == "__main__":
	CF()
	
