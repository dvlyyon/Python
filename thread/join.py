import threading
import time
 
def test(name):
    for i in range(10):
        time.sleep(1)
        print("run "+ name + ": " + str(i))
    print("thread is finished")
thread_name = 'test thread' 
th = threading.Thread(target=test, args=[thread_name])
th.start() 
time.sleep(5)
print("main application is finished")

thread_name = 'test thread'
th = threading.Thread(target=test, args=[thread_name])
th.start()
th.join(360)
time.sleep(5)
print("main application is finished")
