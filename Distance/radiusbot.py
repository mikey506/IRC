import irc.bot
from math import radians, cos, sin, sqrt, asin

class MyBot(irc.bot.SingleServerIRCBot):
    def __init__(self, server, port, nickname, channel):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.geo_db = self.load_geo_db()

    def on_welcome(self, connection, event):
        connection.join(self.channel)

    def on_pubmsg(self, connection, event):
        message = event.arguments[0]
        if message.startswith('!radius'):
            args = message.split()[1:]
            if len(args) != 2:
                self.send_message(connection, event.target, 'Usage: !radius <km> <city/town>')
            else:
                radius_km = float(args[0])
                origin_city = ' '.join(args[1:])
                city_results = self.radius_search(origin_city, radius_km)
                if city_results:
                    result_message = f"Cities within {radius_km} km of {origin_city}: {', '.join(city_results)}"
                else:
                    result_message = f"No cities found within {radius_km} km of {origin_city}"
                self.send_message(connection, event.target, result_message)

    def send_message(self, connection, target, message):
        connection.privmsg(target, message)

    def load_geo_db(self):
        geo_db = {}
        with open('geo.db', 'r') as file:
            for line in file:
                data = line.strip().split(',')
                city = data[0]
                coords = tuple(map(float, data[1:]))
                geo_db[city] = coords
        return geo_db

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371.0  # Earth's radius in kilometers
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)

        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad

        a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))

        distance = R * c
        return distance

    def radius_search(self, origin_city, radius_km):
        origin_coords = self.geo_db.get(origin_city)
        if not origin_coords:
            return []

        city_results = []
        for city, coords in self.geo_db.items():
            if city == origin_city:
                continue
            distance = self.calculate_distance(origin_coords[0], origin_coords[1], coords[0], coords[1])
            if distance <= radius_km:
                city_results.append(city)
        return city_results

if __name__ == '__main__':
    server = 'irc.server.com'  # IRC server hostname
    port = 6667  # IRC server port
    nickname = 'MyBot'  # Bot nickname
    channel = '#mychannel'  # Channel to join

    bot = MyBot(server, port, nickname, channel)
    bot.start()
