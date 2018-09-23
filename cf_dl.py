from bs4 import BeautifulSoup
import requests


class CFDownloader:
	def __init__ (self):
		pass

	def download_problem (self, contestId, problemId):
		url = 'http://codeforces.com/problemset/problem/' + contestId + "/" + problemId
		html_doc = requests.get(url).content
		soup = BeautifulSoup(html_doc, 'html.parser')
		statement = soup.find("div", { "class": "problem-statement"})
		problem = CFProblem(contestId, problemId, statement)
		return problem

class CFProblem:
	def __init__ (self, contestId, problemId, statement_soup):
		problem = statement_soup
		self.id = contestId + problemId
		self.contest = contestId
		self.division = problemId
		self.time_limit = ''.join(problem.find("div", { "class": "time-limit"}).contents[1])
		self.memory_limit = ''.join(problem.find("div", { "class": "memory-limit"}).contents[1])
		self.input_method = ''.join(problem.find("div", { "class": "input-file"}).contents[1])
		self.output_method = ''.join(problem.find("div", { "class": "output-file"}).contents[1])
		
		self.title = problem.find("div", { "class": "title" }).text
		raw_statement = problem.find("div", { "class": "header" }).next_sibling.contents
		self.statement = '\n\n'.join([self.unformatMathjax(elem.text) for elem in raw_statement])

		# This does not support "Interactive" problems.
		# In the future, replace input_spec, output_spec with a full download until tests.
		raw_input_spec = '\n'.join(list(map(lambda x: x.text, problem.find("div", {"class": "input-specification"}).contents)))
		self.input_spec = self.unformatMathjax(raw_input_spec)
		raw_output_spec = '\n'.join(list(map(lambda x: x.text, problem.find("div", {"class": "output-specification"}).contents)))
		self.output_spec = self.unformatMathjax(raw_output_spec)

		if problem.find("div", {"class": "note"}):
			self.test_notes = "\n".join(list(map(lambda x: x.text, problem.find("div", {"class": "note"}).contents)))

		sample_tests = problem.find("div", {"class": "sample-test"})
		input_divs = sample_tests.findAll("div", {"class": "input"})
		inputs = [list(filter(lambda x: isinstance(x, (str)), tag.find("pre").contents)) for tag in input_divs]
		output_divs = sample_tests.findAll("div", {"class": "output"})
		outputs = [list(filter(lambda x: isinstance(x, (str)), tag.find("pre").contents)) for tag in output_divs]
		self.test_cases = list(zip(inputs, outputs))

	def unformatMathjax (self, s):
		part1 = s.replace("$$$", "").replace("\\le", "<").replace("\\gt", ">")
		part2 = part1.replace("\rightarrow", "->").replace("\leftarrow", "<-")
		return part2


