import time


def coffee(last_frame_time):
    sleep_time = 1. / 30
    if sleep_time > 0:
        time.sleep(sleep_time)
    return last_frame_time + sleep_time


start_time = time.time()
last_frame_time = time.time()
tmp = 0
while True:
    last_frame_time = coffee(last_frame_time)
    tmp += 1
    if tmp % 100 == 0:
        #print("Running @ " + str( float(tmp) / (time.time()-start_time) ) + " fps", end='\r' )
        print(time.time() - start_time)
