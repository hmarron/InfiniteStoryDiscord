import errors

class GameStoreInterface:
    def GetGame(self, channel) :
        pass

    def SaveGame(self, channel, game):
        pass

# interface for loading games
# implementations:
# - in memory
# - some doc based db?

# GameStoreMemory implements a game store in memory.
# Might do a redis store or maybe som doc based db store later.
class GameStoreMemory(GameStoreInterface):
    def __init__(self):
        self.games = {}

    def GetGame(self, channel):
        if channel not in self.games:
            return None, errors.ErrNoGame

        return self.games[channel], None

    def SaveGame(self, channel, game):
        self.games[channel] = game
        return None
