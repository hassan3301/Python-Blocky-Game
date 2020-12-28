"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin.

=== Module Description ===

This file contains the hierarchy of player classes.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import random
import pygame

from block import Block
from goal import Goal, generate_goals

from actions import KEY_ACTION, ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, \
    SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PASS, PAINT, COMBINE

# Num moves = 7 0 - 6
ACTIONS = [ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, SWAP_HORIZONTAL,
           SWAP_VERTICAL, SMASH, PAINT, COMBINE]
SMART_ACTIONS = [ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, SWAP_HORIZONTAL,
                 SWAP_VERTICAL, SMASH, PAINT, COMBINE, PASS]


def create_players(num_human: int, num_random: int, smart_players: List[int]) \
        -> List[Player]:
    """Return a new list of Player objects.

    <num_human> is the number of human player, <num_random> is the number of
    random players, and <smart_players> is a list of difficulty levels for each
    SmartPlayer that is to be created.

    The list should contain <num_human> HumanPlayer objects first, then
    <num_random> RandomPlayer objects, then the same number of SmartPlayer
    objects as the length of <smart_players>. The difficulty levels in
    <smart_players> should be applied to each SmartPlayer object, in order.
    """

    player_list = []

    overall_num_players = num_human + num_random + len(smart_players)
    goals = generate_goals(overall_num_players)
    id_list = list(range(overall_num_players))

    for human_index in range(num_human):
        player_list.append(HumanPlayer(id_list[human_index],
                                       goals[human_index]))

    for random_index in range(num_random):
        player_list.append(RandomPlayer(id_list[num_human + random_index],
                                        goals[num_human + random_index]))

    for smart_index in range(len(smart_players)):
        player_list.append(SmartPlayer(id_list[num_human + num_random +
                                               smart_index],
                                       goals[num_human + num_random +
                                             smart_index],
                                       smart_players[smart_index]))

    return player_list


def _get_block(block: Block, location: Tuple[int, int], level: int) -> \
        Optional[Block]:
    """Return the Block within <block> that is at <level> and includes
    <location>. <location> is a coordinate-pair (x, y).

    A block includes all locations that are strictly inside of it, as well as
    locations on the top and left edges. A block does not include locations that
    are on the bottom or right edge.

    If a Block includes <location>, then so do its ancestors. <level> specifies
    which of these blocks to return. If <level> is greater than the level of
    the deepest block that includes <location>, then return that deepest block.

    If no Block can be found at <location>, return None.

    Preconditions:
        - 0 <= level <= max_depth
    """

    child_size = block._child_size()
    child_positions = block._children_positions()
    block_children = block.children

    if level == 0:
        return block
    else:
        # Left and top but not bottom and right.
        for i in range(len(block_children)):
            if child_positions[i][0] <= location[0] < (child_positions[i][0]
                                                       + child_size) \
                    and (child_positions[i][1]) <= location[1] < \
                    child_positions[i][1] + child_size:
                if level == 1:
                    return block_children[i]
                else:
                    return _get_block(block_children[i], location, level - 1)

    return None


def get_random_block(block: Block, random_block_level: int, random_child: int) \
        -> Block:
    """Returns a random block contained within block."""
    rc = random.randint(0, 3)

    if block.max_depth == 0 or random_block_level == 0 or not block.children:
        return block
    elif block.level == random_block_level:
        for c in range(len(block.children)):
            if c == random_child:
                return block.children[c]
    else:
        return get_random_block(block.children[rc],
                                random_block_level, random_child)

    return None



class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    id: int
    goal: Goal

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.id = player_id

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player.

        If no block is selected by the player, return None.
        """
        raise NotImplementedError

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event.
        """
        raise NotImplementedError

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a potential move to make on the game board.

        The move is a tuple consisting of a string, an optional integer, and
        a block. The string indicates the move being made (i.e., rotate, swap,
        or smash). The integer indicates the direction (i.e., for rotate and
        swap). And the block indicates which block is being acted on.

        Return None if no move can be made, yet.
        """
        raise NotImplementedError


def _create_move(action: Tuple[str, Optional[int]], block: Block) -> \
        Tuple[str, Optional[int], Block]:
    return action[0], action[1], block


class HumanPlayer(Player):
    """A human player.
    """
    # === Private Attributes ===
    # _level:
    #     The level of the Block that the user selected most recently.
    # _desired_action:
    #     The most recent action that the user is attempting to do.
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0
    _level: int
    _desired_action: Optional[Tuple[str, Optional[int]]]

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        Player.__init__(self, player_id, goal)

        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._desired_action = None

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player based on
        the position of the mouse on the screen and the player's desired level.

        If no block is selected by the player, return None.
        """
        mouse_pos = pygame.mouse.get_pos()
        block = _get_block(board, mouse_pos, self._level)

        return block

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the player based on
        the mapping in KEY_ACTION, as well as the W and S keys for changing
        the level.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_ACTION:
                self._desired_action = KEY_ACTION[event.key]
            elif event.key == pygame.K_w:
                self._level = max(0, self._level - 1)
                self._desired_action = None
            elif event.key == pygame.K_s:
                self._level += 1
                self._desired_action = None

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return the move that the player would like to perform. The move may
        not be valid.

        Return None if the player is not currently selecting a block.
        """
        block = self.get_selected_block(board)

        if block is None or self._desired_action is None:
            return None
        else:
            move = _create_move(self._desired_action, block)

            self._desired_action = None
            return move


class RandomPlayer(Player):
    """
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    _proceed: bool
    """
    _proceed: bool

    def __init__(self, player_id: int, goal: Goal) -> None:
        # TODO: Implement Me
        self._proceed = False
        Player.__init__(self, player_id, goal)

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid, randomly generated move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove
        else:
            can_make_move = False
            while not can_make_move:

                desired_action_index = random.randint(0, len(ACTIONS) - 1)
                # Create a copy of the board.
                board_copy = board.create_copy()
                max_depth = board.max_depth
                random_block_level = random.randint(0, max_depth)
                random_child = random.randint(0, 3)
                random_block = get_random_block \
                    (board_copy, random_block_level, random_child)

                if desired_action_index == 0:
                    if random_block.rotate(1):
                        actual_block = _get_block(board, random_block.position,
                                                  random_block.level)
                        move = _create_move(ACTIONS[0], actual_block)
                        can_make_move = True
                elif desired_action_index == 1:
                    if random_block.rotate(3):
                        actual_block = _get_block(board, random_block.position,
                                                  random_block.level)
                        move = _create_move(ACTIONS[1], actual_block)
                        can_make_move = True
                elif desired_action_index == 2:
                    if random_block.swap(0):
                        actual_block = _get_block(board, random_block.position,
                                                  random_block.level)
                        move = _create_move(ACTIONS[2], actual_block)
                        can_make_move = True
                elif desired_action_index == 3:
                    if random_block.swap(1):
                        actual_block = _get_block(board, random_block.position,
                                                  random_block.level)
                        move = _create_move(ACTIONS[3], actual_block)
                        can_make_move = True
                elif desired_action_index == 4:
                    if random_block.smash():
                        actual_block = _get_block(board, random_block.position,
                                                  random_block.level)
                        move = _create_move(ACTIONS[4], actual_block)
                        can_make_move = True
                elif desired_action_index == 5:
                    if random_block.paint(self.goal.colour):
                        actual_block = _get_block(board, random_block.position,
                                                  random_block.level)
                        move = _create_move(ACTIONS[5], actual_block)
                        can_make_move = True
                elif desired_action_index == 6:
                    if random_block.combine():
                        actual_block = _get_block(board, random_block.position,
                                                  random_block.level)
                        move = _create_move(ACTIONS[6], actual_block)
                        can_make_move = True

        self._proceed = False  # Must set to False before returning!
        return move


class SmartPlayer(Player):
    """
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    _proceed: bool
    """
    _proceed: bool
    difficulty: int
    def __init__(self, player_id: int, goal: Goal, difficulty: int) -> None:
        # TODO: Implement Me
        self._proceed = False
        Player.__init__(self, player_id, goal)
        self.difficulty = difficulty

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid move by assessing multiple valid moves and choosing
        the move that results in the highest score for this player's goal (i.e.,
        disregarding penalties).

        A valid move is a move other than PASS that can be successfully
        performed on the <board>. If no move can be found that is better than
        the current score, this player will pass.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove

        moves = []
        scores = []
        initial_score = self.goal.score(board)
        i = 0

        while i < self.difficulty:
            desired_action_index = random.randint(0, len(ACTIONS) - 1)
            # Create a copy of the board.
            # This is the copy.
            board_copy = board.create_copy()

            max_depth = board.max_depth
            random_block_level = random.randint(0, max_depth)
            random_child = random.randint(0, 3)

            # We get a random block from this copy.
            random_block = get_random_block \
                    (board_copy, random_block_level, random_child)

            if desired_action_index == 0:

                if random_block.rotate(1):

                    actual_block = _get_block(board, random_block.position,
                                              random_block.level)

                    move = _create_move(ACTIONS[0], actual_block)

                    moves.append(move)


                    random_block.rotate(1)
                    scores.append(self.goal.score(board_copy))

                    i += 1

            elif desired_action_index == 1:
                if random_block.rotate(3):
                    actual_block = _get_block(board, random_block.position,
                                              random_block.level)
                    move = _create_move(ACTIONS[1], actual_block)
                    moves.append(move)

                    random_block.rotate(3)
                    scores.append(self.goal.score(board_copy))

                    i += 1

            elif desired_action_index == 2:
                if random_block.swap(0):
                    actual_block = _get_block(board, random_block.position,
                                              random_block.level)
                    move = _create_move(ACTIONS[2], actual_block)
                    moves.append(move)

                    random_block.swap(0)
                    scores.append(self.goal.score(board_copy))
                    i += 1

            elif desired_action_index == 3:
                if random_block.swap(1):
                    actual_block = _get_block(board, random_block.position,
                                              random_block.level)
                    move = _create_move(ACTIONS[3], actual_block)
                    moves.append(move)

                    random_block.swap(1)
                    scores.append(self.goal.score(board_copy))

                    i += 1

            elif desired_action_index == 4:
                if random_block.smash():
                    actual_block = _get_block(board, random_block.position,
                                              random_block.level)
                    move = _create_move(ACTIONS[4], actual_block)
                    moves.append(move)

                    random_block.smash()
                    scores.append(self.goal.score(board_copy))

                    i += 1

            elif desired_action_index == 5:
                if random_block.paint(self.goal.colour):

                    actual_block = _get_block(board, random_block.position,
                                              random_block.level)
                    move = _create_move(ACTIONS[5], actual_block)
                    moves.append(move)

                    random_block.paint(self.goal.colour)
                    scores.append(self.goal.score(board_copy))

                    i += 1

            elif desired_action_index == 6:
                if random_block.combine():
                    actual_block = _get_block(board, random_block.position,
                                              random_block.level)
                    move = _create_move(ACTIONS[6], actual_block)
                    moves.append(move)

                    random_block.combine()
                    scores.append(self.goal.score(board_copy))
                    i += 1

        best_move_index = scores.index(max(scores))

        if max(scores) <= initial_score:
            self._proceed = False
            return _create_move(SMART_ACTIONS[7], board)
        else:
            self._proceed = False
            return moves[best_move_index]


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'actions', 'block',
            'goal', 'pygame', '__future__'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
