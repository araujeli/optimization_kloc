class ObjectiveFunction:
    def __init__(
        self,
    ):
        """
        This class .

        Args:
            basic_function: .
        """

    def calc_objective_function(self, list_service, list_cities, list_solution):
        of = 0
        for index in range(len(list_service)):
            if list_cities[index] == 1:
                for index_2 in range(len(list_service[index])):
                    of += list_solution[index][index_2] * list_service[index][index_2]
        return of

    def recalc_objective_function_swap_cities(self, list_service, list_solution, position_old, position_new):
        # list_service: lista com as distâncias e seus pesos entre fornecedores e cidades
        # list_solution: quais fornecedores e demandas são atendidas pelas cidades com CD
        # position_old: posição antiga válida
        # position_new: posição nova válida

        list_service_position_old = list_service[position_old]
        list_service_position_new = list_service[position_new]
        list_validate = list_solution[position_new]
        count_distances_old = 0
        count_distances_new = 0
        for index in range(len(list_validate)):
            count_distances_old += list_validate[index] * list_service_position_old[index]
            count_distances_new += list_validate[index] * list_service_position_new[index]
        return - count_distances_old + count_distances_new