import socket
import sys
import traceback

from hearthbreaker.agents.ai.uct.UCTAgent import SimpleUCTAgent
from hearthbreaker.cards.heroes import hero_for_class
from hearthbreaker.constants import CHARACTER_CLASS
from hearthbreaker.engine import Game, Deck, card_lookup
from hearthbreaker.serialization.serialization import serialize

ggame = None


def recvAll(conn):
    data = conn.recv(1024).decode('utf8')
    while data[-1] != '\0':
        data += conn.recv(1024).decode('utf8')
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


class WebAgent:
    def __init__(self, host, port):
        self.__soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__soc.bind((host, int(port)))
        self.__soc.listen(1)
        self.__conn, addr = self.__soc.accept()

    def reconnect(self):
        self.__conn.close()
        self.__soc.close()
        raise ConnectionResetError()

    def do_turn(self, player):
        res = 1
        action, playaction = self.choose_action()
        while not (action == "quit" or action == "end"):
            if action == "play":
                card, res = self.choose_card(player, playaction)
                if card is not None:
                    player.game.play_card(card)
            elif action == "attack":
                attacker, res = self.choose_attacker(player, playaction)
                if attacker is not None:
                    attacker.attack()
            elif action == "power":
                if player.hero.power.can_use():
                    player.hero.power.use()
            self.choose_action(res)
        if action == "quit":
            sys.exit(0)

    def choose_action(self, res=1):
        global ggame
        self.__conn.send(bytes('''{"result":%s,"game":''' % res + serialize(ggame) + ''',"next":"choose_action"}\0''',
                               'utf8'))
        try:
            recv = recvAll(self.__conn)
        except ConnectionResetError:
            self.reconnect()
        return recv[1:recv.rindex('/')], recv

    def choose_card(self, player, playaction):
        filtered_cards = [card for card in filter(lambda card: card.can_use(player, player.game), player.hand)]
        if len(filtered_cards) is 0:
            return None, 0
        playname = playaction[playaction.rindex('/') + 1:]
        if 0 <= int(playname) < len(filtered_cards):
            return filtered_cards[int(playname)], 1
        else:
            return None, 0

    def choose_attacker(self, player, playaction):
        filtered_attackers = [minion for minion in filter(lambda minion: minion.can_attack(), player.minions)]
        if player.hero.can_attack():
            filtered_attackers.append(player.hero)
        if len(filtered_attackers) is 0:
            return None, 0
        playname = playaction[playaction.rindex('/') + 1:]
        if 0 <= int(playname) < len(filtered_attackers):
            return filtered_attackers[int(playname)], 1
        else:
            return None, 0

    def do_card_check(self, cards):
        keeping = [True, True, True]
        if len(cards) > 3:
            keeping.append(True)
        return keeping

    def choose_target(self, targets):

        if len(targets) is 0:
            return None

        return None
        #
        # def choose_index(self, card, player):
        #     renderer.selection_index = 0
        #     renderer.draw_game()
        #     self.window.addstr(0, 0, "Choose placement location")
        #     self.window.refresh()
        #     ch = 0
        #     while ch != 10 and ch != 27:
        #         ch = self.game_window.getch()
        #         if ch == curses.KEY_LEFT:
        #             renderer.selection_index -= 1
        #             if renderer.selection_index < 0:
        #                 renderer.selection_index = len(player.minions)
        #         if ch == curses.KEY_RIGHT:
        #             renderer.selection_index += 1
        #             if renderer.selection_index > len(player.minions):
        #                 renderer.selection_index = 0
        #         renderer.draw_game()
        #         self.window.refresh()
        #     index = renderer.selection_index
        #     renderer.selection_index = -1
        #     if ch == 27:
        #         return -1
        #
        #     return index
        #
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
        ggame = Game([deck1, deck2], [(WebAgent(sys.argv[1], sys.argv[2]), "webagent"), (SimpleUCTAgent(0.2, 10),
                                                                                         "uct")])
        try:
            ggame.start()
        except ConnectionResetError:
            logfile.write('Restart game due to connection reset\n')
        except Exception as e:
            traceback.print_exc(file=logfile)
            logfile.write('\n')
