
from src.core.objective_function import ObjectiveFunction
class InitialSolution:
    def __init__(
        self,
        objective_function: ObjectiveFunction,
    ):
        """
        This class generate a solution using a greedy heuristic.

        Args:
            basic_function: A string with the main document.
        """

        self._objective_function = objective_function

    def build_initial_solution(self, list_service, number_cities_chosen):
        number_potential_cities = len(list_service)
        number_fornecedor_entrega = len(list_service[0])

        list_sum_distance_by_city = []
        for index in range(number_potential_cities):
            list_sum_distance_by_city.append(sum(list_service[index]))

        list_of_min_index = []
        for index in range(number_cities_chosen):
            tmp = min(list_sum_distance_by_city)
            new_index = list_sum_distance_by_city.index(tmp)
            list_of_min_index.append(new_index)
            list_sum_distance_by_city[new_index] = float("inf")

        list_cities = []
        for index in range(number_potential_cities):
            if index in list_of_min_index:
                list_cities.append(1)
            else:
                list_cities.append(0)

        list_solution = []
        for index in range(number_potential_cities):
            list_solution_2 = []
            for index_2 in range(number_fornecedor_entrega):
                list_solution_2.append(0)
            list_solution.append(list_solution_2)

        for index in range(number_fornecedor_entrega):
            list_distance_to_cities = []
            for index_2 in range(number_potential_cities):
                if index_2 in list_of_min_index:
                    list_distance_to_cities.append(list_service[index_2][index])
                else:
                    list_distance_to_cities.append(float("inf"))
            tmp = min(list_distance_to_cities)
            new_index = list_distance_to_cities.index(tmp)
            list_solution[new_index][index] = 1

        of = self._objective_function.calc_objective_function(list_service, list_cities, list_solution)

        return list_cities, list_solution, of