
#===============================================================================
# Imports
#===============================================================================

import abstract
import players.simple_player as simple_player
from utils import INFINITY
from checkers.consts import EM, BK, RK, RP, BP, PAWN_COLOR, KING_COLOR, OPPONENT_COLOR, MAX_TURNS_NO_JUMP, \
    OPPONENT_COLORS, BACK_ROW
from collections import defaultdict
from checkers.moves import GameMove, PAWN_SINGLE_MOVES, KING_SINGLE_MOVES, PAWN_CAPTURE_MOVES, KING_CAPTURE_MOVES
from math import hypot

#===============================================================================
# Globals
#===============================================================================

PAWN_WEIGHT = 40
PAWN_MOVE_WEIGHT = 3
PAWN_LOC_WEIGHT = 1
KING_WEIGHT = 60
KING_MOVE_WEIGHT = 2
KING_LOC_WEIGHT = 1.3
LOC_BONUS = {
    RP: {
        (0, 0): 4, (0, 1): 0, (0, 2): 4, (0, 3): 0, (0, 4): 4, (0, 5): 0, (0, 6): 4, (0, 7): 0,
        (1, 0): 0, (1, 1): 3, (1, 2): 0, (1, 3): 3, (1, 4): 0, (1, 5): 3, (1, 6): 0, (1, 7): 3,
        (2, 0): 2, (2, 1): 0, (2, 2): 2, (2, 3): 0, (2, 4): 2, (2, 5): 0, (2, 6): 2, (2, 7): 0,
        (3, 0): 0, (3, 1): 3, (3, 2): 0, (3, 3): 3, (3, 4): 0, (3, 5): 3, (3, 6): 0, (3, 7): 3,
        (4, 0): 2, (4, 1): 0, (4, 2): 4, (4, 3): 0, (4, 4): 4, (4, 5): 0, (4, 6): 4, (4, 7): 0,
        (5, 0): 0, (5, 1): 5, (5, 2): 0, (5, 3): 5, (5, 4): 0, (5, 5): 5, (5, 6): 0, (5, 7): 2,
        (6, 0): 6, (6, 1): 0, (6, 2): 6, (6, 3): 0, (6, 4): 6, (6, 5): 0, (6, 6): 6, (6, 7): 0,
        (7, 0): 0, (7, 1): 7, (7, 2): 0, (7, 3): 7, (7, 4): 0, (7, 5): 7, (7, 6): 0, (7, 7): 7,
    },
    RK: {
        (0, 0): 1, (0, 1): 0, (0, 2): 1, (0, 3): 0, (0, 4): 1, (0, 5): 0, (0, 6): 1, (0, 7): 0,
        (1, 0): 0, (1, 1): 3, (1, 2): 0, (1, 3): 3, (1, 4): 0, (1, 5): 3, (1, 6): 0, (1, 7): 1,
        (2, 0): 1, (2, 1): 0, (2, 2): 5, (2, 3): 0, (2, 4): 5, (2, 5): 0, (2, 6): 5, (2, 7): 0,
        (3, 0): 0, (3, 1): 7, (3, 2): 0, (3, 3): 7, (3, 4): 0, (3, 5): 7, (3, 6): 0, (3, 7): 1,
        (4, 0): 1, (4, 1): 0, (4, 2): 7, (4, 3): 0, (4, 4): 7, (4, 5): 0, (4, 6): 7, (4, 7): 0,
        (5, 0): 0, (5, 1): 5, (5, 2): 0, (5, 3): 5, (5, 4): 0, (5, 5): 5, (5, 6): 0, (5, 7): 1,
        (6, 0): 1, (6, 1): 0, (6, 2): 3, (6, 3): 0, (6, 4): 3, (6, 5): 0, (6, 6): 3, (6, 7): 0,
        (7, 0): 0, (7, 1): 1, (7, 2): 0, (7, 3): 1, (7, 4): 0, (7, 5): 1, (7, 6): 0, (7, 7): 1,
    }
}
LOC_BONUS[BP] = {(i, j): (LOC_BONUS[RP])[(7 - i, 7 - j)]
                 for (i, j) in LOC_BONUS[RP]}
LOC_BONUS[BK] = {(i, j): (LOC_BONUS[RK])[(7 - i, 7 - j)]
                 for (i, j) in LOC_BONUS[RK]}
DISTANCE_BONUS = 10
DISTANCE_WEIGHT = 10

#===============================================================================
# Player
#===============================================================================

class Player(simple_player.Player):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        super().__init__(setup_time, player_color, time_per_k_turns, k)

    def utility(self, state):
        # (1) piece count,
        # (2) kings count,
        # (3) trapped kings,
        # (4) turn,
        # (5) runaway checkers (unimpeded path to king);
        # (6) opening moves:
        # http://www.checkersgames.net/checkers-strategy/
        # and other minor factors
        # (7)   http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.39.742&rep=rep1&type=pdf
        #       http://stackoverflow.com/questions/20901882/best-ai-approach-for-game-draught-chekers

        if len(state.get_possible_moves()) == 0:
            return INFINITY if state.curr_player != self.color else -INFINITY
        if state.turns_since_last_jump >= MAX_TURNS_NO_JUMP:
            return 0

        piece_counts = defaultdict(lambda: 0)
        location_bonus = defaultdict(lambda: 0)
        unit_location = {RP: set(), RK: set(), BP: set(), BK: set(), }

        for loc in state.board:
            loc_val = state.board[loc]
            if loc_val != EM:
                piece_counts[loc_val] += 1
                location_bonus[loc_val] += LOC_BONUS[loc_val][loc]
                if loc_val == RK or loc_val == BK:
                    unit_location[loc_val].add(loc)

        opponent_color = OPPONENT_COLOR[self.color]

        my_u = ((PAWN_WEIGHT * piece_counts[PAWN_COLOR[self.color]]) +
                (KING_WEIGHT * piece_counts[KING_COLOR[self.color]]))
        op_u = ((PAWN_WEIGHT * piece_counts[PAWN_COLOR[opponent_color]]) +
                (KING_WEIGHT * piece_counts[KING_COLOR[opponent_color]]))
        if my_u == 0:
            # I have no tools left
            return -INFINITY
        elif op_u == 0:
            # The opponent has no tools left
            return INFINITY

        my_kings_distance_bonus = 0
        op_kings_distance_bonus = 0
        my_location_bonus = 0
        op_location_bonus = 0

        if (state.turns_since_last_jump > 12 or
                (piece_counts[PAWN_COLOR[self.color]] + piece_counts[KING_COLOR[self.color]] < 8
                 and piece_counts[PAWN_COLOR[opponent_color]] + piece_counts[KING_COLOR[opponent_color]] < 8)):
            # endgame - try to minimize distance
            if piece_counts[KING_COLOR[self.color]] > 0:
                my_kings_average_distance = find_kings_min_distances_sum(self.color, unit_location) / piece_counts[KING_COLOR[self.color]]
                if my_kings_average_distance > 0:
                    my_kings_distance_bonus = ((state.turns_since_last_jump / MAX_TURNS_NO_JUMP) *
                                               DISTANCE_WEIGHT * (DISTANCE_BONUS - my_kings_average_distance))

            if piece_counts[KING_COLOR[opponent_color]] > 0:
                op_kings_average_distance = find_kings_min_distances_sum(opponent_color, unit_location) / piece_counts[KING_COLOR[opponent_color]]
                if op_kings_average_distance > 0:
                    op_kings_distance_bonus = ((state.turns_since_last_jump / MAX_TURNS_NO_JUMP) *
                                               DISTANCE_WEIGHT * (DISTANCE_BONUS - op_kings_average_distance))

        my_location_bonus = ((PAWN_LOC_WEIGHT * location_bonus[KING_COLOR[self.color]]) +
                             (KING_LOC_WEIGHT * location_bonus[KING_COLOR[self.color]]))
        op_location_bonus = ((PAWN_LOC_WEIGHT * location_bonus[KING_COLOR[opponent_color]]) +
                             (KING_LOC_WEIGHT * location_bonus[KING_COLOR[opponent_color]]))

        my_pawn_moves, my_king_moves = calc_all_moves(state, state.curr_player)
        op_pawn_moves, op_king_moves = calc_all_moves(state, opponent_color)

        # mobility
        my_mobility = PAWN_MOVE_WEIGHT * len(my_pawn_moves) + KING_MOVE_WEIGHT * len(my_king_moves)
        op_mobility = PAWN_MOVE_WEIGHT * len(op_pawn_moves) + KING_MOVE_WEIGHT * len(op_king_moves)

        # runaway checkers
        # for move in my_pawn_moves:
        #     row_distance = abs(move.target_loc[0] - BACK_ROW[self.color])
        #     if (row_distance == 0 or
        #             (row_distance == 1 and (st)))
        #
        # for move in op_pawn_moves:
        # for all available pawn moves - if target_loc passed enemy lines and clear line to kinghood, add bonus

        return ((my_u + my_mobility + my_location_bonus + my_kings_distance_bonus) -
                (op_u + op_mobility + op_location_bonus + op_kings_distance_bonus))

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'better_h')

#===============================================================================
# Auxiliary Functions
#===============================================================================


def calc_single_moves(state, player):
    """Calculating all the possible single moves for @player.
    :return: All the legitimate single moves for this game state, if @player was the current player.
    """
    single_pawn_moves = [GameMove(state.board[i], i, j)
                         for (i, js) in PAWN_SINGLE_MOVES[player].items()
                         if state.board[i] == PAWN_COLOR[player]
                         for j in js
                         if state.board[j] == EM]
    single_king_moves = [GameMove(state.board[i], i, j)
                         for (i, js) in KING_SINGLE_MOVES.items()
                         if state.board[i] == KING_COLOR[player]
                         for j in js
                         if state.board[j] == EM]
    return single_pawn_moves, single_king_moves


def calc_capture_moves(state, player):
    """Calculating all the possible capture moves, but only the first step.
    :return: All the legitimate single capture moves for this game state.
    """
    capture_pawn_moves = [(i, j, k)
                          for i, i_capts in PAWN_CAPTURE_MOVES[player].items()
                          if state.board[i] == PAWN_COLOR[player]
                          for j,k in i_capts
                          if state.board[j] in OPPONENT_COLORS[player]
                          and state.board[k] == EM]
    capture_king_moves = [(i, j, k)
                          for i, i_capts in KING_CAPTURE_MOVES.items()
                          if state.board[i] == KING_COLOR[player]
                          for j,k in i_capts
                          if state.board[j] in OPPONENT_COLORS[player]
                          and state.board[k] == EM]
    return capture_pawn_moves, capture_king_moves


def calc_all_moves(state, player):
    single_pawn_moves, single_king_moves = calc_single_moves(state, player)
    capture_pawn_moves, capture_king_moves = calc_capture_moves(state, player)
    return single_pawn_moves + capture_pawn_moves, single_king_moves + capture_king_moves


def distance(loc1, loc2):
    return hypot(loc2[0] - loc1[0], loc2[1] - loc1[1])


def find_kings_min_distances_sum(player, unit_location):
    opponent_color = OPPONENT_COLOR[player]
    return sum(
        min(
            (distance(king, unit) for unit in
             unit_location[PAWN_COLOR[opponent_color]].union(unit_location[KING_COLOR[opponent_color]]))
            , default=0) for king in unit_location[KING_COLOR[player]]
    )

