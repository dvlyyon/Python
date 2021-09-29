def fibonacci(n):
   temp1, temp2 = 0, 1
   total = 0
   while total < n:
       yield temp1
       temp3 = temp1 + temp2
       temp1 = temp2
       temp2 = temp3
       total += 1
fib_object1 = fibonacci(20)
fib_object2 = fibonacci(20)
print(list(fib_object1))
print(list(fib_object2))
