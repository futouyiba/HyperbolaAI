import json
import sys

from flask import Flask
from hearthbreaker.agents.ai.uct.UCTAgent import SimpleUCTAgent
from hearthbreaker.agents.basic_agents import RandomAgent
from hearthbreaker.cards.heroes import hero_for_class
from hearthbreaker.constants import CHARACTER_CLASS
from hearthbreaker.engine import Game, Deck, card_lookup
from hearthbreaker.serialization.serialization import serialize

app = Flask(__name__)
ggame = None


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
    def do_turn(self, player):
        index = 0
        action = self.choose_action()
        while not (action == "quit" or action == "end"):
            if action == "play":
                card = self.choose_card(player)
                if card is not None:
                    player.game.play_card(card)
            elif action == "attack":
                attacker = self.choose_attacker(player)
                if attacker is not None:
                    attacker.attack()
            elif action == "power":
                if player.hero.power.can_use():
                    player.hero.power.use()
            index += 1
            action = self.choose_action()
        if action == "quit":
            sys.exit(0)

    def choose_action(self):
        return None

        # def choose_card(self, player):
        #     filtered_cards = [card for card in filter(lambda card: card.can_use(player, player.game), player.hand)]
        #     if len(filtered_cards) is 0:
        #         return None
        #     renderer.targets = filtered_cards
        #     renderer.selected_target = renderer.targets[0]
        #     renderer.draw_game()
        #     self.window.addstr(0, 0, "Choose Card")
        #     self.window.refresh()
        #     ch = 0
        #     index = 0
        #     while ch != 10 and ch != 27:
        #         ch = self.game_window.getch()
        #
        #         if ch == curses.KEY_LEFT:
        #             index -= 1
        #             if index < 0:
        #                 index = len(renderer.targets) - 1
        #         if ch == curses.KEY_RIGHT:
        #             index += 1
        #             if index == len(renderer.targets):
        #                 index = 0
        #         renderer.selected_target = renderer.targets[index]
        #         renderer.draw_game()
        #         self.window.addstr(0, 0, "Choose Card")
        #         self.window.refresh()
        #     renderer.targets = None
        #     if ch == 27:
        #         return None
        #
        #     return renderer.selected_target
        #
        # def choose_attacker(self, player):
        #     filtered_attackers = [minion for minion in filter(lambda minion: minion.can_attack(), player.minions)]
        #     if player.hero.can_attack():
        #         filtered_attackers.append(player.hero)
        #     if len(filtered_attackers) is 0:
        #         return None
        #     renderer.targets = filtered_attackers
        #     renderer.selected_target = renderer.targets[0]
        #     renderer.draw_game()
        #     self.window.addstr(0, 0, "Choose attacker")
        #     self.window.refresh()
        #     ch = 0
        #     index = 0
        #     while ch != 10 and ch != 27:
        #         ch = self.game_window.getch()
        #         self.window.addstr(0, 0, "{0}".format(ch))
        #         self.window.refresh()
        #         if ch == curses.KEY_LEFT:
        #             index -= 1
        #             if index < 0:
        #                 index = len(renderer.targets) - 1
        #         if ch == curses.KEY_RIGHT:
        #             index += 1
        #             if index == len(renderer.targets):
        #                 index = 0
        #         renderer.selected_target = renderer.targets[index]
        #         renderer.draw_game()
        #         self.window.refresh()
        #     renderer.targets = None
        #     if ch == 27:
        #         return None
        #
        #     return renderer.selected_target
        #
    def do_card_check(self, cards):

         keeping = [True, True, True]
         if len(cards) > 3:
             keeping.append(True)
         return keeping
        #
        # def choose_target(self, targets):
        #
        #     if len(targets) is 0:
        #         return None
        #     renderer.targets = targets
        #     renderer.selected_target = renderer.targets[0]
        #     renderer.draw_game()
        #     self.window.addstr(0, 0, "Choose target")
        #     self.window.refresh()
        #     ch = 0
        #     index = 0
        #     while ch != 10 and ch != 27:
        #         ch = self.game_window.getch()
        #         if ch == curses.KEY_LEFT:
        #             index -= 1
        #             if index < 0:
        #                 index = len(renderer.targets) - 1
        #         if ch == curses.KEY_RIGHT:
        #             index += 1
        #             if index == len(renderer.targets):
        #                 index = 0
        #         renderer.selected_target = renderer.targets[index]
        #         renderer.draw_game()
        #         self.window.refresh()
        #     renderer.targets = None
        #     if ch == 27:
        #         return None
        #
        #     return renderer.selected_target
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
        #
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


@app.route("/newgame")
def do_stuff():
    global ggame
    deck1 = load_deck("zoo.hsdeck")
    deck2 = load_deck("zoo.hsdeck")
    '''Give agent object and play name'''
    game = Game([deck1, deck2], [(WebAgent(), "webagent"), (SimpleUCTAgent(0.2, 10), "uct")])
    ggame = game
    # game.start()
    res = """{"result": 1, "game": """+ serialize(game)+"}"
    return res


@app.route("/start")
def start_game():
    global ggame
    ggame.start()
    return json.dumps({"result": 1})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
