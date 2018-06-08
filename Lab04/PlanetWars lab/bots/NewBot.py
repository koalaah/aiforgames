class NewBot(object):
    def update(self, gameinfo):
        if gameinfo.my_planets and gameinfo.not_my_planets and not gameinfo.my_fleets:

            src = max(gameinfo.my_planets.values(), key=lambda p: p.num_ships)

        # find a target planet with the minimum number of ships.
            dest = min(gameinfo.not_my_planets.values(), key=lambda p: p.num_ships)

            gameinfo.planet_order(src, dest, int(src.num_ships * 0.75))

