import time
from workers.worker import create_workers


create_workers()

while True:
    print("worker working!!")
    time.sleep(1)