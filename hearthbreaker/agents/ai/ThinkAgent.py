import copy

from hearthbreaker.agents.basic_agents import InnerRandomAgent
from hearthbreaker.engine import Player
from hearthbreaker.tags.base import AuraUntil
from multiprocessing import Pool

'''
This agent copy current game to mind and play with himself
'''

trainlog = open('train.dat', 'a')


def evaluating(inputgame):
    game4test = inputgame.copy(keep=True)
    while not game4test.game_ended:
        game4test.play_single_turn()
    if game4test.playersInOrder[0].hero.dead and game4test._turns_passed < 50:
        return 1.0
    else:
        return 0.0


class ThinkAgent:
    def __init__(self, player, period):
        self.__player = player
        self.__game = player.game
        self.__period = period
        # self.__testtime = 100
        self.__testtime = 10

    def getGame(self):
        return self.__game

    def think(self):
        global trainlog
        # print("UCT is thinking")
        allgames = []
        winrate = []
        action = []
        for i in range(self.__period):
            self.__copyGameToMind()
            self.__gameinmind.current_player.agent.setoutput(True)
            self.__gameinmind.current_player.agent.do_turn(self.__gameinmind.current_player)
            print("Thinking:%s" % i)
            allgames.append(self.__gameinmind.copy(keep=True))
            winrate.append(0)
            self.__gameinmind._end_turn()
            action.append(self.__gameinmind.current_player.agent.datatowrite)
            self.__gameinmind.current_player.agent.datatowrite = []
            self.__gameinmind.current_player.agent.setoutput(False)
            self.__gameinmind.other_player.agent.setoutput(False)
            pool=Pool(2)
            winrate[i] = sum(pool.map(evaluating, [self.__gameinmind for i in range(self.__testtime)]))
            pool.close()
            pool.join()
            # game4test = self.__gameinmind.copy(keep=True)
            # for j in range(self.__testtime):
            #     winrate[i]+=self.evaluating(self.__gameinmind)
            # print('Retesting...')
            # while not game4test.game_ended:
            #     game4test.play_single_turn()
            # if game4test.playersInOrder[0].hero.dead and game4test._turns_passed < 50:
            #     winrate[i] += 1.0
            # game4test = self.__gameinmind.copy(keep=True)
            winrate[i] = winrate[i] / self.__testtime
        print('Win rates:' + ','.join([str(a) for a in winrate]))
        v = max(winrate)
        if len(action[winrate.index(v)]) > 0:
            trainlog.write('\t'.join(action[winrate.index(v)]) + '\n')
            trainlog.flush()
        # print("win rate:%s->%s" % (v, winrate.index(v)))
        # print("Target game->%s:%s\t%s:%s" % (allgames[winrate.index(v)].players[0].name, allgames[winrate.index(v)].players[0].hero.health,
        # allgames[winrate.index(v)].players[1].name, allgames[winrate.index(v)].players[1].hero.health))
        return allgames[winrate.index(v)]

    def __copyGameToMind(self):
        copied_game = copy.copy(self.__game)
        copied_game.events = copy.copy(self.__game.events)
        copied_game._all_cards_played = [copy.copy(card) for card in self.__game._all_cards_played]
        '''copied_game.players = [player.copy(copied_game) for player in self.players]
        if self.__game.current_player is self.__game.players[0]:
            copied_game.current_player = copied_game.players[0]
            copied_game.other_player = copied_game.players[1]
        else:
            copied_game.current_player = copied_game.players[1]
            copied_game.other_player = copied_game.players[0]

        copied_game.current_player.opponent = copied_game.other_player
        copied_game.other_player.opponent = copied_game.current_player
        copied_game._has_turn_ended = self._has_turn_ended

        for player in copied_game.players:
            player.hero.attach(player.hero, player)
            if player.weapon:
                player.weapon.attach(player.hero, player)
            for minion in player.minions:
                minion.attach(minion, player)

        for secret in copied_game.other_player.secrets:
            secret.activate(copied_game.other_player)
        '''
        self.__gameinmind = copied_game
        self.__copyPlayerToMind()

    def __copyPlayerToMind(self):
        onedeck = None
        for player in self.__gameinmind.players:
            if player.name == self.__player.name:
                onedeck = player.deck
        if onedeck is None:
            raise Exception("can't find agent")
        copied_players = [
            (Player(player.name, onedeck.copy(), InnerRandomAgent(player, player.name), self.__gameinmind), player)
            for player in self.__game.players]
        for copied_player, original_player in copied_players:
            copied_player.hero = original_player.hero.copy(copied_player)
            copied_player.graveyard = copy.copy(original_player.graveyard)
            copied_player.minions = [minion.copy(copied_player, self.__gameinmind) for minion in
                                     original_player.minions]
            copied_player.hand = [copy.copy(card) for card in original_player.hand]
            for card in copied_player.hand:
                card._attached = False
                card.attach(card, copied_player)
            copied_player.spell_damage = original_player.spell_damage
            copied_player.mana = original_player.mana
            copied_player.max_mana = original_player.max_mana
            copied_player.upcoming_overload = original_player.upcoming_overload
            copied_player.current_overload = original_player.current_overload
            copied_player.dead_this_turn = copy.copy(original_player.dead_this_turn)
            if original_player.weapon:
                copied_player.weapon = original_player.weapon.copy(copied_player)
            for effect in original_player.effects:
                effect = copy.copy(effect)
                copied_player.add_effect(effect)
            copied_player.secrets = []
            for secret in original_player.secrets:
                new_secret = type(secret)()
                new_secret.player = copied_player
                copied_player.secrets.append(new_secret)
            for aura in filter(lambda a: isinstance(a, AuraUntil), original_player.player_auras):
                aura = copy.deepcopy(aura)
                aura.owner = copied_player.hero
                copied_player.add_aura(aura)
            for aura in filter(lambda a: isinstance(a, AuraUntil), original_player.object_auras):
                aura = copy.deepcopy(aura)
                aura.owner = copied_player.hero
                copied_player.add_aura(aura)
            copied_player.effect_count = dict()

        self.__gameinmind.players = [player for player, oplayer in copied_players]
        if self.__game.current_player is self.__game.players[0]:
            self.__gameinmind.current_player = self.__gameinmind.players[0]
            self.__gameinmind.other_player = self.__gameinmind.players[1]
        else:
            self.__gameinmind.current_player = self.__gameinmind.players[1]
            self.__gameinmind.other_player = self.__gameinmind.players[0]

        self.__gameinmind.current_player.opponent = self.__gameinmind.other_player
        self.__gameinmind.other_player.opponent = self.__gameinmind.current_player
        self.__gameinmind._has_turn_ended = self.__game._has_turn_ended

        for player in self.__gameinmind.players:
            player.hero.attach(player.hero, player)
            if player.weapon:
                player.weapon.attach(player.hero, player)
            for minion in player.minions:
                minion.attach(minion, player)

        for secret in self.__gameinmind.other_player.secrets:
            secret.activate(self.__gameinmind.other_player)
