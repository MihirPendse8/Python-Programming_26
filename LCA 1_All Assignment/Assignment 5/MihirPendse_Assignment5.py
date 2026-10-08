#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import re
def is_alphanumeric(s):
    return bool(re.fullmatch(r'[a-zA-Z0-9]+',s))

text=input("Enter a string.")
if is_alphanumeric(text):
    print("The string contains only a-z, A-Z, and 0-9.")
else:
    print("The string contains other characters.")

