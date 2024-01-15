import sys
import datetime

if __name__ == "__main__":
    if sys.argv[1] == "sub":
        date1 = datetime.datetime.strptime(sys.argv[2], '%Y-%m-%dT%H:%M:%SZ')
        date2 = datetime.datetime.strptime(sys.argv[3], '%Y-%m-%dT%H:%M:%SZ')
        delta = date2 - date1
        print(f"Time delta between {sys.argv[3]} and {sys.argv[2]} is:  {delta}")
    else:
        print("Cannot regonize the input")
