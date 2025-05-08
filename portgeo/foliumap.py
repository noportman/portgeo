"""
This module provides a custom Map class that extends folium.Map
"""

import folium


class Map(folium.Map):
    """Custom Map class to handle portgeos."""

    def __init__(self, center=[0, 0], zoom=2, **kwargs):
        super().__init__(location=center, zoom_start=zoom, **kwargs)

    def add_geojson(self, data, **kwargs):
        """Add a GeoJSON layer to the map.

        Args:
            data (str or dict): Path to the GeoJSON file or GeoJSON data.
            **kwargs: Additional arguments for folium.GeoJson.
        """

        import geopandas as gpd

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            geojson = gdf.__geo_interface__

        elif isinstance(data, dict):
            geojson = data

        folium.GeoJson(data=geojson, **kwargs).add_to(self)

    def add_shp(self, data, **kwargs):
        """Add a shapefile layer to the map.

        Args:
            data (str): Path to the shapefile.
            **kwargs: Additional arguments for folium.GeoJson.
        """

        import geopandas as gpd

        gdf = gpd.read_file(data)
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_gdf(self, gdf, **kwargs):
        """Add a GeoDataFrame layer to the map.

        Args:
            gdf (GeoDataFrame): GeoDataFrame to add.
            **kwargs: Additional arguments for folium.GeoJson.
        """

        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_vector(self, data, **kwargs):
        """Add a vector layer to the map.

        Args:
            data (str or GeoDataFrame or dict): Path to the vector file,
                GeoDataFrame, or GeoJSON data.
            **kwargs: Additional arguments for folium.GeoJson.
        """
        import folium

        import geopandas as gpd

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            self.add_gdf(gdf, **kwargs)
        elif isinstance(data, gpd.GeoDataFrame):
            self.add_gdf(data, **kwargs)
        elif isinstance(data, dict):
            self.add_geojson(data, **kwargs)
        else:
            raise ValueError(
                "Unsupported data type. Please provide a GeoDataFrame, GeoJSON, or file path."
            )

    def add_layer_control(self):
        """Add a layer control to the map.

        Args:
            **kwargs: Additional arguments for folium.LayerControl.
        """
        folium.LayerControl().add_to(self)
