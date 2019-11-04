import subprocess

class InitIsGenerator(object):
    def __init__(self, i):
        yield i
        
class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        z = input(prompt)
        subprocess.call([z])
p = Point(x=1, yy=2)


def lookup_with_default_key(mapping, key=None):
    if key is None:
        key = [] # Should be key = ()
    return mapping[key]
    
