import sys
import random
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--exclude', '-e', type=str, help='excluded chars')
parser.add_argument('--length', '-l', type=int, help='password length')
parser.add_argument('--alphanum', '-o',  action="store_true", help='only include alphnum')

args = parser.parse_args()

length=12
if args.length:
    length=args.length
i=0
passwd=[]
while i < length:
    tmp_char = chr(random.randint(33,126))
    if args.alphanum:
        if not tmp_char.isalnum():
            continue
    if args.exclude:
        if tmp_char in args.exclude:
            continue
    passwd.append(tmp_char)
    i+=1

print(''.join(passwd))
