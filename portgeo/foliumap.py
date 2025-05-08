"""
This module provides a custom Map class that extends folium.Map
"""

import folium
import folium.plugins


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

    def add_split_map(self, left="openstreetmap", right="cartodbpositron", **kwargs):
        """Add a split map to the map.
        Args:
            left (str): Name of the left layer. Default is "openstreetmap".
            right (str): Name of the right layer. Default is "cartodbpositron".
            **kwargs: Additional arguments for folium.TileLayer.
        """
        from localtileserver import get_folium_tile_layer
        import os

        if left.startswith("http") or os.path.exists(left):
            layer_left = get_folium_tile_layer(left, overlay=True, **kwargs)
        else:
            layer_left = folium.TileLayer(left, overlay=True, **kwargs)

        if right.startswith("http") or os.path.exists(right):
            layer_right = get_folium_tile_layer(right, overlay=True, **kwargs)
        else:
            layer_right = folium.TileLayer(right, overlay=True, **kwargs)

        sbs = folium.plugins.SideBySideLayers(
            layer_left=layer_left, layer_right=layer_right
        )

        layer_left.add_to(self)
        layer_right.add_to(self)
        sbs.add_to(self)
