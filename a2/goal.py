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
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import math
import random
from typing import List, Tuple
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    binary_goal_decider = random.randint(0, 1)
    colour_index_list = []
    goal_list = []

    while len(colour_index_list) < num_goals:
        randi = random.randint(0, len(COLOUR_LIST) - 1)
        if randi not in colour_index_list:
            colour_index_list.append(randi)

    # Case of perimeter goal.
    if binary_goal_decider == 0:
        # For each randomly generated colour index, append a goal w/ said colour
        for colour_index in colour_index_list:
            goal_list.append(PerimeterGoal(COLOUR_LIST[colour_index]))
        return goal_list

    # Case of blob goal.
    else:
        for colour_index in colour_index_list:
            goal_list.append(BlobGoal(COLOUR_LIST[colour_index]))
        return goal_list


def add_blocks(block: Block, level: int) -> List[List]:
    """Takes in a block and generates new blocks until this block contains
    blocks that are unit cells. """

    if level == block.max_depth - 1:
        return [[block.colour, block.colour], [block.colour, block.colour]]
    else:
        sub_blocks = add_blocks(block, level + 1)
        return full_merge(sub_blocks, sub_blocks, sub_blocks, sub_blocks)


def full_merge(lst1: List[List], lst2: List[List], lst3: List[List],
               lst4: List[List]) -> List[List]:
    """Merge each square fully."""

    def merge(lst1: List[List], lst2: List[List]) -> List[List]:
        """Merge each square partially."""

        merged_list = []
        for i in range(len(lst1)):
            merged_list.append(lst1[i] + lst2[i])
        return merged_list

    def merge_rects(lst1: List[List], lst2: List[List]) -> List[List]:
        """Merge each rectangle."""
        merged = []
        for i in range(len(lst1)):
            merged.append(lst1[i])
        for j in range(len(lst2)):
            merged.append(lst2[j])

        return merged

    one_and_two = merge(lst1, lst2)
    three_and_four = merge(lst3, lst4)
    return merge_rects(one_and_two, three_and_four)


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """

    def flatten_helper(block: Block) -> List[List: Tuple]:
        """A helper for the flatten function."""
        # I ADDED BLOCK.LEVEL == BLOCK.MAX_DEPTH - 1
        # ---> and
        if len(block.children) == 4 and not block.children[0].children and \
                block.level == block.max_depth - 1 and not \
                block.children[1].children\
                and not block.children[2].children and not \
                block.children[3].children:
            return [[block.children[1].colour, block.children[2].colour],
                    [block.children[0].colour, block.children[3].colour]]
        else:
            if len(block.children) == 4:
                ordered_children = [block.children[1], block.children[2],
                                    block.children[0], block.children[3]]
            else:
                ordered_children = [block, block, block, block]
            sub_blocks = []
            for c in range(len(ordered_children)):
                if ordered_children[c].children == []:
                    sub_blocks.append(add_blocks(ordered_children[c],
                                                 ordered_children[c].level))

                else:
                    sub_blocks.append(flatten_helper(ordered_children[c]))

        return full_merge(sub_blocks[0], sub_blocks[1], sub_blocks[2],
                          sub_blocks[3])

    if block.max_depth == 0:
        return [[block.colour]]
    else:
        return flatten_helper(block)


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """A perimeter goal."""
    def score(self, board: Block) -> int:
        board = _flatten(board)
        score = 0
        if self.colour in board[0]:
            score += board[0].count(self.colour)
            if self.colour == board[0][0]:
                score += 1
            if self.colour == board[0][-1]:
                score += 1

        if self.colour in board[-1]:
            score += board[-1].count(self.colour)
            if self.colour == board[-1][0]:
                score += 1
            if self.colour == board[-1][-1]:
                score += 1

        for column_index in range(1, len(board) - 1):
            if self.colour in board[column_index]:
                if self.colour == board[column_index][0]:
                    score += 1
                if self.colour == board[column_index][-1]:
                    score += 1

        return score

    def description(self) -> str:

        return 'Get as many {} blocks as you can on the edges of the board.'.\
            format(colour_name(self.colour))


class BlobGoal(Goal):
    """A blob goal."""
    def score(self, board: Block) -> int:
        scores = []
        flat_board = _flatten(board)
        visited = []
        for j in range(len(flat_board)):
            visited.append([])
        for col in visited:
            for k in range(len(visited)):
                col.append(-1)
        i = 0
        for item in flat_board:
            for e in range(len(item)):
                scores.append(self._undiscovered_blob_size((i, e), flat_board,
                                                           visited))
            i += 1
        return max(scores)

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        if pos[0] < 0 or pos[0] > len(board) - 1 or pos[1] < 0 or pos[1] > \
                len(board) - 1:
            return 0
        elif board[pos[0]][pos[1]] != self.colour and \
                visited[pos[0]][pos[1]] == -1:
            visited[pos[0]][pos[1]] = 0
            return 0
        elif board[pos[0]][pos[1]] == self.colour and \
                visited[pos[0]][pos[1]] == -1:

            visited[pos[0]][pos[1]] = 1

            flat_list = []
            for sublist in board:
                for item in sublist:
                    flat_list.append(item)

            if len(set(flat_list)) == 1:
                return 4
            score = 1

            score += self._undiscovered_blob_size((pos[0] + 1, pos[1]), board,
                                                  visited)
            score += self._undiscovered_blob_size((pos[0], pos[1] + 1), board,
                                                  visited)
            score += self._undiscovered_blob_size((pos[0] - 1, pos[1]), board,
                                                  visited)
            score += self._undiscovered_blob_size((pos[0], pos[1] - 1), board,
                                                  visited)
            return score

        else:
            return 0











    def description(self) -> str:

        return 'Get as many {} blocks as you can in one giant blob.'.\
            format(colour_name(self.colour))


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
