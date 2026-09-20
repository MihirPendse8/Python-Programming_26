#!/usr/bin/env python
# coding: utf-8

# In[8]:


thislist=["Aditya" ,"Ayush" ,"Mihir" ,"Yash", "Parth"]
print(thislist)

thislist[3:5]=["Arjun", "Sarthak"]
print(thislist)

thislist.insert(3,"Akshat")
print(thislist)

thislist.append("Atharva")
print(thislist)

thislist.remove("Ayush")
print(thislist)


# In[3]:


thistuple=("Aditya" ,"Ayush" ,"Mihir" ,"Yash", "Parth")
print(thistuple)

y=list(thistuple)
y.append("Atharva")
y.remove("Ayush")
y.insert(2,"Akshat")
y[3:5]=["Arjun", "Sarthak"]
thistuple=tuple(y)
print(thistuple)


# In[2]:


mydict={
    "Name":"Mihir",
    "College":"MIT-WPU",
    "Division":2
}
print(mydict)

mydict["Name"]="Aditya"

mydict["Branch"]="CSE"

mydict.pop("Division")

print(mydict)

x=mydict.keys()
print(x)

y=mydict.items()
print(y)

