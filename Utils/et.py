# Requires Python 3
# uses datetime.timestamp() to convert to seconds for
# elapsed time calculations : stopwatch

import time
import datetime

start_dt = datetime.datetime.now()  
start_sec = start_dt.timestamp()
time.sleep(3)
stop_dt = datetime.datetime.now()
stop_sec = stop_dt.timestamp()

# Calculate intervals
elapsed_dt = stop_dt - start_dt
elapsed_sec = stop_sec - start_sec

# Print results - with two significant digits
print(f"Start time = {start_dt} : Start_sec = {start_sec}")
print(f"Stop time = {stop_dt} : Stop_sec = {stop_sec}")
print(f"Elapsed time = {elapsed_dt} : Elapsed_sec = {elapsed_sec:.2f}")

# END
