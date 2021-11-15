#!/bin/bash
echo $1
succ=0
fail=0
for i in $(cat "$1"* | grep 'Success:' | cut -d ' ' -f 13 | cut -d ':' -f 2); do ((succ = succ+i)); done; echo "Success: $succ";
sum=0
for i in $(cat "$1"* | grep 'Success:' | cut -d ' ' -f 11 | cut -d ':' -f 2); do ((fail = fail+i)); done; echo "Fail: $fail";
echo "Sucess: $succ, Fail: $fail, Success Rate: $(( succ*100/(succ+fail) )) "
cat "$1"* | grep ERROR | cut -d ' ' -f 11- | sort | uniq -c 

