import math
import copy
import random
import numpy as np


class nQueens:

    def __init__(self, n, method_type):
        self.n = n
        self.assignment = [-1] * n  # each element is the row index for corresponding column, -1 means no assignment yet
        self.domain = [list(range(n)) for i in range(n)]  # available values (rows) for each column (variable)
        self.updated_domains = dict(zip(range(n), self.domain))
        self.unassigned_columns = [i for i in range(n)]  # none of the columns are assigned yet
        self.backtrack_counter = 0
        self.curr_domains = None
        self.method_type = method_type
        self.solve_and_print()

    def prune(self, var, value, removals):
        """Rule out var=value."""

        self.curr_domains[var].remove(value)
        if removals is not None:
            removals.append((var, value))

    def select_next_variable(self):
        """
        :return: Next unassigned variable (column) in line
        """

        return self.unassigned_columns[0]

    def is_consistent(self, col, val):
        """
        Check if assigning val to col will be consistent with the rest of the assigments
        :return: true of consistent, false otherwise
        """
        assigned_columns = [i for i in range(self.n) if i != col and i not in self.unassigned_columns]
        for i in assigned_columns:
            col_distance = abs(i - col)
            row_distance = abs(self.assignment[i] - val)
            if row_distance == 0 or row_distance == col_distance:
                return False
        return True

    def select_next_variable_improved(self):
        """
        Finds and returns the variable with the fewest legal values
        :return: Variable with the least amount of legal values
        """
        updated_domains_len = {key: len(value) for key, value in self.updated_domains.items()}
        return min(updated_domains_len, key=updated_domains_len.get)

    def forward_checking(self, var):
        """
        Updates the domain of values and returns it
        :param var: Current column to check
        :return: Updated domain
        """
        assert self.assignment[var] == -1
        current_domain = self.domain[var]
        updated_domain = []
        for potential_assignment in current_domain:
            if self.is_consistent(var, potential_assignment):
                updated_domain.append(potential_assignment)
        return updated_domain

    def ac3(self):
        """
        Updates the domain of values and returns it
        :param var: Current column to check
        :return: Updated domain
        """
        Domain_x = self.unassigned_columns
        Domain_y = self.domain
        work_queue = set([(var, val) for var in Domain_x for val in Domain_y[var]])
        removals = []
        while work_queue:
            (var, val) = work_queue.pop()
            revised, rem = self.revise(Domain_x, Domain_y)
            if rem:
                removals.extend(rem)
            if revised:
                if Domain_x == []:
                    return [], removals
                else:
                    pass
        return dict(zip(Domain_x, [Domain_y[x] for x in Domain_x])), removals

    def revise(self, Domain_x: list, Domain_y: list):
        """Return true if we remove a value"""
        revised = False
        removals = []
        for var in Domain_x:
            temp_check = False
            for val in Domain_y[var]:
                if self.is_consistent(var, val):
                    temp_check = True
                    break
            if not temp_check:
                # Nothing consistent was found
                removals.append(var)
                Domain_x.remove(var)
                revised = True
        return revised, removals

    def backtrack(self):
        """
        Recursive backtracking function
        :return:a solution (final problem state) if there is one, otherwise it returns [].
        """
        self.backtrack_counter += 1

        if len(self.unassigned_columns) == 0:
            return self.assignment

        # Select the next unassigned column
        var = self.select_next_variable()
        # Iterate through values for var
        for val in self.domain[var]:
            if self.is_consistent(var, val):
                self.assignment[var] = val
                self.unassigned_columns.remove(var)
                result = self.backtrack()
                if result:
                    return result
                self.assignment[var] = -1
                self.unassigned_columns.append(var)  # reassign var to the unassigned columns
        return []

    def backtrack_improved(self, inference, First=True):
        """
        Recursive backtracking function
        :param inference: an inference method such as forward chaining or ac3
        :return:a solution (final problem state) if there is one, otherwise it returns [].
        """
        self.backtrack_counter += 1

        if len(self.unassigned_columns) == 0:
            return self.assignment
        if First:
            for var in self.unassigned_columns:
                self.updated_domains[var] = inference(var)
        var = self.select_next_variable_improved()
        for val in self.updated_domains[var]:
            self.assignment[var] = val
            self.unassigned_columns.remove(var)
            if var in self.updated_domains:
                del self.updated_domains[var]
            # selecting minimum remaining values
            for col in self.unassigned_columns:
                self.updated_domains[col] = inference(col)
            result = self.backtrack_improved(inference, False)
            if result:
                return result
            self.assignment[var] = -1
            self.unassigned_columns.append(var)
        return []

    def backtrack_improved_ac3(self, constraint, First=True):
        """
        Recursive backtracking function
        :param inference: an inference method such as forward chaining or ac3
        :return:a solution (final problem state) if there is one, otherwise it returns [].
        """
        self.backtrack_counter += 1

        if len(self.unassigned_columns) == 0:
            return self.assignment
        if First:
            self.updated_domains, _ = constraint()
        if not self.updated_domains:
            # self.assignment[var] = -1
            # self.unassigned_columns.append(var)
            return []
        var = self.select_next_variable_improved()
        for val in self.updated_domains[var]:
            if self.is_consistent(var, val):
                self.assignment[var] = val
                self.unassigned_columns.remove(var)
                # selecting minimum remaining values
                self.updated_domains, removals = constraint()
                if removals:
                    for removal in removals:
                        if removal not in self.unassigned_columns:
                            self.unassigned_columns.append(removal)
                result = self.backtrack_improved_ac3(constraint, False)
                if result:
                    return result
                self.assignment[var] = -1
                self.unassigned_columns.append(var)
        return []

    def solve_and_print(self):
        if self.method_type == 'domino':
            print("domino called")
            solution = self.backtrack()
        elif self.method_type == 'forward':
            print("Forward checking called")
            solution = self.backtrack_improved(self.forward_checking)
        elif self.method_type == 'ac3':
            print("ac3 called")
            solution = self.backtrack_improved_ac3(self.ac3)
        if solution.count(-1) == len(solution):
            print('Sorry, there is no solution to the %d-queens problem.' % (self.n))
        else:
            print('Solution: ' + str(solution))
            for x in range(0, self.n):
                for y in range(0, self.n):
                    if solution[x] == y:
                        print('Q', end=' ')
                    else:
                        print('-', end=' ')
                print('')

        print("Backtracking is called %d times" % self.backtrack_counter)


n = 50
# nq = nQueens(n, 'domino')
nq = nQueens(n, 'forward')
# nq = nQueens(n, 'ac3')
