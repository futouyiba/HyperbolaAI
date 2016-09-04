import json

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


@app.route("/newgame")
def do_stuff():
    global ggame
    deck1 = load_deck("zoo.hsdeck")
    deck2 = load_deck("zoo.hsdeck")
    '''Give agent object and play name'''
    game = Game([deck1, deck2], [(RandomAgent(), "opponent"), (SimpleUCTAgent(0.2, 10), "uct")])
    ggame = game
    # game.start()
    res = {"result": 1, "game": serialize(game)}
    return json.dumps(res)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
