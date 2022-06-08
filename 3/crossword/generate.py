import sys
import math

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
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        # Enforce node and arc consistency, and then solve the CSP.
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        # Update `self.domains` such that each variable is node-consistent.
        # (Remove any values that are inconsistent with a variable's unary
        # constraints; in this case, the length of the word.)
        for word in self.domains:
            length = word.length
            newDomain = set()
            for var in self.domains[word]:
                if len(var) == length:
                    newDomain.add(var)
            self.domains[word] = newDomain.copy()

    def revise(self, x, y):
        # Make variable `x` arc consistent with variable `y`.
        # To do so, remove values from `self.domains[x]` for which there is no
        # possible corresponding value for `y` in `self.domains[y]`.

        # Return True if a revision was made to the domain of `x`; return
        # False if no revision was made.
        revised = False
        newDomain = self.domains[x].copy()
        overlap = self.crossword.overlaps[x, y]
        yletters = set()
        for yvar in self.domains[y]:
            yletters.add(yvar[overlap[1]])
        for xvar in newDomain:
            if xvar[overlap[0]] not in yletters:
                self.domains[x].remove(xvar)
                revised = True
        return revised

    def ac3(self, arcs=None):
        # Update `self.domains` such that each variable is arc consistent.
        # If `arcs` is None, begin with initial list of all arcs in the problem.
        # Otherwise, use `arcs` as the initial list of arcs to make consistent.

        # Return True if arc consistency is enforced and no domains are empty;
        # return False if one or more domains end up empty.
        arcscopy = []
        if arcs == None:
            for x in self.domains:
                for y in self.domains:
                    if (x != y) and (y in self.crossword.neighbors(x)):
                        arcscopy.append((x, y))

        while len(arcscopy) != 0:
            arc = arcscopy.pop(0)
            if self.revise(arc[0], arc[1]):
                if self.domains[arc[0]] == 0:
                    return False
                else:
                    neighbors = self.crossword.neighbors(arc[0])
                    neighbors.remove(arc[1])
                    for z in neighbors:
                        arcscopy.append((z, arc[0]))
        return True

    def assignment_complete(self, assignment):
        # Return True if `assignment` is complete (i.e., assigns a value to each
        # crossword variable); return False otherwise.
        varcount = 0
        for var in assignment:
            varcount += 1
            if assignment[var] == None:
                return False
        if varcount == len(self.crossword.variables):
            return True
        return False

    def consistent(self, assignment):
        # Return True if `assignment` is consistent (i.e., words fit in crossword
        # puzzle without conflicting characters); return False otherwise.
        values = []
        for var in assignment:
            val = assignment[var]
            if val in values:
                return False
            values.append(val)
            if var.length != len(val):
                return False
            neighbors = self.crossword.neighbors(var)
            for z in neighbors:
                if z in assignment:
                    current = assignment[z]
                    overlap = self.crossword.overlaps[var, z]
                    if val[overlap[0]] != current[overlap[1]]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        # Return a list of values in the domain of `var`, in order by
        # the number of values they rule out for neighboring variables.
        # The first value in the list, for example, should be the one
        # that rules out the fewest values among the neighbors of `var`.
        orderedlist = [[word, 0] for word in list(self.domains[var])]
        includedNVars = []
        for x in self.crossword.variables:
            if x not in list(assignment.keys()) and x in list(self.crossword.neighbors(var)):
                includedNVars.append(x)
        checklist = [[list(self.domains[Nvar]), list(self.crossword.overlaps[var, Nvar])] for Nvar in includedNVars]
        for variableword in orderedlist:
            removecount = 0
            for Nvar in checklist:
                words = Nvar[0]
                overlap = Nvar[1]
                for word in words:
                    if variableword[0][overlap[0]] != word[overlap[1]]:
                        removecount += 1
            variableword[1] = removecount
        orderedlist = sorted(orderedlist, key=lambda word: word[1])
        rlist = []
        for x in orderedlist:
            rlist.append(x[0])
        return rlist

    def select_unassigned_variable(self, assignment):
        # Return an unassigned variable not already part of `assignment`.
        # Choose the variable with the minimum number of remaining values
        # in its domain. If there is a tie, choose the variable with the highest
        # degree. If there is a tie, any of the tied variables are acceptable
        # return values.
        variables = []
        temp = []
        for x in self.crossword.variables:
            if x not in list(assignment.keys()):
                variables.append([x, len(self.domains[x]), len(self.crossword.neighbors(x))])
        variables = sorted(variables, key=lambda variable: variable[1])
        minDomains = variables[0][1]
        while len(variables) != 0:
            if variables[0][1] == minDomains:
                temp.append(variables[0])
            variables.pop(0)
        variables = temp.copy()
        if len(variables) == 1:
            return variables[0][0]
        variables = sorted(variables, key=lambda variable: variable[2], reverse=True)
        return variables[0][0]

    def backtrack(self, assignment):
        # Using Backtracking Search, take as input a partial assignment for the
        # crossword and return a complete assignment if possible to do so.

        # `assignment` is a mapping from variables (keys) to words (values).

        # If no assignment is possible, return None.
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignmentcopy = assignment.copy()
            assignmentcopy[var] = value
            if self.consistent(assignmentcopy):
                assignment[var] = value
                result = self.backtrack(assignment)
                if result != None:
                    return result
                assignment.pop(var)
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
