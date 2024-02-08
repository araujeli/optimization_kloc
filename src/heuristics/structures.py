import pandas as pd
import math
import random
from random import randint

from src.service.basic_functions import BasicFunctions
from src.core.objective_function import ObjectiveFunction
class Structures:
    def __init__(
        self,
        basic_function: BasicFunctions,
        objective_function: ObjectiveFunction
    ):
        """
        This class.

        Args:
            basic_function: .
            objective_function: .
        """

        self._basic_function = basic_function
        self._objective_function = objective_function

    def structure_swap_cities_fornecedor(self, list_service, list_solution, list_cities, of):
        list_position_fornecedor_entrega = randint(
            0, len(list_service[0]) - 1
        )

        position_fornecedor_addressed = 0
        for index in range(len(list_cities)):
            if list_solution[index][list_position_fornecedor_entrega] == 1:
                position_fornecedor_addressed = index

        new_position_fornecedor_addressed = randint(
            0, len(list_cities) - 1
        )
        while list_solution[new_position_fornecedor_addressed][list_position_fornecedor_entrega] == 1 \
                or list_cities[new_position_fornecedor_addressed] == 0:
            new_position_fornecedor_addressed = randint(
                0, len(list_cities) - 1
            )

        list_solution[position_fornecedor_addressed][list_position_fornecedor_entrega] = 0
        list_solution[new_position_fornecedor_addressed][list_position_fornecedor_entrega] = 1
        new_of = - list_service[position_fornecedor_addressed][list_position_fornecedor_entrega] + \
                 list_service[new_position_fornecedor_addressed][list_position_fornecedor_entrega]
        if new_of > 0:
            list_solution[position_fornecedor_addressed][list_position_fornecedor_entrega] = 1
            list_solution[new_position_fornecedor_addressed][list_position_fornecedor_entrega] = 0
        else:
            of += new_of

        return list_solution, of

    def structure_swap_cities(self, list_service, list_cities, list_solution, of):
        # list_service: lista com as distâncias e seus pesos entre fornecedores e cidades
        # list_cities: lista de cidades com CD
        # list_solution: quais fornecedores e demandas são atendidas pelas cidades com CD

        list_position_to_choose_one_validated_city = randint(
            0, len(list_cities) - 1
        )
        while list_cities[list_position_to_choose_one_validated_city] == 0:
            list_position_to_choose_one_validated_city = randint(
                0, len(list_cities) - 1
            )

        list_position_to_choose_one_invalidated_city = randint(
            0, len(list_cities) - 1
        )
        if len(list_service) != len(list_cities):
            while list_cities[list_position_to_choose_one_invalidated_city] == 1:
                list_position_to_choose_one_invalidated_city = randint(
                    0, len(list_cities) - 1
                )

        list_cities = self._basic_function.swap(list_cities, list_position_to_choose_one_validated_city,
                           list_position_to_choose_one_invalidated_city)
        list_solution = self._basic_function.swap(list_solution, list_position_to_choose_one_validated_city,
                             list_position_to_choose_one_invalidated_city)
        new_of = self._objective_function.recalc_objective_function_swap_cities(list_service, list_solution,
                                                       list_position_to_choose_one_validated_city,
                                                       list_position_to_choose_one_invalidated_city)
        if new_of > 0:
            list_cities = self._basic_function.swap(list_cities, list_position_to_choose_one_invalidated_city,
                               list_position_to_choose_one_validated_city)
            list_solution = self._basic_function.swap(list_solution, list_position_to_choose_one_invalidated_city,
                                 list_position_to_choose_one_validated_city)
        else:
            of += new_of

        return list_cities, list_solution, of

    def structure_smallest_cities_for_fornecedor(self, number_cities, list_service, list_cities, list_solution):
        for index in range(len(list_solution[0])):
            list_distance_to_cities = []
            for index_2 in range(number_cities):
                if list_cities[index_2] == 1:
                    list_distance_to_cities.append(list_service[index_2][index])
                    list_solution[index_2][index] = 0
                else:
                    list_distance_to_cities.append(float("inf"))
                    list_solution[index_2][index] = 0
            tmp = min(list_distance_to_cities)
            new_index = list_distance_to_cities.index(tmp)
            list_solution[new_index][index] = 1
        of = self._objective_function.calc_objective_function(list_service, list_cities, list_solution)
        return list_solution, of