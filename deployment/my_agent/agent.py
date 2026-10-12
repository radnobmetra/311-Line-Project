import threading
from google.adk.apps import App
from google.adk.agents.context_cache_config import ContextCacheConfig
from .subagents import overseer_agent
from timerloop import run_loop

# Enables timer in background; for inactivity
timerloop_thread = threading.Thread(target=run_loop, daemon=True)
timerloop_thread.start()

root_agent = overseer_agent

app = App(
    name="my_agent",
    root_agent=root_agent,
    context_cache_config=ContextCacheConfig(),
)