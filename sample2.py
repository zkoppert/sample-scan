import subprocess
from xml.dom.minidom import parse, parseString

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
    
def transcode_file(request, filename):
    command = 'ffmpeg -i "{source}" output_file.mpg'.format(source=filename)
    subprocess.call(command, shell=True)

dom1 = parse('c:\\temp\\mydata.xml')
