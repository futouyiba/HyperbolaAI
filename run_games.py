import json
import timeit

from hearthbreaker.agents.ai.uct.UCTAgent import SimpleUCTAgent
from hearthbreaker.agents.trade_agent import TradeAgent
from hearthbreaker.agents.basic_agents import RandomAgent
from hearthbreaker.cards.heroes import hero_for_class
from hearthbreaker.constants import CHARACTER_CLASS
from hearthbreaker.engine import Game, Deck, card_lookup


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


_totalPlay = 1
_totalCount = 0.0


def do_stuff():
    global _totalTry
    _count = 0

    def play_game():
        global _totalCount
        nonlocal _count
        _count += 1
        new_game = game.copy()
        try:
            new_game.start()
        except Exception as e:
            print(json.dumps(new_game.__to_json__(), default=lambda o: o.__to_json__(), indent=1))
            print(new_game._all_cards_played)
            raise e

        if new_game.playersInOrder[0].hero.dead and new_game._turns_passed < 50:
            _totalCount += 1.0
        del new_game

        if _count % 1000 == 0:
            print("---- game #{} ----".format(_count))

    deck1 = load_deck("zoo.hsdeck")
    deck2 = load_deck("zoo.hsdeck")
    '''Give agent object and play name'''
    game = Game([deck1, deck2], [(TradeAgent(), "opponent"), (SimpleUCTAgent(0.2, 10), "uct")])
    # game = Game([deck1, deck2], [(UCTAgent.SimpleUCTAgent(0.1,100),"opponent"), (UCTAgent.SimpleUCTAgent(0.2,100),
    #                                                                              "uct")])

    print(timeit.timeit(play_game, 'gc.enable()', number=_totalPlay))
    print("uct win rate:%0.2f" % (_totalCount / _totalPlay))


if __name__ == "__main__":
    do_stuff()
