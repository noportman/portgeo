"""Main module."""

import os
import ipyleaflet


class Map(ipyleaflet.Map):
    """Custom Map class to handle portgeos."""

    def __init__(
        self, center=[20, 0], zoom=2, scroll_wheel_zoom=True, height="400px", **kwargs
    ):
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.scroll_wheel_zoom = scroll_wheel_zoom
        self.layout.height = height

    def add_basemap(self, basemap="OpenStreetMap"):
        """Add a basemap to the map."""

        url = eval(f"ipyleaflet.basemaps.{basemap}").build_url()
        layer = ipyleaflet.TileLayer(url=url, name=basemap)
        self.add(layer)

    def add_google_map(self, map_type="roadmap"):
        """Add a Google Map to the map."""

        map_types = {"roadmap": "r", "satellite": "s", "hybrid": "y", "terrain": "p"}
        map_type = map_types[map_type.lower()]

        url = f"https://mt1.google.com/maps/vt/lyrs={map_type}&x={{x}}&y={{y}}&z={{z}}"
        layer = ipyleaflet.TileLayer(url=url, name=f"Google {map_type.capitalize()}")
        self.add(layer)

    def add_geojson(self, data, zoom_to_layer=True, hover_style=None, **kwargs):
        """Add a GeoJSON layer to the map."""

        import geopandas as gpd

        if hover_style is None:
            hover_style = {
                "color": "yellow",
                "fillColor": "yellow",
                "fillOpacity": 0.5,
                "weight": 2,
            }

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            geojson = gdf.__geo_interface__

        elif isinstance(data, dict):
            geojson = data

        layer = ipyleaflet.GeoJSON(data=geojson, hover_style=hover_style, **kwargs)
        self.add_layer(layer)

        if zoom_to_layer:
            bounds = gdf.total_bounds
            self.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

    def add_shp(self, data, **kwargs):
        """Add a shapefile layer to the map."""

        import geopandas as gpd

        gdf = gpd.read_file(data)
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_gdf(self, gdf, **kwargs):
        """Add a GeoDataFrame layer to the map."""

        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_vector(self, data, **kwargs):
        """Add a vector layer to the map."""

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
