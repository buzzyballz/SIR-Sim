from datetime import datetime

class logger:

    def __init__(self, filename=None, stdout=True):
        if filename is None:
            self.filename = None
        else:
            self.filename = open(filename, "a")
        self.out = stdout

    def info(self, msg):
        msg = str(datetime.now()) + " [INFO] " + msg
        if self.out:
            print(msg)
        if not self.filename is None:
            self.filename.write(msg)
