from . import helpers

class WebTrader:
    def __init__(self):
        self.__read_config()

    def __read_config(self):
        '''读取 config'''
        self.config = helpers.file2dict(self.config_path)
