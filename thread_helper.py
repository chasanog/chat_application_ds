import threading

def newThread(target, args):
    thr = threading.Thread(target = target, args = args)
    thr.daemon = True
    thr.start()