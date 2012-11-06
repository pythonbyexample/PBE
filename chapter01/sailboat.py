import math

def dotproduct(v1, v2):
    return v1.x * v2.x + v1.y * v2.y

def length(v):
    return math.sqrt(dotproduct(v, v))

def angle(v1, v2):
    return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))

class Vector(object):
    __slots__ = ['x', 'y']

    def __init__(self, x, y):
        self.x, self.y = x, y

    def __str__(self):
        return str(tuple(self))

    def __repr__(self):
        return str(tuple(self))

    def __iter__(self):
        return iter((self.x, self.y))

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

def main():
    v1 = Vector(1,2)
    v2 = Vector(2,5)
    print "v1", v1
    print "v2", v2
    v = v1+v2
    print "v", v
    t = v1, v2, v
    print dotproduct(v1, v2)
    print angle(v1, v2)
    print [length(x) for x in t]

main()
