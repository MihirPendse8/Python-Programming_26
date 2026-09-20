#!/usr/bin/env python
# coding: utf-8

# In[ ]:


a= int(input("Enter a number a: "))
b= int(input("Enter a number b: "))
c= int(input("Enter a number c: "))
if a>b:
    if a>=c:
        if a==c:
            print("a and c are equal and largest")
        else:
            print("a is the largest number")
    else:
        print("c is the largest number")
elif a==b and a==c:
    print("a,b and c are equal")
elif a==b:
    print("a and b are equal and largest")
elif b>=c:
    if b==c:
        print("b and c are equal and largest")
    else:
        print("b is the largest number")
else:
    print("c is the largest number")


# In[ ]:




