from typing import Tuple


class FortuneWheel:
    def __init__(self):
        self.games = {}

    def donate(self, donation: Tuple[str, float]):
        game_name, game_score = donation

        if game_name in self.games:
            self.games[game_name] += game_score
        else:
            self.games[game_name] = game_score

    def get_games_with_probabilities(self):
        if len(self.games) == 0:
            raise ConnectionError("Games list is empty")

        games_sum = sum(self.games.values())

        games_with_probabilities = {
            game: score / games_sum for game, score in self.games.items()
        }
        return games_with_probabilities
