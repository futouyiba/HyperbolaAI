import abc
import copy
import random

# from hearthbreaker.serialization.serialization import serialize
from hearthbreaker.cards.base import Card



class Agent(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def do_card_check(self, cards):
        pass

    @abc.abstractmethod
    def do_turn(self, player):
        pass

    @abc.abstractmethod
    def choose_target(self, targets):
        pass

    @abc.abstractmethod
    def choose_index(self, card, player):
        pass

    @abc.abstractmethod
    def choose_option(self, options, player):
        pass

    def filter_options(self, options, player):
        if isinstance(options[0], Card):
            return [option for option in options if option.can_choose(player)]
        return [option for option in options if option.card.can_choose(player)]


class DoNothingAgent(Agent):
    def __init__(self):
        self.game = None

    def do_card_check(self, cards):
        return [True, True, True, True]

    def do_turn(self, player):
        pass

    def choose_target(self, targets):
        return targets[0]

    def choose_index(self, card, player):
        return 0

    def choose_option(self, options, player):
        return self.filter_options(options, player)[0]


class PredictableAgent(Agent):
    def do_card_check(self, cards):
        return [True, True, True, True]

    def do_turn(self, player):
        done_something = True

        if player.hero.power.can_use():
            player.hero.power.use()

        if player.hero.can_attack():
            player.hero.attack()

        while done_something:
            done_something = False
            for card in player.hand:
                if card.can_use(player, player.game):
                    player.game.play_card(card)
                    done_something = True
                    break

        for minion in copy.copy(player.minions):
            if minion.can_attack():
                minion.attack()

    def choose_target(self, targets):
        return targets[0]

    def choose_index(self, card, player):
        return 0

    def choose_option(self, options, player):
        return self.filter_options(options, player)[0]


class RandomAgent(DoNothingAgent):
    def __init__(self, print=False):
        super().__init__()
        self.__print = print

    def do_card_check(self, cards):
        return [True, True, True, True]

    def do_turn(self, player):
        # print("Turn passed:%s"%player.game._turns_passed)
        while True:
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
                    if self.__print:
                        print(
                            "Agent action:" + player.name + "\t" + "use power->" + player.game.other_player.name + ':' + str(
                                player.game.other_player.hero.health))

                elif action < len(attack_minions):
                    attack_minions[action].attack()
                    if self.__print:
                        print(
                            "Agent action:" + player.name + "\t" + "attack->" + player.game.other_player.name + ':' + str(
                                player.game.other_player.hero.health))
                else:
                    player.game.play_card(playable_cards[action - len(attack_minions)])
                    if self.__print:
                        print("Agent action:" + player.name + "\t" + "play card->%s " % playable_cards[
                            action - len(attack_minions)] + player.game.other_player.name + ':' + str(
                            player.game.other_player.hero.health))
            else:
                return


class InnerRandomAgent(DoNothingAgent):
    def __init__(self, player, playername):
        super().__init__()
        self.__print = print
        self.player = player
        self.playername = playername
        self.output = True
        self.datatowrite=[]

    def setoutput(self, set):
        self.output = set

    def do_card_check(self, cards):
        return [True, True, True, True]

    def do_turn(self, player):
        while True:
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
            else:
                return

    def choose_target(self, targets):
        i = random.randint(0, len(targets) - 1)
        # print('\t'.join([t.card.name for t in targets]) + '\t'.join([str(t.health) for t in targets])+'\t%s'%i)
        if self.output and self.player.game.attackername != None:
            for n in range(8):
                if n < len(targets):
                    self.datatowrite.append(targets[n].card.name)
                    self.datatowrite.append(str(targets[n].health))
                else:
                    self.datatowrite.append('nocard')
                    self.datatowrite.append('0')
            self.datatowrite.append(self.player.game.attackername)
            self.datatowrite.append(str(self.player.game.attackerhealth))
            self.datatowrite.append(str(i))
            self.player.game.attackername = None
            self.player.game.attackerhealth = None

            # print('\t'.join(datatowrite) + '\t%s' % i)
            # trainlog.write('\t'.join(datatowrite) + '\t%s\n' % i)
            # trainlog.flush()
        return targets[i]

    def choose_index(self, card, player):
        return random.randint(0, len(player.minions))

    def choose_option(self, options, player):
        options = self.filter_options(options, player)
        return options[random.randint(0, len(options) - 1)]
