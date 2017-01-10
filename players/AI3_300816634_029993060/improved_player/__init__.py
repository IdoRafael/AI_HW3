
#===============================================================================
# Imports
#===============================================================================

import abstract
import players.simple_player as simple_player

#===============================================================================
# Player
#===============================================================================

class Player(simple_player.Player):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        super().__init__(setup_time, player_color, time_per_k_turns, k)

    def selective_deepening_criterion(self, state):
        # deepen if jump move available
        possible_moves = state.get_possible_moves()
        return len(possible_moves) > 0 and len(possible_moves[0].jumped_locs) > 0

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'improved')
