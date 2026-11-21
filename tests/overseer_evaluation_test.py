

import sys
import json
sys.path.insert(1, "../311-Line-Project")
from evaluation import evaluate_overseer


def test_overseer_evaluation():

	##evaluate_overseer.test_overseer_evaluation()
	file = open("evaluation/evaluation_results/overseer_eval_results.md")

	def read_sixth_line():
		for i in range(6):
			line = file.readline()
			if i == 5:
				return line

	
	score_line = read_sixth_line()
	assert score_line == "- Average score: 1.00\n"

test_overseer_evaluation()
