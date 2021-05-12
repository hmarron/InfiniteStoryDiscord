import errors
import random

playerClasses = ["noble", "knight", "peasant", "wizard", "rogue", "ranger", "squire"]

class GameManager:
    def __init__(self, gameRepo, infiniteStoryClient):
        self.infiniteStoryClient = infiniteStoryClient
        self.gameRepo = gameRepo

    def NewGame(self, host, channel, enforceTurns=False):
        game = Game(host, self.infiniteStoryClient, enforceTurns=enforceTurns)
        self.gameRepo.SaveGame(channel, game)
        return game, None

    def GetGame(self, channel):
        return self.gameRepo.GetGame(channel)

    def SaveGame(self, channel, game):
        return self.gameRepo.SaveGame(channel, game)

class Game:
    def __init__(self, host, infiniteStoryClient, enforceTurns=False):
        self.id = 0
        self.players = {}
        self.host = host # discord name NOT player name
        self.infiniteStoryClient = infiniteStoryClient
        self.running = False
        self.enforceTurns = enforceTurns
        self.turnOrder = []

    def Start(self, discordName):
        if self.running:
            return None, errors.ErrGameRunning

        if len(self.players) == 0:
            return None, errors.ErrNotEnoughPlayers

        if discordName != self.host:
            return None, errors.ErrHostOnly

        if self.host not in self.players:
            return None, errors.ErrHostNeedsName

        if self.enforceTurns:
            self.__initTurnOrder()

        self.id, text, err = self.infiniteStoryClient.NewStory(random.choice(playerClasses), self.players[self.host])
        if err != None:
            return None, err

        self.running = True
        return text, None

    def SetPlayerName(self, discordName, playerName):
        if self.running:
            return errors.ErrGameRunning

        if playerName == "":
            return errors.ErrNoName

        if playerName in self.players.values():
            return errors.ErrNameAlreadyInUse

        self.players[discordName] = playerName

        return None

    def GetPlayerName(self, discordName, playerName):
        if discordName not in self.players:
            return None
        return self.players[discordName]

    def Act(self, discordName, action):
        if not self.running:
            return None, errors.ErrGameNotRunning

        if discordName not in self.players:
            return None, errors.ErrPlayerNotFound

        if self.enforceTurns and not self.__isPlayersTurn(discordName):
            return None, errors.ErrNotYourTurn

        # if action is being carried out by non-host
        # convert "turn left" -> "john turns left"
        if discordName != self.host and action.strip() != "":
            parts = action.split(" ")
            parts[0] = parts[0] + "s"
            action = " ".join(parts)
            action = self.players[discordName] + " " + action

        text, err = self.infiniteStoryClient.Act(self.id, action)
        if err != None:
            return None, err

        if self.enforceTurns:
            self.__nextTurn()

        text = ">> " + action + "\n " + text
        return text, None

    def Say(self, discordName, action):
        if not self.running:
            return None, errors.ErrGameNotRunning

        if discordName not in self.players:
            return None, errors.ErrPlayerNotFound

        if discordName != self.host:
            return None, errors.ErrHostOnly

        if self.enforceTurns and not self.__isPlayersTurn(discordName):
            return None, errors.ErrNotYourTurn

        text, err = self.infiniteStoryClient.Say(self.id, action)
        if err != None:
            return None, err

        if self.enforceTurns:
            self.__nextTurn()

        text = ">> \"" + action + "\"\n " + text
        return text, None

    def Info(self):
        info = "Game ID: **{}** \n".format(self.id)
        info += "Running: **{}** \n".format(self.running)
        info += "Party: \n"
        for discordName, playerName in self.players.items():
            info += "   **{}**: **{}** \n".format(discordName, playerName)

        if self.enforceTurns:
            info += "Turn order: \n"
            i = 1
            for player in self.turnOrder:
                # TODO check if it's this players turn
                info += "   {}. {}\n".format(i, player)
                i += 1

        mainPlayer = "None"
        if self.host in self.players:
            mainPlayer = self.players[self.host]

        info += "Main Character: **{}** as **{}**\n".format(self.host, mainPlayer)


        return info, None

    def __initTurnOrder(self):
        self.turnOrder = [self.host]
        print("iterating over")
        print(self.players)
        print(self.players.keys())
        for player in self.players:
            if player != self.host:
                self.turnOrder.append(player)

    def __nextTurn(self):
        self.turnOrder += [self.turnOrder.pop(0)]

    def __isPlayersTurn(self, discordName):
        return self.turnOrder[0] == discordName

