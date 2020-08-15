import yaml

__config = None


def config():
    global __config
    if not __config:
        # Abre archivo en modo de leectura -- f de file
        with open('config.yaml', mode='r') as f:
            __config = yaml.load(f)
    return __config
