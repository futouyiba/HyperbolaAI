import socket
import sys
import traceback
import time

from hearthbreaker.agents.ai.uct.UCTAgent import SimpleUCTAgent
from hearthbreaker.cards.heroes import hero_for_class
from hearthbreaker.constants import CHARACTER_CLASS
from hearthbreaker.engine import Game, Deck, card_lookup
from hearthbreaker.serialization.serialization import serialize

ggame = None


def recvAll(conn):
    print('Recving from client ...')
    data = conn.recv(1024).decode('utf8')
    while data[-1] != '\0':
        data += conn.recv(1024).decode('utf8')
    print("Receive:" + data)
    return data[:-1]


def load_deck(filename):
    cards = []
    character_class = CHARACTER_CLASS.MAGE

    with open(filename, "r") as deck_file:
        contents = deck_file.read()
        items = contents.splitlines()
        for line in items[0:]:
            parts = line.split(" ", 1)
            count = int(parts[0])
            for i in range(0, count):
                card = card_lookup(parts[1])
                if card.character_class != CHARACTER_CLASS.ALL:
                    character_class = card.character_class
                cards.append(card)

    if len(cards) > 30:
        pass

    return Deck(cards, hero_for_class(character_class))


class OperationError(Exception):
    def __init__(self):
        Exception.__init__(self)


class WebAgent:
    def __init__(self, host, port):
        self.__soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__soc.bind((host, int(port)))
        self.__soc.listen(1)
        self.__conn, addr = self.__soc.accept()

    def reconnect(self):
        print('Do reconnect')
        self.__conn.close()
        self.__soc.close()
        time.sleep(3)

    def do_turn(self, player):
        global ggame
        action, playaction = self.choose_action()
        while not (action == "quit" or action == "endturn" or action == "restart"):
            res = 0
            if action == "play":
                card, res = self.choose_card(player, playaction)
                backupgame = player.game.copy(keep=True)
                if card is not None:
                    try:
                        player.game.play_card(card)
                    except OperationError:
                        ggame = backupgame
                        res = 0
            elif action == "attack":
                attacker, res = self.choose_attacker(player, playaction)
                backupgame = player.game.copy(keep=True)
                if attacker is not None:
                    try:
                        attacker.attack()
                    except OperationError:
                        ggame = backupgame
                        res = 0
            elif action == "power":
                res = 1
                backupgame = player.game.copy(keep=True)
                if player.hero.power.can_use():
                    try:
                        player.hero.power.use()
                    except OperationError:
                        ggame = backupgame
                        res = 0
            action, playaction = self.choose_action(res)
        if action == "quit" or action == "restart":
            raise ConnectionError()

    def choose_action(self, res=1):
        print("choose_action")
        global ggame
        self.__conn.send(bytes('''{"result":%s,"game":''' % res + serialize(ggame) + ''',"next":"choose_action"}\0''',
                               'utf8'))
        recv = recvAll(self.__conn)
        return recv[1:recv.rindex('/')], recv

    def choose_card(self, player, playaction):
        print("choose_card")
        filtered_cards = [card for card in filter(lambda card: card.can_use(player, player.game), player.hand)]
        if len(filtered_cards) is 0:
            return None, 0
        playname = playaction[playaction.rindex('/') + 1:]
        if 0 <= int(playname) < len(player.hand):
            print("Play card:" + player.hand[int(playname)].name)
            if player.hand[int(playname)].can_use(player, player.game):
                return player.hand[int(playname)], 1
            else:
                return None, 0
        else:
            return None, 0

    def choose_attacker(self, player, playaction):
        print("choose_attacker")
        filtered_attackers = [minion for minion in filter(lambda minion: minion.can_attack(), player.minions)]
        if player.hero.can_attack():
            filtered_attackers.append(player.hero)
        if len(filtered_attackers) is 0:
            return None, 0
        playname = playaction[playaction.rindex('/') + 1:]
        if 0 <= int(playname) < len(player.minions):
            if player.minions[int(playname)].can_attack():
                return player.minions[int(playname)], 1
            else:
                return None, 0
        else:
            return None, 0

    def do_card_check(self, cards):
        keeping = [True, True, True]
        if len(cards) > 3:
            keeping.append(True)
        return keeping

    def choose_target(self, targets):
        print("choose_target")
        if len(targets) is 0:
            print('Error? no targets available')
            raise OperationError()
        self.__conn.send(
            bytes('''{"result":1,"next":"choose_target","choose_from":[%s]}\0''' % serialize(targets), 'utf8'))
        # decision = recvAll(self.__conn)
        decision = self.__conn.recv(1024).decode('utf8')
        print(decision)
        # final = decision[decision.rindex('/') + 1:]
        final = decision[:-1]
        if 0 <= int(final) < len(targets):
            return targets[int(final)]
        else:
            raise OperationError()

    def choose_index(self, card, player):
        print("choose_index")
        self.__conn.send(bytes('''{"result":1,"next":"choose_index","choose_from":[%s]}\0''' % ','.join(
            [str(x) for x in range(len(player.minions) + 1)]), 'utf8'))
        # decision = recvAll(self.__conn)
        decision = self.__conn.recv(1024).decode('utf8')
        print(decision)
        # final = decision[decision.rindex('/') + 1:]
        final = decision[:-1]
        if 0 <= int(final) <= len(player.minions):
            return int(final)
        else:
            raise OperationError()

            # def choose_option(self, options, player):
            #     self.window.addstr(0, 0, "Choose option")
            #     index = 0
            #     selected = 0
            #     for option in options:
            #         if index == selected:
            #             color = curses.color_pair(4)
            #         else:
            #             color = curses.color_pair(3)
            #
            #         if isinstance(option, Card):
            #             self.text_window.addstr(0, index * 20, "{0:^19}".format(option.name[:19]), color)
            #         else:
            #             self.text_window.addstr(0, index * 20, "{0:^19}".format(option.card.name[:19]), color)
            #         index += 1
            #     self.window.refresh()
            #     self.text_window.refresh()
            #     ch = 0
            #     while ch != 10 and ch != 27:
            #         ch = self.game_window.getch()
            #         if ch == curses.KEY_LEFT:
            #             starting_selected = selected
            #             selected -= 1
            #             if selected < 0:
            #                 selected = len(options) - 1
            #             while not options[selected].can_choose(player) and selected != starting_selected:
            #                 selected -= 1
            #                 if selected < 0:
            #                     selected = len(options) - 1
            #         if ch == curses.KEY_RIGHT:
            #             starting_selected = selected
            #             selected += 1
            #             if selected == len(options):
            #                 selected = 0
            #             while not options[selected].can_choose(player) and selected != starting_selected:
            #                 selected += 1
            #                 if selected == len(options):
            #                     selected = 0
            #
            #         index = 0
            #         for option in options:
            #             if index == selected:
            #                 color = curses.color_pair(4)
            #             else:
            #                 color = curses.color_pair(3)
            #             if isinstance(option, Card):
            #                 self.text_window.addstr(0, index * 20, "{0:^19}".format(option.name[:19]), color)
            #             else:
            #                 self.text_window.addstr(0, index * 20, "{0:^19}".format(option.card.name[:19]), color)
            #             index += 1
            #         self.window.refresh()
            #         self.text_window.refresh()
            #     if ch == 27:
            #         return None
            #
            #     return options[selected]


if __name__ == '__main__':
    if len(sys.argv) < 3:
        port = int(sys.argv[2])
        print('Usage: COMMAND host port')
        sys.exit(1)
    deck1 = load_deck("zoo.hsdeck")
    deck2 = load_deck("zoo.hsdeck")
    logfile = open('hearthbreaker.log', 'a')
    while True:
        agent = WebAgent(sys.argv[1], sys.argv[2])
        ggame = Game([deck1, deck2], [(agent, "webagent"), (SimpleUCTAgent(0.2, 10), "uct")])
        try:
            ggame.start()
            agent.reconnect()
        except ConnectionResetError:
            logfile.write('Restart game due to connection reset\n')
            agent.reconnect()
        except Exception as e:
            traceback.print_exc(file=logfile)
            logfile.write('\n')
            agent.reconnect()
