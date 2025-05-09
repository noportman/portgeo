"""
This module provides a custom Map class that extends folium.Map
"""

import folium
import folium.plugins


class Map(folium.Map):
    """Custom Map class to handle portgeos."""

    def __init__(self, center=[0, 0], zoom=2, **kwargs):
        super().__init__(location=center, zoom_start=zoom, **kwargs)

    def add_geojson(
        self,
        data,
        tooltip_fields=None,
        tooltip_aliases=None,
        highlight=True,
        style_function=None,
        **kwargs,
    ):
        """Add a GeoJSON layer to the map with optional tooltip and highlight on hover.

        Args:
            data (str or dict): Path to the GeoJSON file or GeoJSON data.
            tooltip_fields (list): Fields to include in the tooltip.
            tooltip_aliases (list): Optional aliases for tooltip fields.
            highlight (bool): Whether to highlight geometry on hover.
            style_function (function): Optional base style function.
            **kwargs: Additional arguments for folium.GeoJson.

        Raises:
            TypeError: If data is not a string or dictionary.
            ValueError: If data is not a valid GeoJSON.
        """
        import geopandas as gpd
        import folium

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            geojson = gdf.__geo_interface__
        elif isinstance(data, dict):
            geojson = data
        else:
            raise TypeError("Data must be a file path or GeoJSON dictionary.")

        # Default style (optional)
        default_style = style_function or (
            lambda f: {"fillOpacity": 0.5, "weight": 1, "color": "gray"}
        )

        # Optional highlight effect on hover
        highlight_fn = (
            (lambda f: {"weight": 3, "color": "yellow", "fillOpacity": 0.2})
            if highlight
            else None
        )

        # Tooltip configuration
        tooltip = (
            folium.GeoJsonTooltip(
                fields=tooltip_fields,
                aliases=tooltip_aliases or tooltip_fields,
                localize=True,
                sticky=True,
                labels=True,
            )
            if tooltip_fields
            else None
        )

        folium.GeoJson(
            data=geojson,
            style_function=default_style,
            highlight_function=highlight_fn,
            tooltip=tooltip,
            **kwargs,
        ).add_to(self)

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

    def add_choropleth(
        self,
        gdf,
        column,
        join_col,
        key_on="feature.properties.name",
        fill_color="YlGn",
        legend_name=None,
        tooltip_fields=None,
        tooltip_aliases=None,
        **kwargs,
    ):
        """Add a Choropleth layer to the map.

        Args:
            gdf (GeoDataFrame or str): GeoDataFrame or path to file with geometries and data.
            column (str): Column in the GeoDataFrame to color by.
            join_col (str): Column to join GeoJSON and data on.
            key_on (str): GeoJSON property key to match join_col (e.g., 'feature.properties.<name>').
            fill_color (str): Color scheme for the choropleth.
            legend_name (str): Name for the legend.
            **kwargs: Additional arguments for folium.Choropleth.
        """
        import geopandas as gpd
        import json

        # Case 1: file path
        if isinstance(gdf, str):
            gdf = gpd.read_file(gdf)
            gdf = gdf.to_crs(epsg=4326)
            geojson = json.loads(gdf.to_json())

        # Case 2: GeoJSON dictionary
        elif isinstance(gdf, dict):
            if "features" not in gdf:
                raise ValueError("GeoJSON dict must have a 'features' key.")
            try:
                gdf = gpd.GeoDataFrame.from_features(gdf["features"])
                gdf = gdf.set_geometry("geometry").set_crs(epsg=4326)
                geojson = gdf.__geo_interface__  # or json.loads(gdf.to_json())
            except Exception as e:
                raise ValueError(f"Failed to parse GeoJSON dictionary: {e}")

        # Case 3: GeoDataFrame
        elif isinstance(gdf, gpd.GeoDataFrame):
            gdf = gdf.to_crs(epsg=4326)
            geojson = json.loads(gdf.to_json())

        else:
            raise TypeError(
                "gdf must be a GeoDataFrame, file path, or GeoJSON dictionary."
            )

        if join_col not in gdf.columns or column not in gdf.columns:
            raise ValueError(
                f"'{join_col}' and/or '{column}' not found in GeoDataFrame columns: {list(gdf.columns)}"
            )

        folium.Choropleth(
            geo_data=geojson,
            data=gdf[[join_col, column]],
            columns=[join_col, column],
            key_on=key_on,
            fill_color=fill_color,
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name=legend_name or column,
            **kwargs,
        ).add_to(self)

        # Add tooltips on hover (optional)
        if tooltip_fields:
            folium.GeoJson(
                geojson,
                tooltip=folium.GeoJsonTooltip(
                    fields=tooltip_fields,
                    aliases=tooltip_aliases or tooltip_fields,
                    localize=True,
                    sticky=True,
                    labels=True,
                ),
                style_function=lambda x: {
                    "fillOpacity": 0,
                    "weight": 0,
                },  # transparent overlay
            ).add_to(self)
