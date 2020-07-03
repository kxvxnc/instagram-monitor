import ig
import json
import threading
import utils

def main():
    proxy_list = utils.get_proxies("proxies.txt")
    with open("config.json", "r") as f2:
        settings = json.loads(f2.read())
        delay = settings["delay"]
        webhook = settings["webhook"]
        threads = []
        for user in settings["users"]:
            t = threading.Thread(target=ig.instagram, args=(user, delay, webhook, proxy_list))
            threads.append(t)
            t.start()
            
if __name__ == "__main__":
    main()