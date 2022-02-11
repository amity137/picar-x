class ConfigFile(object):

    def __init__(self, filename):

        self.filename = filename

        try:
            with open(self.filename, 'r') as conf:
                text = conf.read()
                self.map = eval(text)
        except FileNotFoundError:
            self.map = dict()

    def get(self, name, default_value = None):

        return self.map[name] if name in self.map else default_value

    def set(self, name, value):

        self.map[name] = value

        with open(self.filename, 'w') as conf:
            text = conf.write(str(self.map))