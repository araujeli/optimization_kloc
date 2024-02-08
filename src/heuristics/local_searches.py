import pandas as pd
import math
import random
from random import randint

from src.service.basic_functions import BasicFunctions
from src.core.objective_function import ObjectiveFunction

class LocalSearches:
    def __init__(
        self,
        basic_function: BasicFunctions,
        objective_function: ObjectiveFunction
    ):
        """
        This class storage the local searches.

        Args:
            basic_function: .
        """

        self._basic_function = basic_function
        self._objective_function = objective_function

    def LS_swap_cities(self, list_service, list_cities, list_solution, of):
        # list_service: lista com as distâncias e seus pesos entre fornecedores e cidades
        # list_cities: lista de cidades com CD
        # list_solution: quais fornecedores e demandas são atendidas pelas cidades com CD

        for list_position_to_choose_one_validated_city in range(len(list_cities)):
            if list_cities[list_position_to_choose_one_validated_city] == 1:
                for list_position_to_choose_one_invalidated_city in range(len(list_cities)):
                    if list_cities[list_position_to_choose_one_invalidated_city] == 0:
                        list_cities = self._basic_function.swap(list_cities, list_position_to_choose_one_validated_city,
                                           list_position_to_choose_one_invalidated_city)
                        list_solution = self._basic_function.swap(list_solution,
                                             list_position_to_choose_one_validated_city,
                                             list_position_to_choose_one_invalidated_city)
                        new_of = self._objective_function.recalc_objective_function_swap_cities(list_service, list_solution,
                                                                       list_position_to_choose_one_validated_city,
                                                                       list_position_to_choose_one_invalidated_city)
                        if new_of > 0:
                            list_cities = self._basic_function.swap(list_cities,
                                                                    list_position_to_choose_one_invalidated_city,
                                                                    list_position_to_choose_one_validated_city)
                            list_solution = self._basic_function.swap(list_solution,
                                                                      list_position_to_choose_one_invalidated_city,
                                                                      list_position_to_choose_one_validated_city)
                        else:
                            of += new_of

        return list_cities, list_solution, of

    def LS_swap_cities_fornecedor(self, list_service, list_solution, list_cities, of):
        list_position_fornecedor_entrega = randint(
            0, len(list_service[0]) - 1
        )

        for index in range(len(list_cities)):
            if list_solution[index][list_position_fornecedor_entrega] == 1:
                position_fornecedor_addressed = index
                for new_position_fornecedor_addressed in range(len(list_cities)):
                    if list_solution[new_position_fornecedor_addressed][list_position_fornecedor_entrega] == 0 \
                            and list_cities[new_position_fornecedor_addressed] == 1:
                        new_of = - list_service[position_fornecedor_addressed][list_position_fornecedor_entrega] + \
                                 list_service[new_position_fornecedor_addressed][list_position_fornecedor_entrega]
                        if new_of <= 0:
                            list_solution[position_fornecedor_addressed][list_position_fornecedor_entrega] = 0
                            list_solution[new_position_fornecedor_addressed][list_position_fornecedor_entrega] = 1
                            of += new_of

        return list_solution, of