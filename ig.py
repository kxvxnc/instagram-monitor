import requests
import time
import random
import utils
from dhooks import Webhook, Embed

class instagram:
    def __init__(self, user, delay, hook, proxy_list):
        self.headers = {
            'authority': 'www.instagram.com',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.56',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US,en;q=0.9'
        }
        self.proxies = proxy_list
        self.proxy = None
        self.user = user
        self.monitor_delay = delay
        self.hook = hook
        self.log = utils.Logger("USER", self.user)
        self.session = requests.Session()
        self.post_url = None
        self.post_caption = None
        self.post_image = []
        self.bio = None
        self.profile_pic = None
        self.profile_pic_link = None
        self.private = None
        self.run()

    def set_proxy(self):
        if len(self.proxies) > 0:
            self.proxy = random.choice(self.proxies)
        else:
            self.proxy = None
        r = self.session.get(f"https://www.instagram.com/{self.user}/?__a=1", headers=self.headers, proxies=self.proxy)
        self.log.info("Getting proxy.")
        if r.status_code == 429:
            self.log.error("Bad proxy. Removing from proxy list.")
            self.proxies.remove(self.proxy)
            self.set_proxy()
        else:
            self.log.success("Good proxy.")

    def initialize(self):
        self.log.info(f"Initializing...")
        r = self.session.get(f"https://www.instagram.com/{self.user}/?__a=1", headers=self.headers, proxies=self.proxy)
            
        try:
            r.json()
        except Exception as e:
            self.log.error(f"Switching proxy. Error: {e}")
            self.set_proxy()
            self.initialize()
            return

        try:
            latest = r.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]
            self.post_url = latest["shortcode"]
            self.post_caption = latest["edge_media_to_caption"]["edges"][0]["node"]["text"]
            if "edge_sidecar_to_children" in latest:
                for image in latest["edge_sidecar_to_children"]["edges"]:
                    self.post_image.append(image["node"]["display_url"])
            else:
                self.post_image.append(latest["display_url"])
        except Exception as e:
            self.log.error(f"Could not initialize latest post. Error: {e}")

        try:
            self.bio = r.json()["graphql"]["user"]["biography"]
            self.profile_pic_link = r.json()["graphql"]["user"]["profile_pic_url_hd"]
            self.profile_pic = r.json()["graphql"]["user"]["profile_pic_url_hd"].split("/")[-1].split("?")[0]
            self.private = r.json()["graphql"]["user"]["is_private"]
            self.log.success("User initialized.")
        except Exception as e:
            self.log.error(f"Could not initialize profile details. Error: {e}")
            
    def monitor(self):
        while True:
            try:
                self.log.info(f"Monitoring...")
                r = self.session.get(f"https://www.instagram.com/{self.user}/?__a=1", headers = self.headers, proxies=self.proxy)
                if r.status_code == 429:
                    self.set_proxy()

                try:
                    r.json()
                except Exception as e:
                    self.log.error(f"Switching proxy. Error: {e}")
                    self.set_proxy()
                    self.monitor()
                    break
                
                try:
                    user = r.json()["graphql"]["user"]
                    current = user["edge_owner_to_timeline_media"]["edges"][0]["node"]
                    if current["shortcode"] != self.post_url:
                        self.log.success("New post detected.")
                        self.post_image.clear()
                        self.post_url = current["shortcode"]
                        try:
                            self.post_caption = current["edge_media_to_caption"]["edges"][0]["node"]["text"]
                        except:
                            pass
                        if "edge_sidecar_to_children" in current:
                            for image in current["edge_sidecar_to_children"]["edges"]:
                                self.post_image.append(image["node"]["display_url"])
                        else:
                            self.post_image.append(current["display_url"])
                        self.detect_post()
                except Exception as e:
                    self.log.error(f"Couldn't get latest post. Error: {e}")

                try:
                    user = r.json()["graphql"]["user"]
                    if user["biography"] != self.bio:
                        self.bio = user["biography"]
                        self.log.success(f"New bio detected: {self.bio}")
                        self.detect_bio()
                    if user["is_private"] != self.private:
                        self.private = user["is_private"]
                        self.log.success(f"Private change: {self.private}")
                        self.detect_private()
                    if user["profile_pic_url_hd"].split("/")[-1].split("?")[0] != self.profile_pic:
                        self.profile_pic = user["profile_pic_url_hd"].split("/")[-1].split("?")[0]
                        self.profile_pic_link = user["profile_pic_url_hd"]
                        self.log.success("New profile pic detected.")
                        self.detect_profile_pic()
                except Exception as e:
                    self.log.error(f"Could not set latest user details. Error: {e}")
            except Exception as e:
                self.log.error(f"Error: {e}")
            time.sleep(self.monitor_delay)

    def detect_post(self):
        hook = Webhook(self.hook)
        embed = Embed(
            description ='New post detected.',
            color = 0x5CDBF0,
            timestamp = 'now'
        )
        embed.set_author(name='Instagram Monitor')
        embed.add_field(name = 'User', value = f"[{self.user}](https://www.instagram.com/{self.user})",inline = False)
        embed.add_field(name = 'Link', value = f"https://www.instagram.com/p/{self.post_url}/", inline = False)
        embed.set_thumbnail(self.profile_pic_link)
        if self.post_caption:
            embed.add_field(name = 'Caption', value = self.post_caption, inline = False)
        else:
            embed.add_field(name = 'Caption', value = "\u274C No caption", inline = False)
        if len(self.post_image) == 1:
            embed.set_image(self.post_image[0])
            hook.send(embed = embed)
        else:
            embed.set_image(self.post_image[0])
            hook.send(embed = embed)
            for i in range(1, len(self.post_image)):
                embed = Embed(description = f"{i+1}/{len(self.post_image)}", color = 0x5CDBF0, timestamp = 'now')
                embed.set_image(self.post_image[i])
                hook.send(embed = embed)

    def detect_bio(self):
        hook = Webhook(self.hook)
        embed = Embed(
            description = 'New bio detected.',
            color = 0x5CDBF0,
            timestamp = 'now'
        )
        embed.set_title('Instagram Monitor')
        embed.add_field(name = 'User', value = f"[{self.user}](https://www.instagram.com/{self.user})",inline = False)
        if self.bio:
            embed.add_field(name = 'Bio', value = self.bio, inline = False)
        else:
            embed.add_field(name = 'Bio', value = "\u274C Empty Bio", inline = False)
        embed.set_thumbnail(self.profile_pic_link)
        hook.send(embed = embed)

    def detect_private(self):
        hook = Webhook(self.hook)
        if self.private:
            desc = "Profile changed to private."
        elif not self.private:
            desc = "Profile changed to public."
        else:
            self.log.error("Privacy was never set.")
        embed = Embed(
            description = "Privacy change detected.",
            color = 0x5CDBF0,
            timestamp = 'now'
        )
        embed.set_author(name='Instagram Monitor')
        embed.add_field(name = 'User', value = f"[{self.user}](https://www.instagram.com/{self.user})",inline = False)
        embed.add_field(name = 'Status', value = desc, inline = False)
        embed.set_thumbnail(self.profile_pic_link)
        hook.send(embed = embed)

    def detect_profile_pic(self):
        hook = Webhook(self.hook)
        embed = Embed(
            description = 'New profile picture detected.',
            color = 0x5CDBF0,
            timestamp = 'now'
        )
        embed.set_author(name='Instagram Monitor')
        embed.add_field(name = 'User', value = f"[{self.user}](https://www.instagram.com/{self.user})",inline = False)
        embed.set_image(self.profile_pic_link)
        hook.send(embed = embed)

    def run(self):
        try:
            if self.proxies:
                self.set_proxy()
            self.initialize()
            self.monitor()
        except Exception as e:
            self.log.error(f"Error: {e}")
            return