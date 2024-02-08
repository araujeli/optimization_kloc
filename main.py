# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pandas as pd
import math
import random
from random import randint

from src.data.data_treatment import DataTreatment
from src.metaheuristics.GRASP import Grasp
from src.core.initial_solution import InitialSolution
from src.heuristics.local_searches import LocalSearches
from src.heuristics.structures import Structures
from src.core.objective_function import ObjectiveFunction
from src.service.basic_functions import BasicFunctions
from maps.test import TestFolium
from google.cloud import storage
import gcsfs

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    treat = DataTreatment('input\\fornecedor_destino_sku_3.csv', 'input\\Local_municipios.xlsx', 'Cenarios\\Viana_Extrema_Itajai.xlsx', 'input\\skus_ativos.csv', 'input\\ICMSPadrao.xlsx')
    #treat.analyze_prod_lat_long()

    list_skus = treat.treat_current_scenario('input\\Lista_extrema.xlsx')
    list_service = treat.data_treat(list_skus)
    df_stored = treat.return_data_stored()

    print("Starting metaheuristic...")

    bf = BasicFunctions()
    obf = ObjectiveFunction()
    initial = InitialSolution(obf)
    ls = LocalSearches(bf, obf)
    ns = Structures(bf, obf)
    grasp = Grasp(ls, ns, initial)
    list_cities_final, list_solution_final, of_final = grasp.run(list_service, 3, 1)

    print(list_cities_final)
    print(of_final)

    df_result, cities_names = treat.return_df_lat_long_and_cities(df_stored, list_solution_final, list_cities_final)
    treat.create_maps(df_result, 'fornecedor', cities_names)
    treat.create_maps(df_result, 'entrega', cities_names)

    #print(list_skus)
    #print(df_result)

    df_result_1 = df_result.loc[df_result['VIANA'] == 1]
    df_result_3 = df_result_1['codigo_produto'].drop_duplicates()
    list_result_2 = df_result_3.values.tolist()

    df_pesados = pd.read_csv('input\\skus_ativos_leves_pesados_310823.csv', sep=',')
    df_pesados_1 = df_pesados.loc[df_pesados['pesado'] == 0]
    list_leves = df_pesados_1['codigo'].values.tolist()

    df_final_result = df_result.loc[df_result['codigo_produto'].isin(list_result_2)]
    df_final_result_1 = df_final_result.loc[df_result['codigo_produto'].isin(list_leves)]
    df_final_result_2 = df_final_result_1['codigo_produto'].drop_duplicates()
    list_result_final = df_final_result_2.values.tolist()
    treat.export_from_csv_to_excel(list_result_final, 'input\\fornecedor_destino_sku_3.csv')
    #treat.export_result_to_bucket()

    print(len(list_skus))
    #print(len(list_result_2))
    print(len(list_result_final))


    #treat.join_sum_demanda()



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
