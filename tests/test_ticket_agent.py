
import subprocess
import sys
import pytest

sys.path.insert(1, "../311-Line-Project")
#import ticket_eval

subprocess.run([sys.executable, "ticket_eval.py"], check=True)

def test_ticket_agent_evaluation():

	# evaluate ticket agent
	file = open("evaluation_results/ticket_stat_eval_results.md")

	def read_sixth_line():
		for i in range(6):
			line = file.readline()
			if i == 5:
				return line

	
	score_line = read_sixth_line()
	assert score_line == "- Average score: 1.00\n"
	print("Test Ran Successfully")

