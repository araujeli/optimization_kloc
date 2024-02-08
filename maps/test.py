import folium
from folium.plugins import HeatMap
import pandas as pd

class TestFolium:
    def __init__(
            self
    ):
        """
        """
    def printFolium(self):
        print(folium.__version__)
        m = folium.Map(location=[40, -95],zoom_start=4)

        url = (
            "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data"
        )
        state_geo = f"{url}/us-states.json"
        state_unemployment = f"{url}/US_Unemployment_Oct2012.csv"
        state_data = pd.read_csv(state_unemployment)

        folium.Choropleth(

            # geographical locations
            geo_data=state_geo,
            name="choropleth",

            # the data set we are using
            data=state_data,
            columns=["State", "Unemployment"],

            # YlGn refers to yellow and green
            fill_color="YlGn",
            fill_opacity=0.7,
            line_opacity=.1,
            key_on="feature.id",
            legend_name="Unemployment Rate (%)",
        ).add_to(m)

        m.save('maps\\results\\final_map.html')

        mapa = folium.Map(location=[-13.4008012, -46.4565518], zoom_start=5)
        df = pd.read_excel('input\\Local_municipios.xlsx', names=['city', 'uf', 'lat', 'long'], header=0)
        locais = df[['lat', 'long']].values.tolist()
        HeatMap(locais, radius=15).add_to(mapa)
        mapa.save('maps\\results\\mapa_test.html')
        return 0

    def create_map(self, locais, type_flow, city):
        mapa = folium.Map(location=[-13.4008012, -46.4565518], zoom_start=5)

        df = pd.read_excel('input\\Local_municipios.xlsx', names=['cities', 'uf', 'lat', 'long'], header=0)
        df_2 = df.loc[df['cities'] == city]
        current_city = df_2[['lat', 'long']].values.tolist()
        current_city_2 = current_city[0]
        folium.Marker(location=current_city_2,
                      popup=city,
                      tooltip=city,
                      icon=folium.Icon(color="green")
                      ).add_to(mapa)

        HeatMap(locais, radius=15).add_to(mapa)
        mapa.save('maps\\results\\result_'+type_flow+'_'+city+'.html')
        return 0
