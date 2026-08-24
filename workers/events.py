import time
from workers.worker import even_manager


while True:
    even_manager()
    print("Workers working!!")
    time.sleep(5)
    