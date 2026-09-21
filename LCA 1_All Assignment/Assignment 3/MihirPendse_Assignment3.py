#!/usr/bin/env python
# coding: utf-8

# In[ ]:


x=int(input("Enter first side "))
y=int(input("Enter second side "))
z=int(input("Enter third side "))

def right_angled_triangle(x,y,z):

    if x**2+ y**2==z**2 or z**2+ y**2==x**2 or x**2+ z**2==y**2:
        print("It is a right angled triangle") 
    else:
        print("It is not a right angled triangle")
right_angled_triangle(x,y,z)


