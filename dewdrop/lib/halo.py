#coding: utf-8
from concurrent import futures

MAX_WORKERS = 24
executor = futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)


