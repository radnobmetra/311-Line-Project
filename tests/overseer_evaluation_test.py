

import sys
sys.path.insert(1, "../311-Line-Project")
import subprocess

def test_overseer_evaluation():
	subprocess.run([sys.executable, "./evaluation/evaluate_overseer.py"], check=True)
	file = open("evaluation/evaluation_results/overseer_eval_results.md")

	def read_sixth_line():
		for i in range(6):
			line = file.readline()
			if i == 5:
				return line

	
	score_line = read_sixth_line()
	assert score_line == "- Average score: 1.00\n"
	print("Test Ran Successfully")

test_overseer_evaluation()
