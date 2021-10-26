import threading
import time
 
def test(name):
    mythread = threading.currentThread()
    mythread.mystop=False
    for i in range(100):
        if mythread.mystop:
            break
        time.sleep(1)
        print("run "+ name + ": " + str(i))
    print("thread is finished")
thread_name = 'thread1' 
th1 = threading.Thread(target=test, args=[thread_name])
th1.start() 
time.sleep(5)
print("to create thread2")

thread_name = 'thread2'
th2 = threading.Thread(target=test, args=[thread_name])
th2.start()
time.sleep(5)
print("before")
th2.join(-360)
th2.mystop=True
print("after")
time.sleep(5)
print("main application is finished")
