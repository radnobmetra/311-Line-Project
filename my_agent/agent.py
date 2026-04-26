import threading
from .subagents import overseer_agent
from timerloop import run_loop 

#enables timer in background; for inactivity
timerloop_thread = threading.Thread(target=run_loop, daemon=True)
timerloop_thread.start()

root_agent = overseer_agent
