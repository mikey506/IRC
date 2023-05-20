import irc.bot
import json
import time

class MyBot(irc.bot.SingleServerIRCBot):
    def __init__(self, server, port, nickname, channel):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.geo_db = self.load_geo_db()

    def on_welcome(self, connection, event):
        connection.join(self.channel)

    def on_pubmsg(self, connection, event):
        message = event.arguments[0]
        if message.startswith('!communities'):
            args = message.split()[1:]
            if len(args) != 1:
                self.send_message(connection, event.target, "Usage: !communities <city/town>")
            else:
                city = args[0]
                self.search_community(connection, event.target, city)
        elif message.startswith('!addcommunity'):
            args = message.split()[1:]
            if len(args) < 6:
                self.send_message(connection, event.target, "Usage: !addcommunity <city/town from geo.db> <community name> <total members/subscription> <Platform> <URL for Community> <mod usernames>")
            else:
                city_tag = args[0]
                community_name = args[1]
                total_members = args[2]
                platform = args[3]
                url = args[4]
                mod_usernames = args[5:]
                self.add_community(connection, event.target, city_tag, community_name, total_members, platform, url, mod_usernames)
        elif message.startswith('!removecommunity'):
            args = message.split()[1:]
            if len(args) != 2:
                self.send_message(connection, event.target, "Usage: !removecommunity <city/town from geo.db> <community name>")
            else:
                city_tag = args[0]
                community_name = args[1]
                self.remove_community(connection, event.target, city_tag, community_name)
        elif message.startswith('!setcommunity'):
            args = message.split()[1:]
            if len(args) != 4:
                self.send_message(connection, event.target, "Usage: !setcommunity <city/town from geo.db> <community name> <variable> <value>")
            else:
                city_tag = args[0]
                community_name = args[1]
                variable = args[2]
                value = args[3]
                self.set_community(connection, event.target, city_tag, community_name, variable, value)

    def send_message(self, connection, target, message):
        message = message.replace('\r', '').replace('\n', '')  # Remove carriage returns and newlines
        connection.privmsg(target, message)
        time.sleep(3)  # Introduce a 3-second delay

    def load_geo_db(self):
        geo_db = {}
        with open('geo.db', 'r') as file:
            for line in file:
                city, lat, lon = line.strip().split(',')
                geo_db[city] = (float(lat), float(lon))
        return geo_db

    def search_community(self, connection, target, city):
        filename = f'./communities/{city}.json'
        try:
            with open(filename, 'r') as file:
                communities = json.load(file)
            if communities:
                for community in communities:
                    community_name = community['community_name']
                    total_members = community['total_members']
                    platform = community['platform']
                    url = community['url']
                    mods = ', '.join(community['mods'])
                    output = f"Name:** {community_name} ** >> Size:** {total_members} **>>** {platform} **>>**- {url} **"
                    self.send_message(connection, target, output)
            else:
                self.send_message(connection, target, f"No communities found for {city}")
        except FileNotFoundError:
            self.send_message(connection, target, f"No communities found for {city}")
        except json.JSONDecodeError:
            self.send_message(connection, target, f"Invalid JSON file for {city}")

    def add_community(self, connection, target, city_tag, community_name, total_members, platform, url, mod_usernames):
        filename = f'./communities/{city_tag}.json'
        try:
            with open(filename, 'r+') as file:
                communities = json.load(file)
                communities.append({
                    'community_name': community_name,
                    'total_members': total_members,
                    'platform': platform,
                    'url': url,
                    'mods': mod_usernames
                })
                file.seek(0)
                json.dump(communities, file, indent=4)
                file.truncate()
            self.send_message(connection, target, f"Community added to {city_tag} successfully")
        except FileNotFoundError:
            with open(filename, 'w') as file:
                communities = [{
                    'community_name': community_name,
                    'total_members': total_members,
                    'platform': platform,
                    'url': url,
                    'mods': mod_usernames
                }]
                json.dump(communities, file, indent=4)
            self.send_message(connection, target, f"Community added to {city_tag} successfully")

    def remove_community(self, connection, target, city_tag, community_name):
        filename = f'./communities/{city_tag}.json'
        try:
            with open(filename, 'r+') as file:
                communities = json.load(file)
                removed = False
                for community in communities:
                    if community['community_name'] == community_name:
                        communities.remove(community)
                        removed = True
                        break
                if removed:
                    file.seek(0)
                    json.dump(communities, file, indent=4)
                    file.truncate()
                    self.send_message(connection, target, f"Community '{community_name}' removed from {city_tag}")
                else:
                    self.send_message(connection, target, f"Community '{community_name}' not found in {city_tag}")
        except FileNotFoundError:
            self.send_message(connection, target, f"No communities found for {city_tag}")
        except json.JSONDecodeError:
            self.send_message(connection, target, f"Invalid JSON file for {city_tag}")

    def set_community(self, connection, target, city_tag, community_name, variable, value):
        filename = f'./communities/{city_tag}.json'
        try:
            with open(filename, 'r+') as file:
                communities = json.load(file)
                modified = False
                for community in communities:
                    if community['community_name'] == community_name:
                        community[variable] = value
                        modified = True
                        break
                if modified:
                    file.seek(0)
                    json.dump(communities, file, indent=4)
                    file.truncate()
                    self.send_message(connection, target, f"Variable '{variable}' for community '{community_name}' in {city_tag} set to '{value}'")
                else:
                    self.send_message(connection, target, f"Community '{community_name}' not found in {city_tag}")
        except FileNotFoundError:
            self.send_message(connection, target, f"No communities found for {city_tag}")
        except json.JSONDecodeError:
            self.send_message(connection, target, f"Invalid JSON file for {city_tag}")

if __name__ == "__main__":
    server = "irc.example.com"  # Update with your IRC server address
    port = 6667  # Update with the IRC server port
    nickname = "MyBot"  # Update with your desired nickname
    channel = "#example"  # Update with the channel you want the bot to join

    bot = MyBot(server, port, nickname, channel)
    bot.start()
