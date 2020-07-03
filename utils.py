from colored import stylize
from datetime import datetime
import colored

class Logger:
    def __init__(self, title, id_num=None):
        if id_num == None:
            self.identifier = "[{}]".format(title)
        else:
            self.identifier = "[{} {}]".format(title, id_num)

    def alert(self, msg, tag="ALERT"):
        current_time = datetime.now().strftime("%I:%M:%S.%f %p")
        text = "[{}] {} [{}] -> {}".format(current_time, self.identifier, tag, msg)
        print(stylize(text, colored.fg("magenta")))

    def info(self, msg, tag="INFO"):
        current_time = datetime.now().strftime("%I:%M:%S.%f %p")
        text = "[{}] {} [{}] -> {}".format(current_time, self.identifier, tag, msg)
        print(stylize(text, colored.fg("cyan")))

    def error(self, msg, tag="ERROR"):
        current_time = datetime.now().strftime("%I:%M:%S.%f %p")
        text = "[{}] {} [{}] -> {}".format(current_time, self.identifier, tag, msg)
        print(stylize(text, colored.fg("red")))

    def success(self, msg ,tag="SUCCESS"):
        current_time = datetime.now().strftime("%I:%M:%S.%f %p")
        text = "[{}] {} [{}] -> {}".format(current_time, self.identifier, tag, msg)
        print(stylize(text, colored.fg("green")))

def get_proxies(file):
    proxy_list = []
    proxies = open("proxies.txt").read().splitlines()
    for proxy in proxies:
        p = proxy.split(":")
        try:
            dict = {
                "http": f"http://{p[2]}:{p[3].strip()}@{p[0]}:{p[1]}",
                "https": f"https://{p[2]}:{p[3].strip()}@{p[0]}:{p[1]}",
            }
            proxy_list.append(dict)
        except:
            dict = {
                "http": f"http://{p[0]}:{p[1]}",
                "https": f"https://{p[0]}:{p[1]}",
            }
            proxy_list.append(dict)
    return proxy_list