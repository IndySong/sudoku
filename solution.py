assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI')
                for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)
diag_boxes_lst = [[x + y for (x, y) in zip(rows, cols)], [x + y
                  for (x, y) in zip(rows, cols[::-1])]]

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
    Args: values(dict) - a dictionary of the form {'box_name': '123456789', ...}
    Returns: the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    for unit in unitlist + diag_boxes_lst:
        twins = set()
        temp_dct = dict() #key: value of the box, value: box index
        for box in unit:
            if values[box] not in temp_dct:
                temp_dct[values[box]] = [box]
            else:
                temp_dct[values[box]].append(box)
        for key, value in temp_dct.items():
            if len(value) > 1:
                for box in unit:
                    if box not in temp_dct[key]:
                        values[box].replace(key, '')
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args: grid(string) - A grid in string form.
    Returns: A grid in dictionary form
             Keys: The boxes, e.g., 'A1'
             Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    values = []
    all_digits = '123456789'
    for c in grid:
        if c == '.':
            values.append(all_digits)
        else:
            values.append(c)
    return dict(zip(boxes, values))

def display(values):
    """
    Display the values as a 2-D grid.
    Args: The sudoku in dictionary form
    Returns: None
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)] * 3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    Eliminate values from peers (including diagonal peers) of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    In addition, whenever there is a box on the diagonals with a single value,
    eliminate this value from the corresponding diagonal peers.

    Moreover, eliminate values using naked twins strategy.

    Args: values - Sudoku in dictionary form.
    Returns: resulting Sudoku in dictionary form after eliminating values.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for solved_box in solved_values:
        digit = values[solved_box]
        for peer in peers[solved_box]:
            values[peer] = values[peer].replace(digit, '')
        for diag_boxes in diag_boxes_lst:
            if solved_box in diag_boxes:
                for diag_box in diag_boxes:
                    if diag_box != solved_box:
                        values[diag_box] = values[diag_box].replace(digit, '')

    return naked_twins(values)

def only_choice(values):
    """
    Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Args: Sudoku in dictionary form.
    Returns: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        for digit in '123456789':
            potential_boxes = [box for box in unit if digit in values[box]]
            if len(potential_boxes) == 1:
                values[potential_boxes[0]] = digit
    return values

def reduce_puzzle(values):
    """
    Use Eliminate Strategy, Only Choice Strategy, & Naked Twins Strategy

    Args: Sudoku in dictionary form.
    Returns: Resulting Sudoku in dictionary form after eliminating invalid
             choice and filling in only choices.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if
                                   len(values[box]) == 1])

        # Your code here: Use the Eliminate Strategy
        values = eliminate(values)

        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if
                                  len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero
        # available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Using depth-first search and propagation, create a search tree and solve
    the sudoku.
    Args: Sudoku in dictionary form.
    Returns: A solution of the Sudoku puzzle in dictionary form if it exists.
             Otherwise, False.
    """
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if not values:
        return False ## Failed earlier
    if all(len(values[box]) == 1 for box in boxes):
        return values ## Solved!

    # Choose one of the unfilled squares with the fewest possibilities
    n, box = min((len(values[box]), box) for box in boxes
                 if len(values[box]) > 1)

    # Now use recursion to solve each one of the resulting sudokus,
    # and if one returns a value (not False), return that answer!
    for value in values[box]:
        new_sudoku = values.copy()
        new_sudoku[box] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """

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
