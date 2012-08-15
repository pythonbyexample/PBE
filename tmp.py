#!/usr/bin/env python

class A(object):
    def __init__(self, x, y):
        self.a = x, y
        self.x, self.y = x, y

    def __str__(self):
        return str(self.a)

    def __iter__(self):
        return iter(self.a)

a = A(1,2)
x, y = a
print a
print x, y
