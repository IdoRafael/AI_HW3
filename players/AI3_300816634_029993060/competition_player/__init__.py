
#===============================================================================
# Imports
#===============================================================================

import abstract
import players.AI3_300816634_029993060.improved_better_h_player as ibh


#===============================================================================
# Player
#===============================================================================

class Player(ibh.Player):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        super().__init__(setup_time, player_color, time_per_k_turns, k)

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'Original_Name_LOLZ0RZ')
