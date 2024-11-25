from .relay import Relay


def from_conf(conf):
    conf.setdefault("normally_open", "yes")
    return Relay(
        conf["board_url"],
        conf.getint("relay_number"),
        normally_open=conf.getboolean("normally_open"),
    )
