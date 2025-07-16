import geopandas as gpd
import pandas as pd
import folium
from shapely.geometry import Polygon
from folium.plugins import MarkerCluster


if __name__ == "__main__":

    df = pd.read_csv('./data/amostra_processed.csv', encoding='latin1')
    df_1 = pd.read_csv('./data/reserva_processed.csv', encoding='latin1')

    df['reserva'] = 0
    df_1['reserva'] = 1
    df = pd.concat([df, df_1], ignore_index=True)
    gdf= gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df['lon'], df['lat']),
        crs="EPSG:4326"  # WGS84 (latitude/longitude)
    )
    gdf = gdf.to_crs(epsg=4326)
    color_map = {
        "numero": 'número encontrado',
        "numero_aproximado": 'número encontrado',
        'logradouro': 'rua encontrada',
        'localidade': 'bairro',
        'municipio': 'localização precisa não encontrada'
    }

    m = folium.Map(location=[gdf.geometry.y.mean(), gdf.geometry.x.mean()], zoom_start=6)

    marker_cluster = MarkerCluster().add_to(m)

    def get_color(reserva):
        return 'blue' if reserva == 1 else 'green'

    def get_status(reserva):
        return 'LISTA RESERVA'  if reserva == 1 else 'LISTA PRIORIDADE'

    color_map = {
        "numero": 'Número',
        "numero_aproximado": 'Número',
        'logradouro': 'Rua',
        'localidade': 'Bairro',
        'municipio': 'Localização precisa não encontrada'
    }

    for idx, row in gdf.iterrows():
        lat, lon = row.geometry.y, row.geometry.x
        
        # Get color for the current precisao value, default to gray if missing
        pin_color = color_map.get(row['precisao'], 'gray')
        
        popup_html = f"""
        <ul>
            <strong>{get_status(row['reserva'])}</strong>
            <li><strong>Razão:</strong> {row['nome_razao']}</li>
            <li><strong>Setor:</strong> {row['setor']}</li>
            <li><strong>Endereço:</strong> {row['raw_endereco']}</li>
            <li><strong>Telefone:</strong> {row['telefone']}</li>
            <li><strong>Municipio:</strong> {row['nome_municipio']}</li>
            <li><strong>Geocode precisão:</strong> {color_map[row['precisao']]}</li>
            <li><strong>Latitude:</strong> {row['lat']}</li>
            <li><strong>Longitude:</strong> {row['lon']}</li>
        </ul>
        """
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=get_color(row['reserva'])),
        ).add_to(marker_cluster)

    m.save("./map.html")