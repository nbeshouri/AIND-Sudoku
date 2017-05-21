assignments = []


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """
    Eliminate values using the naked twins strategy.

    If you have n boxes in a unit that can only be exactly the same n digits,
    you can't use those digits anywhere else in the unit. If you tried, you'd
    end up with one of the n boxes either empty or duplicating another box in the
    unit. So, unless the board is invalid, we can safely remove the n digits
    as possibilities for the rest of the boxes in the unit.

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    for unit in unitlist:
        # Create a mapping of digits to all boxes in the unit that contain them.
        digits_to_boxes = {}
        for box in unit:
            box_list = digits_to_boxes.setdefault(values[box], [])
            box_list.append(box)
        # Remove the twins' digits from the other boxes in the unit.
        for digits, box_list in digits_to_boxes.items():
            if len(digits) > 1 and len(box_list) == len(digits):
                for digit in digits:
                    for box in unit:
                        if box not in box_list and digit in values[box]:
                            assign_value(values, box, values[box].replace(digit, ''))
    return values

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a + b for a in A for b in B]

rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
diag_units = [[rows[i] + cols[i] for i in range(9)], [rows[i] + cols[8 - i] for i in range(9)]]
unitlist = row_units + column_units + square_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.

    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    values = []
    all_digits = '123456789'
    for c in grid:
        if c == '.':
            values.append(all_digits)
        elif c in all_digits:
            values.append(c)
    assert len(values) == 81
    return dict(zip(boxes, values))

def display(values):
    """
    Display the values as a 2-D grid.

    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_boxes = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_boxes:
        if len(values[box]) == 1:
            target = values[box]
            for peer in peers[box]:
                assign_value(values, peer, values[peer].replace(target, ''))
    return values

def only_choice(values):
    """
    Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Args:
        Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        for digit in '123456789':
            boxes_in_unit = [box for box in unit if digit in values[box]]
            if len(boxes_in_unit) == 1:
                assign_value(values, boxes_in_unit[0], digit)
    return values

def reduce_puzzle(values):
    """
    Iteratively simplify the puzzle.

    Args:
        Sudoku in dictionary form.
    Returns:
        The reduced sudoku if reduction was possible, otherwise False.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Using depth-first search, try all possible solutions.

    Args:
        Sudoku in dictionary form.
    Returns:
        The solved sudoku if solution is possible, otherwise False.
    """
    # First, reduce the puzzle using the previous function.
    values = reduce_puzzle(values)
    # Not all boards in the search tree are valid, so reduce() can fail.
    if not values:
        return False
    # Find unsolved boxes.
    undecided_boxes = [box for box in boxes if len(values[box]) > 1]
    # If there aren't any, we're done.
    if not undecided_boxes:
        return values
    _, best_box = min((len(values[box]), box) for box in undecided_boxes)
    # Now use recursion to solve each one of the resulting sudokus,
    # and if one returns a value (not False), return that answer!
    for digit in values[best_box]:
        new_values = values.copy()
        assign_value(new_values, best_box, digit)
        new_values = search(new_values)
        if new_values:
            return new_values

def solve(grid):
    """
    Find the solution to a Sudoku grid.

    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
