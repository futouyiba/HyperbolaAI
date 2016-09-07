import random
from hearthbreaker.serialization.serialization import serialize

from hearthbreaker.agents.ai.ThinkAgent import ThinkAgent
from hearthbreaker.agents.basic_agents import RandomAgent


class SimpleUCTAgent(RandomAgent):
    def __init__(self, finishrate=0.0001, period=400):
        RandomAgent.__init__(self)
        self.__finishrate = finishrate
        self.__period = period

    def do_card_check(self, cards):
        return [random.choice([True, False]) for i in range(0, 4)]

    def do_turn(self, player):
        print("Game status:" + 'Turn passed:%s\t' % player.game._turns_passed + player.name + ":" + str(
            player.hero.health) + "\t" + player.game.other_player.name + ':' + str(
            player.game.other_player.hero.health))
        self.__thinkagent = ThinkAgent(player, self.__period)
        nextgame = self.__thinkagent.think()
        '''Recover human player's information'''
        print('Player:' + nextgame.players[nextgame.play_order[0]].name + '\t' + str(
            nextgame.players[nextgame.play_order[0]].hero.health))
        print('Player:' + nextgame.players[nextgame.play_order[1]].name + '\t' + str(
            nextgame.players[nextgame.play_order[1]].hero.health))
        # nextgame.players[nextgame.play_order[0]] = self.__thinkagent.getGame().players[nextgame.play_order[0]]
        nextgame.players[nextgame.play_order[0]].mycopy(self.__thinkagent.getGame().players[nextgame.play_order[0]])
        nextgame.players[nextgame.play_order[1]].mycopy(self.__thinkagent.getGame().players[nextgame.play_order[1]])
        # if self.__thinkagent.getGame().current_player is self.__thinkagent.getGame().players[0]:
        #     nextgame.current_player = nextgame.players[0]
        #     nextgame.other_player = nextgame.players[1]
        # else:
        #     nextgame.current_player = nextgame.players[1]
        #     nextgame.other_player = nextgame.players[0]

        # nextgame.current_player.opponent = nextgame.other_player
        # nextgame.other_player.opponent = nextgame.current_player
        # nextgame._has_turn_ended = self.__thinkagent.getGame()._has_turn_ended


        '''while True:
            attack_minions = [minion for minion in filter(lambda minion: minion.can_attack(), player.minions)]
            if player.hero.can_attack():
                attack_minions.append(player.hero)
            playable_cards = [card for card in filter(lambda card: card.can_use(player, player.game), player.hand)]
            if player.hero.power.can_use():
                possible_actions = len(attack_minions) + len(playable_cards) + 1
            else:
                possible_actions = len(attack_minions) + len(playable_cards)
            if possible_actions > 0:
                action = random.randint(0, possible_actions - 1)
                if player.hero.power.can_use() and action == possible_actions - 1:
                    player.hero.power.use()
                elif action < len(attack_minions):
                    attack_minions[action].attack()
                else:
                    player.game.play_card(playable_cards[action - len(attack_minions)])
                if self.finish_turn():
                    return
            else:
                return
        '''

    def finish_turn(self):
        return random.randrange(0, 1) < self.__finishrate

    def choose_target(self, targets):
        return targets[random.randint(0, len(targets) - 1)]

    def choose_index(self, card, player):
        return random.randint(0, len(player.minions))

    def choose_option(self, options, player):
        options = self.filter_options(options, player)
        return options[random.randint(0, len(options) - 1)]
