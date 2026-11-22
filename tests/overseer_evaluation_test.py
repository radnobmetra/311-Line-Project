

import sys
from pathlib import Path
sys.path.insert(1, "../311-Line-Project")
import subprocess


def test_overseer_evaluation():
	test_dir = Path(__file__).resolve().parent
	project_dir = test_dir.parent

	if str(project_dir) not in sys.path:
		sys.path.insert(0, str(project_dir))
	
	subprocess.run([sys.executable, str(project_dir / "evaluation/evaluate_overseer.py")], cwd=project_dir, check=True)
	results_file = project_dir / "evaluation/evaluation_results/overseer_eval_results.md"
	results_markdown_file = results_file.open()

	def read_sixth_line():
		for i in range(6):
			line = results_markdown_file.readline()
			if i == 5:
				return line

	
	score_line = read_sixth_line()
	assert score_line == "- Average score: 1.00\n"
	print("Test Ran Successfully")

test_overseer_evaluation()
