import pandas as pd
import math
from maps.test import TestFolium
from google.cloud import storage
from google.cloud import bigquery
import gcsfs

class DataTreatment:
    def __init__(
        self,
            main_doc: str,
            cities_doc: str,
            capitais_doc: str,
            current_skus: str,
            incentivo_fiscal: str
    ):
        """
        This class generate a solution using a greedy heuristic.

        Args:
            main_doc: A string with the main document.
            cities_doc: A string with the lat/long cities document.
            capitais_doc: A string with the capitais document.
        """

        self._main_doc = main_doc
        self._cities_doc = cities_doc
        self._capitais_doc = capitais_doc
        self._current_skus = current_skus
        self._incentivo_fiscal = incentivo_fiscal

    def lat_long_reader(self, doc, name_1, name_2, name_3, name_4, sheet_name):
        df = pd.read_excel(doc, names=[name_1, name_2, name_3, name_4], header=0, sheet_name=sheet_name)
        #print(df.head(n=10))
        return df

    def lat_long_reader_2(self, doc, name_1, name_2, name_3, name_4, name_5, sheet_name):
        df = pd.read_excel(doc, names=[name_1, name_2, name_3, name_4, name_5], header=0, sheet_name=sheet_name)
        #print(df.head(n=10))
        return df

    def incentivo_reader(self):
        df = pd.read_excel(self._incentivo_fiscal)
        return df

    def build_list_service(self, df, capital_doc):
        df_lat_long_capitais = self.lat_long_reader(capital_doc, 'capital', 'estado_capital',
                                                     'Lat_capital', 'Long_capital', 'Capitais')
        list_capitais = df_lat_long_capitais['capital'].tolist()
        list_service = []
        for column_index in list_capitais:
            list_service.append(df['MULT_' + column_index.replace(" ", "")].tolist())
        return list_service

    def data_reader(self, doc):
        df = pd.read_csv(doc, sep=',')
        df['cidade_entrega'] = df['cidade_entrega'].str.upper()
        df['cidade_entrega'] = df['cidade_entrega'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
        df['cidade_fornecedor'] = df['cidade_fornecedor'].str.upper()
        df['cidade_fornecedor'] = df['cidade_fornecedor'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
        df_result_group = df.groupby(['codigo_fornecedor', 'cidade_fornecedor', 'estado_fornecedor',
                                      'cidade_entrega', 'estado_entrega', 'codigo_produto', 'ibge']).size().reset_index(name='count')
        df_result_sum = df.groupby(['codigo_fornecedor', 'cidade_fornecedor', 'estado_fornecedor',
                                      'cidade_entrega', 'estado_entrega', 'codigo_produto', 'ibge'])['qtd_itens'].sum()
        df_result_group_2 = df_result_group.drop(columns=['count'])
        df_result_group_2['qtd_itens'] = df_result_sum.values

        return df_result_group_2

    def merge(self, df_1, df_2, key_1, key_2):
        df = pd.merge(df_1, df_2, on=[key_1, key_2])
        #print(df.head(n=10))
        return df

    def merge_one_key(self, df_1, df_2, key_1):
        df = pd.merge(df_1, df_2, on=[key_1])
        #print(df.head(n=10))
        return df

    def calc_distance(self, lat_1, long_1, lat_2, long_2):
        if lat_1 == lat_2 and long_1 == long_2:
            return 0
        result = 6371 * math.acos(math.cos(math.pi * (90-lat_1)/180) * math.cos(math.pi * (90-lat_2)/180) +
                                  math.sin(((90-lat_1) * math.pi / 180)) * math.sin(((90-lat_2) * math.pi / 180)) *
                                  math.cos(((long_2 - long_1) * math.pi / 180)))
        return result

    def calc_distance_between_lists(self, list_1, list_2, list_3, list_4, tipo, df_icms):
        estado_1 = list_1[1]
        lat_1 = list_1[2]
        long_1 = list_1[3]

        list_of_distances = []

        for i in range(len(list_2)):
            estado_2 = list_4[i]
            chave_estado = ""
            if tipo == 'entrega':
                chave_estado = estado_1 + estado_2
            else:
                chave_estado = estado_2 + estado_1
            serie_icms = df_icms.loc[chave_estado]

            lat_2 = list_2[i]
            long_2 = list_3[i]
            list_of_distances.append(self.calc_distance(lat_1, long_1, lat_2, long_2)*serie_icms['ICMS'])

        return list_of_distances

    def make_list(self, data):
        list_test = []
        for elemento in data:
            list_test.append(elemento)
        return list_test

    def mult_columns(self, df, tipo_principal, tipo_1):
        return df.eval('MULT_'+tipo_principal.replace(" ", "")+' = '+tipo_1+' * '+"SUM"+'_'+tipo_principal)

    def mult_all_colums(self, df, columns_chosen):
        df_result = df
        for column_index in columns_chosen:
            df_result = self.mult_columns(df_result, column_index.replace(" ", ""), 'qtd_itens')
        return df_result

    def sum_columns(self, df, tipo_principal, tipo_1, tipo_2):
        return df.eval('SUM_'+tipo_principal.replace(" ", "")+' = '+tipo_principal+'_'+tipo_1+' + '+tipo_principal+'_'+tipo_2)

    def sum_all_colums(self, df, columns_chosen):
        df_result = df
        for column_index in columns_chosen:
            df_result = self.sum_columns(df_result, column_index.replace(" ", ""), 'entrega', 'fornecedor')
        return df_result

    def delete_columns(self, df, tipo_principal, tipo_1, tipo_2):
        df_result_1 = df.drop(columns=[tipo_principal+"_"+tipo_1])
        df_result_2 = df_result_1.drop(columns=[tipo_principal+"_"+tipo_2])
        return df_result_2

    def delete_all_colums_type(self, df, columns_chosen):
        df_result = df
        for column_index in columns_chosen:
            df_result = self.delete_columns(df_result, column_index.replace(" ", ""), 'entrega', 'fornecedor')
        return df_result

    def delete_all_colums_operation(self, df, operacao, columns_chosen):
        df_result = df
        for column_index in columns_chosen:
            df_result = df_result.drop(columns=[operacao+"_"+column_index.replace(" ", "")])
        return df_result

    def print_hi(self, name):
        # Use a breakpoint in the code line below to debug your script.
        print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

    def insert_list_of_distances_in_dataframe(self, tipo_de_agente_distancia, dframe_capital, dframe_current, df_icms):
        list_names_capitais = dframe_capital['capital'].values.tolist()
        size_of_list_names_capitais = len(list_names_capitais)

        dframe_current_2 = dframe_current[dframe_current['Lat_'+tipo_de_agente_distancia].notna()]
        dframe_current_3 = dframe_current_2[dframe_current_2['Long_' + tipo_de_agente_distancia].notna()]

        lat_fornecedores = dframe_current_3['Lat_'+tipo_de_agente_distancia].values.tolist()
        long_fornecedores = dframe_current_3['Long_'+tipo_de_agente_distancia].values.tolist()
        estado_fornecedores = dframe_current_3['estado_'+tipo_de_agente_distancia].values.tolist()

        for i in range(size_of_list_names_capitais):
            print(i)
            list_capital = self.make_list(dframe_capital.iloc[i, :])
            current_list = self.calc_distance_between_lists(list_capital, lat_fornecedores, long_fornecedores, estado_fornecedores, tipo_de_agente_distancia, df_icms)
            dframe_current_3[list_capital[0].replace(" ", "")+"_"+tipo_de_agente_distancia] = current_list


        return dframe_current_3


    def store_data(self, data):
        self._df_stored = data

    def return_data_stored(self):
        return self._df_stored

    # Press the green button in the gutter to run the script.
    def data_treat(self, list_skus):
        df_lat_long_1 = self.lat_long_reader_2(self._cities_doc, 'cidade_entrega', 'estado_entrega',
                                        'Lat_entrega', 'Long_entrega', 'ibge', 'V2')
        #df_incentivo_fiscal = self.incentivo_reader()
        df_reader = self.data_reader(self._main_doc)
        print(len(df_reader.index))
        df_skus = pd.read_csv(self._current_skus, sep=',')
        list_current_skus = df_skus['codigo'].values.tolist()
        df_reader = df_reader.loc[df_reader['codigo_produto'].isin(list_current_skus)]
        print(len(df_reader.index))
        df_test = df_reader['codigo_produto']
        df_test_2 = df_test.drop_duplicates()
        #print(len(df_test_2))
        #df_reader_2 = df_reader['codigo_produto'].drop_duplicates()
        #df_reader_3 = df_reader_2.values.tolist()
        #print(len(df_reader_3))

        df_merge_1 = self.merge_one_key(df_lat_long_1, df_reader, "ibge")
        df_lat_long_2 = self.lat_long_reader(self._cities_doc, 'cidade_fornecedor', 'estado_fornecedor',
                                        'Lat_fornecedor', 'Long_fornecedor', 'V1')
        df_merge_2 = self.merge(df_lat_long_2, df_merge_1, "cidade_fornecedor", "estado_fornecedor")
        df_lat_long_capitais = self.lat_long_reader(self._capitais_doc, 'capital', 'estado_capital',
                                                    'Lat_capital', 'Long_capital', 'Capitais')
        print(len(df_merge_2.index))

        #df_merge_3 = self.merge_incentivo(df_merge_2, df_incentivo_fiscal, "codigo_produto")
        #print(df_merge_3.columns)

        df_icms = pd.read_excel(self._incentivo_fiscal, index_col="Chave")
        df_merge_2 = df_merge_2.drop(columns=['cidade_entrega_y', 'estado_entrega_y'])
        df_merge_2.rename(
            columns={'cidade_entrega_x': 'cidade_entrega', 'estado_entrega_x': 'estado_entrega'},
            inplace=True)
        print(df_merge_2.columns)
        print("Iniciando calculos de lat/long")
        print("Calculo de entrega")
        df_result = self.insert_list_of_distances_in_dataframe("entrega", df_lat_long_capitais, df_merge_2, df_icms)
        print("Calculo de fornecedor")
        df_result2 = self.insert_list_of_distances_in_dataframe("fornecedor", df_lat_long_capitais, df_result, df_icms)

        print("Finalizando calculos de lat/long")

        list_capitais = df_lat_long_capitais['capital'].tolist()
        df_soma_2 = self.sum_all_colums(df_result2, list_capitais)
        df_delete = self.delete_all_colums_type(df_soma_2, list_capitais)
        df_mult = self.mult_all_colums(df_delete, list_capitais)
        #df_delete_qtd = df_mult.drop(columns=['qtd_itens'])
        df_final_result = self.delete_all_colums_operation(df_mult, "SUM", list_capitais)
        #df_final_result = self.delete_all_colums_operation(df_final_result, "Incentivo", list_capitais)
        df_final_result_2 = df_final_result
        if (len(list_skus) > 0):
            df_final_result_2 = df_final_result.loc[~df_final_result['codigo_produto'].isin(list_skus)]

        df_test_final = df_final_result_2['codigo_produto']
        df_test_final_2 = df_test_final.drop_duplicates()
        #print(len(df_test_final_2))

        self.store_data(df_final_result_2)

        list_final_service = self.build_list_service(df_final_result_2, self._capitais_doc)

        return list_final_service

    def return_df_lat_long_and_cities(self, current_df, list_solution, list_cities):
        df_capitais = pd.read_excel(self._capitais_doc, names=['City', "UF", 'Lat', "Long"], header=0)
        list_capitais_names = df_capitais['City'].values.tolist()

        list_capitais_chosen = []

        for i in range(len(list_cities)):
            if list_cities[i] == 1:
                current_df[list_capitais_names[i]] = list_solution[i]
                list_capitais_chosen.append(list_capitais_names[i])

        current_df_final = self.delete_all_colums_operation(current_df, "MULT", list_capitais_names)

        #print(current_df_final.columns)

        return current_df_final, list_capitais_chosen

    def return_list_lat_long(self, current_df, type_flow, city):
        df_result_1 = current_df.loc[current_df[city] == 1]
        df_select_type_flow = df_result_1[['Lat_'+type_flow, 'Long_'+type_flow, 'qtd_itens']]
        #df_select_type_flow_2 = df_select_type_flow.drop_duplicates()
        return df_select_type_flow.values.tolist()

    def create_maps(self, current_df, type_flow, cities):
        folium = TestFolium()
        for city in cities:
            list_result_lat_long = self.return_list_lat_long(current_df, type_flow, city)
            folium.create_map(list_result_lat_long, type_flow, city)
        return 0

    def treat_current_scenario(self, doc):
        df_extrema = pd.read_excel(doc)
        df_skus = df_extrema['Sku'].drop_duplicates()
        list_skus = df_skus.values.tolist()
        return list_skus

    def export_excel(self, list, file_1):
        df = pd.read_excel(file_1)
        df_final_result = df.loc[df['Sku'].isin(list)]
        file_name = 'output\\list_extrema.xlsx'
        df_final_result.to_excel(file_name)
        return 0

    def  export_from_csv_to_excel(self, list, file_1):
        df = pd.read_csv(file_1)
        df_2 = df['codigo_produto']
        #print(df_2)
        df_3 = df_2.drop_duplicates()
        df_final_result = df_3.loc[df_3.isin(list)]
        file_name = 'output\\TesteSudeste Produtos para Extrema e devem ir a Viana.csv'
        df_final_result.to_csv(file_name)
        return 0

    def join_sum_demanda(self):
        df = pd.read_csv('input\\fornecedor_destino_sku_2.csv', sep=',')
        df_result_sum = df.groupby('codigo_produto')['qtd_itens'].sum().rename_axis('Sku')
        df_result_sum_2 = df_result_sum.reset_index()
        df_result_sum_3 = pd.DataFrame(df_result_sum_2)

        df_n_extrema = pd.read_excel('output\\Lista potenciais SKUs para enviar a Extrema(1).xlsx')
        df_merge = df_result_sum_3.merge(df_n_extrema,on=['Sku'],how="right")
        df_merge.to_excel('output\\Lista potenciais SKUs para enviar a Extrema(1) com quantidades.xlsx')
        return 0

    def analyze_prod_lat_long(self):
        df_lat_long_1 = self.lat_long_reader(self._cities_doc, 'cidade_entrega', 'estado_entrega',
                                             'Lat_entrega', 'Long_entrega')
        df_lat_long_1 = df_lat_long_1[['cidade_entrega', 'estado_entrega', 'Lat_entrega']]
        df_lat_long_2 = self.lat_long_reader(self._cities_doc, 'cidade_fornecedor', 'estado_fornecedor',
                                             'Lat_fornecedor', 'Long_fornecedor')
        df_lat_long_2 = df_lat_long_2[['cidade_fornecedor', 'estado_fornecedor', 'Lat_fornecedor']]

        df = self.data_reader(self._main_doc)
        df_fornecedores = df[['cidade_fornecedor', 'estado_fornecedor']]
        df_entrega = df[['cidade_entrega', 'estado_entrega']]
        df_fornecedores = df_fornecedores.drop_duplicates()
        df_entrega = df_entrega.drop_duplicates()

        df_fornecedores.to_excel('output\\fornecedor.xlsx')
        df_entrega.to_excel('output\\entrega.xlsx')

        df_lat_long_1.to_excel('output\\cities_entrega.xlsx')
        df_lat_long_2.to_excel('output\\cities_fornecedor.xlsx')
        return 0

    def export_result_to_bucket(self):
        storage_client = storage.Client()
        bucket_name = 'clock-upload'
        bucket = storage_client.bucket(bucket_name)
        fs = gcsfs.GCSFileSystem(project=storage_client.project)
        local_file_path = 'output\\TesteSudeste Produtos para Extrema e devem ir a Viana.csv'
        cloud_file_path = f'{bucket_name}/TesteSudeste Produtos para Extrema e devem ir a Viana.csv'

        with fs.open(cloud_file_path, 'wb') as cloud_file:
            with open(local_file_path, 'rb') as local_file:
                cloud_file.write(local_file.read())


    # See PyCharm help at https://www.jetbrains.com/help/pycharm/