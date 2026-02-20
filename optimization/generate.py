import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for v in self.domains:
            self.domains[v] = {word for word in self.domains[v] if len(word) == v.length}

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # following the pseudocode
        revised = False
        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            return False
        i, j = overlap
        to_remove = []

        for X in self.domains[x]:
            match_found = False
            for Y in self.domains[y]:
                if X[i] == Y[j]:
                    match_found = True
                    break

            if not match_found:
                to_remove.append(X)
                revised = True
        for word in to_remove:
            self.domains[x].remove(word)

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # create queue
        if arcs == None:
            queue = []
            for v1 in self.crossword.variables:
                for v2 in self.crossword.variables:
                    if v1 != v2:
                        overlap = self.crossword.overlaps[v1, v2]
                        if overlap is not None:
                            queue.append((v1, v2))
        else:
            queue = list(arcs)

        while len(queue) != 0:
            (x, y) = queue.pop(0)  # first element
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x):
                    if z != y:
                        queue.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for v in self.crossword.variables:
            if v not in assignment:
                return False
            if not assignment[v]:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # binary constraints (overlaps), unary constraints (correct lengths), must also be unique
        # check if they are unique
        words = list(assignment.values())
        if len(words) != len(set(words)):
            return False
        # check for correct lengths
        for v in assignment:
            if len(assignment[v]) != v.length:
                return False
        # check for overlaps
        for v1 in assignment:
            for v2 in assignment:
                if v1 != v2:
                    overlap = self.crossword.overlaps[v1, v2]
                    if overlap:
                        i, j = overlap
                        if assignment[v1][i] != assignment[v2][j]:
                            return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # least constraining value heuristic
        neighbors = self.crossword.neighbors(var)
        unassigned_neighbors = [n for n in neighbors if n not in assignment]

        counts = {}

        for value in self.domains[var]:
            ruled_out = 0
            for neighbor in unassigned_neighbors:
                overlap = self.crossword.overlaps[var, neighbor]
                i, j = overlap

                for neighbor_value in self.domains[neighbor]:
                    if value[i] != neighbor_value[j]:
                        ruled_out += 1

            counts[value] = ruled_out
        return sorted(self.domains[var], key=lambda val: counts[val])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_vars = [v for v in self.crossword.variables if v not in assignment]
        best_v = None
        min_remaining_vals = float("inf")  # can only go down
        max_degree = -1  # can only go up
        for v in unassigned_vars:
            num_vals = len(self.domains[v])
            degree = len(self.crossword.neighbors(v))
            if num_vals < min_remaining_vals:
                min_remaining_vals = num_vals
                max_degree = degree
                best_v = v
            elif num_vals == min_remaining_vals:
                if degree > max_degree:
                    max_degree = degree
                    best_v = v
        return best_v

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            if self.consistent({**assignment, var: value}):
                assignment[var] = value
                # keep a copy to restore later
                old_domains = {v: self.domains[v].copy() for v in self.domains}
                self.domains[var] = {value}
                if self.ac3(arcs=[(z, var) for z in self.crossword.neighbors(var)]):
                    result = self.backtrack(assignment)  # recursively go thorugh the function
                    if result is not None:
                        return result

                # if inference failed
                self.domains = old_domains
                del assignment[var]
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
