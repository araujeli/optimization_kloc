import random
from random import randint

from src.heuristics.local_searches import LocalSearches
from src.heuristics.structures import Structures
from src.core.initial_solution import InitialSolution
from src.service.basic_functions import BasicFunctions


class Grasp:
    def __init__(
            self,
            local_searches: LocalSearches,
            structures: Structures,
            initial_solution: InitialSolution,
    ):
        """
        This class generate a solution using a GRASP metaheuristic.

        Args:
            local_searches:.
            structures:.
            initial_solution:.
        """

        self._local_searches = local_searches
        self._structures = structures
        self._initial_solution = initial_solution

    def local_search(self, list_service, list_cities_1, list_solution_1, of):
        list_cities_2, list_solution_2, of_2 = self._local_searches.LS_swap_cities(list_service, list_cities_1,
                                                                                   list_solution_1, of)
        list_solution_3, of_3 = self._local_searches.LS_swap_cities_fornecedor(list_service, list_solution_2,
                                                                               list_cities_1, of_2)
        return list_cities_1, list_solution_3, of_3

    def structure(self, list_service, list_cities, list_solution, of):
        list_cities_2, list_solution_2, of_2 = self._structures.structure_swap_cities(list_service, list_cities,
                                                                                      list_solution, of)
        list_solution_3, of_3 = self._structures.structure_swap_cities_fornecedor(list_service, list_solution_2,
                                                                                  list_cities, of_2)
        return list_cities, list_solution_3, of_3

    def run(self, list_service, number_cities, number_iterations):
        list_cities_current, list_solution_current, of_current = self._initial_solution.build_initial_solution(
            list_service,
            number_cities)

        print(of_current)

        for i in range(number_iterations):
            list_cities_current_2, list_solution_current_2, of_2 = self.structure(list_service, list_cities_current,
                                                                                  list_solution_current, of_current)
            list_cities_current_3, list_solution_3, of_3 = self.local_search(list_service, list_cities_current_2,
                                                                             list_solution_current_2, of_2)

            list_cities_current = list_cities_current_3
            list_solution_current = list_solution_3
            of_current = of_3

        list_solution_current, of_current_2 = self._structures.structure_smallest_cities_for_fornecedor(number_cities,
                                                                                                        list_service,
                                                                                                        list_cities_current,
                                                                                                        list_solution_current)

        return list_cities_current, list_solution_current, of_current_2
