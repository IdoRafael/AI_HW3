
#===============================================================================
# Imports
#===============================================================================

import abstract
import players.AI3_300816634_029993060.better_h_player as better_h

#===============================================================================
# Player
#===============================================================================


class Player(better_h.Player):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        super().__init__(setup_time, player_color, time_per_k_turns, k)

    def selective_deepening_criterion(self, state):
        # deepen if jump move available
        possible_moves = state.get_possible_moves()
        return len(possible_moves) > 0 and len(possible_moves[0].jumped_locs) > 0

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'improved_better_h')
