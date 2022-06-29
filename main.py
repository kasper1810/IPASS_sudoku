import random
from itertools import combinations


def read_puzzle(filename):
    '''
    reads the puzzle so it can be solved.
    :param filename: txt file which contains the puzzle the program needs to solve
    :return: set: cells(all 81 cells in a sudoku), dict: values(the given numbers in the cells),
    int row (the number of rows the sudoku has), int column (the number of columns the sudoku has)
    '''
    puzzel = open(filename, 'r')
    values = dict()
    cells = set()
    row = 0
    column = 0

    for regel in puzzel:
        regel = regel.rstrip()
        print(regel)
        row += 1
        column = 0
        elementen = regel.split()
        for element in elementen:
            column += 1
            cells.add((row, column))
            if int(element) == 0:
                values[(row, column)] = {0}
            else:
                values[(row, column)] = {int(element)}
    print('')
    return cells, values, row, column


def read_units(filename):
    '''
    reads the units where the number 1 till 9 need to come
    :param filename: txt file which contains all indexes of the cells in 1 unit
    :return: a dict with all units
    '''
    lines = open(filename, 'r')
    units = dict()

    for regel in lines:
        regel = regel.rstrip()
        unitcells = set()
        elementen = regel.split(',')
        naam = elementen.pop(0)
        for element in elementen:
            i, j = element.split('-')
            unitcells.add((int(i), int(j)))
        units[naam] = unitcells
    return units


def determine_neighbors(cells, units):
    '''
    determine for each cell all cells that have direct influence on it (cells in the same units: row, column, square)
    :param cells: all 81 cells in the sudoku
    :param units: all 36 units in the sudoku
    :return: dict neighbors with as key the cell and as values all other cells that have direct influence
    '''
    neighbors = dict()
    for cell in cells:
        neighborset = set()
        for name in units:
            if cell in units[name]:
                neighborset = neighborset | units[name]
        neighborset.discard(cell)
        neighbors[cell] = neighborset
    return neighbors


def related_cells(cells, neighbors):
    '''
    determine for a given collection of cells the collection
    # of cells that is influenced by it
    :param cells: all 81 cells in the sudoku
    :param neighbors: all neighbours of a cell
    :return: set with related cells en neighbours of a cell
    '''
    related_cells = set()
    init = True
    for cell in cells:
        if init:
            related_cells = neighbors[cell]
            init = False
        else:
            related_cells = related_cells & neighbors[cell]
    return related_cells


def printset(s, sep):
    # return members from set as string
    return sep.join(str(v) for v in s).replace(' ', ' ')


def print_puzzle(values, nrows, ncolumns):
    '''
    prints the puzzle
    :param values: all values (assigned numbers) in the puzzle
    :param nrows: all rows in the puzzle
    :param ncolumns: all columns in the puzzle
    :return: None
    '''
    # first determine column widths
    columnwidths = []
    for j in range(1, ncolumns + 1):
        kolombreedte = 0
        for i in range(1, nrows + 1):
            breedte = len(values[(i, j)]) + 1
            if breedte > kolombreedte:
                kolombreedte = breedte
        columnwidths.append(kolombreedte)
    printstring = "\n"
    for i in range(1, nrows + 1):
        for j in range(1, ncolumns + 1):
            printwaarde = '{message:{align}{width}}'.format(
                message=printset(values[(i, j)], ""),
                align='^',
                width=columnwidths[j - 1]
            )
            printstring += printwaarde
        printstring += "\n"

    print(printstring + "\n")
    return


def statusinfo():
    '''
    determines the total number of remaining possibilities of all cells if the total is 81 the puzzle is solved
    :return: int of total possibilities
    '''
    total = 0
    for cell in values:
        total += len(values[cell])
    return total


def determined_values(s):
    '''
    searches for determined possibilities in the cells
    :param s: set of cells
    :return: set of determined values in these cells
    '''
    possibilities = set()
    for cell in s:
        if len(values[cell]) == 1:
            possibilities.update(values[cell])
    return possibilities


def all_values(s):
    '''
    searches for all possibilities in the cells
    :param s: set of cells
    :return: set of values in these cells
    '''
    possibilities = set()
    for cell in s:
        possibilities.update(values[cell])
    return possibilities


def check_units():
    '''
    checks all units in the sudoku if there is a number that can only occur in one cell in the unit the number will be assigned to the spot
    :return: returns bool true if a number is assigned to a spot otherwise its false
    '''
    # iterate over all units
    for unit in units:
        unitcells = units[unit]
        for cell in unitcells:
            if len(values[cell]) == 1:
                continue
            remainder = unitcells.copy()
            remainder.remove(cell)
            remainingvalues = values[cell] - all_values(remainder)
            if len(remainingvalues) == 1:
                values[cell] = remainingvalues
                print("Determined cell " + str(cell) + ": " + printset(values[cell], "") + " (can be placed nowhere else in " + unit + ")")
                return True
    return False


def refresh():
    '''
    for each undetermined cell all possibilities will be searched for and all number that cannot be on that place be will
    eliminated if this leads to only 1 possibilty the number is determined and the process will be repeated.
    :return: 2 things get returned both are booleans. the first one is number skipped will be true if a possibility is eliminated (otherwise false)
    the second is number found will be true if a number gets determined (otherwise false).
    '''

    # return values
    number_found = False
    number_skipped = False

    # status
    found_something = True
    while (found_something):
        found_something = False
        for cell in cells:
            # only undetermined cells
            if len(values[cell]) > 1:
                neighborvalues = determined_values(neighbors[cell])
                commonvalues = values[cell] & neighborvalues
                remainingvalues = values[cell] - neighborvalues
                if len(commonvalues) > 0:
                    values[cell] = remainingvalues
                    number_skipped = True
                    if len(remainingvalues) == 1:
                        print(str(cell) + ' must be ' + printset(values[cell], ' '))
                        found_something = True
                        number_found = True
    return number_skipped, number_found


def skipper():
    '''
    when 2 cells with 2 possibilties where the possibilties are the same in both cells they can get removed from other cells in the same unit.
    :return: 2 things get returned both are booleans. the first one is number skipped will be true if a possibility is eliminated (otherwise false)
    the second is number found will be true if a number gets determined (otherwise false).
    '''

    number_found = False
    number_skipped = False

    for groepsgrootte in range(1, unit_size):
        # iterate over all units
        for unit in units:
            groepen = combinations(units[unit], groepsgrootte)
            # iterate over all combinations
            for subset in groepen:
                # determine union of all possible values in combination
                groep = set(subset)
                union_of_values = all_values(groep)
                if len(union_of_values) == groepsgrootte:
                    # we can skip all values in union from related cells
                    comment = "Number(s) " + printset(union_of_values, "") + " must be placed in " + printset(groep, "")
                    comment_printed = False
                    for cell in related_cells(groep, neighbors):
                        for number in union_of_values:
                            if number in values[cell]:
                                if not comment_printed:
                                    print(comment)
                                    comment_printed = True
                                print(str(number) + " removed from " + str(cell))
                                values[cell] = values[cell] - {number}
                                number_skipped = True
                                if len(values[cell]) == 1:
                                    print(str(cell) + " must be " + printset(values[cell], ""))
                                    number_found = True

                    if number_found:
                        return number_skipped, number_found

    return number_skipped, number_found


def skipper2():
    '''
    when n cells with n possibilties where the number of cells and possibilties are the same and the possibilities in those cells are the same.
    they can get removed from other cells in the same unit.
    :return: 2 things get returned both are booleans. the first one is number skipped will be true if a possibility is eliminated (otherwise false)
    the second is number found will be true if a number gets determined (otherwise false).
    '''
    number_found = False
    number_skipped = False

    for groepsgrootte in range(2, unit_size):
        # iterate over all units
        for unit in units:
            groepen = combinations(units[unit], groepsgrootte)
            # iterate over all combinations
            for subset in groepen:
                # determine union of all possible values in combination
                groep = set(subset)
                group_values = all_values(groep)
                complement = units[unit] - groep
                complement_values = all_values(complement)
                remainder = group_values - complement_values
                # we can skip all values in union from related cells
                comment = "Number(s) " + printset(remainder,
                                                  "") + " in unit " + unit + " must be placed somewhere in " + printset(
                    groep, "")
                comment_printed = False
                for cell in related_cells(groep, neighbors):
                    for number in remainder:
                        if number in values[cell]:
                            if not comment_printed:
                                print(comment)
                                comment_printed = True
                            print(str(number) + " removed from " + str(cell))
                            values[cell] = values[cell] - {number}
                            number_skipped = True
                            if len(values[cell]) == 1:
                                print(str(cell) + " must be " + printset(values[cell], ""))
                                number_found = True

                if number_found:
                    return number_skipped, number_found

    return number_skipped, number_found


def solve_puzzle():
    '''
    program tries to solve the puzzle as far as he can until the puzzle is done
    this function uses all the other functions
    :return: int statusinfo()
    '''
    refresh_calls = 0
    check_units_calls = 0
    skipper_calls = 0
    skipper2_calls = 0

    while True:

        refresh_calls += 1
        number_skipped, number_found = refresh()
        if number_skipped:
            if number_found:
                print_puzzle(values, n_rows, n_columns)
            continue

        aantal_gevonden = statusinfo()
        if aantal_gevonden == n_rows * n_columns:
            break

        check_units_calls += 1
        number_found = check_units()
        if number_found:
            print_puzzle(values, n_rows, n_columns)
            continue

        skipper_calls += 1
        number_skipped, number_found = skipper()
        if number_skipped:
            print_puzzle(values, n_rows, n_columns)
            continue

            # nrc_11
        skipper2_calls += 1
        number_skipped, number_found = skipper2()
        if number_skipped:
            print_puzzle(values, n_rows, n_columns)
            continue

        break

    print("refresh_calls     :", refresh_calls)
    print("check_units_calls :", check_units_calls)
    print("skipper_calls     :", skipper_calls)
    print("skipper2_calls    :", skipper2_calls)

    return statusinfo()


#########################
# main program          #
#########################


cells, values, n_rows, n_columns = read_puzzle('sudoku_input2.txt')
print(cells)
units = read_units('units.txt')
print(units)
neighbors = determine_neighbors(cells, units)

# determine unit_size
unit_size = len(units[random.choice(list(units.keys()))])
allvalues = set(range(1, unit_size + 1))

row_occurence = n_columns // unit_size
column_occurence = n_rows // unit_size

print('Number of rows        : ', n_rows)
print('Number of columns     : ', n_columns)
print('Size of units         : ', unit_size)
print('Row multiplicity      : ', row_occurence)
print('Column multiplicity   : ', column_occurence)
print('')

for cell in cells:
    if values[cell] == {0}:
        values[cell] = allvalues

totaal = solve_puzzle()

print('')


if totaal == n_rows * n_columns:
    print('Solved!')
else:
    print('Unsolved....')