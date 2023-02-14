def run_file(filename):
    import sys
    m = filename.split(".py")[0]
    if sys.modules.get(m):
        del sys.modules[m]
    __import__(m)
