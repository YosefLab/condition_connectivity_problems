import itertools, file_reader, time, copy, collections
import gurobipy

TIME_LIMIT = 20 * 60

class Instance:
    def __init__(self, file_name):
        self.file_name = file_name
        a, _, _ = file_reader.read_test_case(file_name)
        self.num_cities = a
        self.x_vars = [[0] * (a + 1) for i in range(a + 1)]
        self.model = gurobipy.Model()

    def __call__(self, *args, **kwargs):
        return self.begin_solve()

    def begin_solve(self):
        start = time.time()
        a, b, c = file_reader.read_test_case(self.file_name)
        result = self.solve(a, b, c)
        print 'Took', time.time() - start, 'seconds'
        return result

    def solve(self, num_cities, cost_matrix, color_array):
        """
        Solves the NPTSP problem using an ILP solver.

        :param num_cities: Number of cities
        :param cost_matrix: Cost matrix
        :param color_array: Color array
        :return: Array of city indices, one-indexed
        """
        print 'Number of cities:', num_cities

        """
        Augment the cost matrix. Since we want to find the best path, let's add a dummy city
        and connect it to all other cities with edge cost zero.
        """
        aug_cost_matrix = copy.deepcopy(cost_matrix)
        for i in range(len(aug_cost_matrix)):
            aug_cost_matrix[i].append(0)
        aug_cost_matrix.append([0] * (num_cities + 1))

        # Flatten the augmented cost matrix
        flat_aug_cost_matrix = list(itertools.chain(*aug_cost_matrix))

        print 'Creating constraints...'

        # Variable matrix

        for i in range(num_cities + 1):
            for j in range(num_cities + 1):
                self.x_vars[i][j] = self.model.addVar(vtype=gurobipy.GRB.BINARY)

        self.model.update()

        # Objective function
        obj_expr = 0
        flat_x_vars = list(itertools.chain(*self.x_vars))
        for i in range(len(flat_x_vars)):
            obj_expr += flat_x_vars[i] * flat_aug_cost_matrix[i]
        self.model.setObjective(obj_expr, gurobipy.GRB.MINIMIZE)

        # Flow constraints
        for i in range(num_cities + 1):
            expr_row_major = 0
            expr_col_major = 0
            for j in range(num_cities + 1):
                if i == j:
                    continue
                expr_row_major += self.x_vars[i][j]
                expr_col_major += self.x_vars[j][i]
            self.model.addConstr(expr_row_major == 1)
            self.model.addConstr(expr_col_major == 1)

        # Sub-tour elimination, from Wikipedia
        u_vars = []
        for i in range(num_cities + 1):
            u_vars.append(self.model.addVar(lb=0, ub=num_cities + 1, vtype=gurobipy.GRB.INTEGER))
        self.model.update()
        for i in range(1, num_cities + 1):
            for j in range(1, num_cities + 1):
                if i == j:
                    continue
                self.model.addConstr(u_vars[i] - u_vars[j] + (num_cities + 1) * self.x_vars[i][j] <= num_cities)


        # Non-partisan
        red_indices = find_all_indices(color_array, "R")
        blue_indices = find_all_indices(color_array, "B")


        for i in red_indices:
            for j in red_indices:
                for k in red_indices:
                    for l in red_indices:
                        self.model.addConstr(self.x_vars[i][j] + self.x_vars[j][k] + self.x_vars[k][l] <= 2)

        print 'Enforced red constraints'

        for i in blue_indices:
            for j in blue_indices:
                for k in blue_indices:
                    for l in blue_indices:
                        self.model.addConstr(self.x_vars[i][j] + self.x_vars[j][k] + self.x_vars[k][l] <= 2)


        print 'Enforced blue constraints'

        self.model.update()

        print 'Finished generating constraints. Solving...'

        try:
            self.model.setParam('TimeLimit', TIME_LIMIT)
            self.model.optimize()
        except gurobipy.GurobiError, err:
            print err

    def did_time_out(self):
        return self.model.getAttr('Status') == gurobipy.GRB.TIME_LIMIT

    def get_gap(self):
        return self.model.getAttr('MIPGap')

    def get_current_solution(self):
        # Extract city ordering

        city_ordering = [0]
        curr_city = 0
        for _ in range(self.num_cities):
            curr_city = map(lambda var: var.x, self.x_vars[curr_city]).index(1)
            city_ordering.append(curr_city)

        # Rotate
        rotate_amount = -city_ordering.index(self.num_cities)
        d = collections.deque(city_ordering)
        d.rotate(rotate_amount)
        city_ordering = list(d)
        city_ordering.pop(0)

        # One-indexing
        city_ordering = map(lambda x: x + 1, city_ordering)

        return city_ordering

def all_ones_except_this_index(idx, len):
    lst = [1] * len
    lst[idx] = 0
    return lst

def find_all_indices(lst, elem):
    """
    Finds elements that match elem in the lst and returns their indices.
    :param lst:
    :param elem:
    :return:
    """
    indices = []
    for i in range(len(lst)):
        if lst[i] == elem:
            indices.append(i)
    return indices