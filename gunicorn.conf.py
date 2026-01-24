import os

bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"
workers = 1
worker_class = "sync"
threads = 1
timeout = 180
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
preload_app = False
accesslog = "-"
errorlog = "-"
loglevel = "info"
capture_output = True
enable_stdio_inheritance = True


