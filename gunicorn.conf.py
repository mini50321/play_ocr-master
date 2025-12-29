import multiprocessing
import os

bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 180
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
preload_app = True
accesslog = "-"
errorlog = "-"
loglevel = "info"
capture_output = True
enable_stdio_inheritance = True

