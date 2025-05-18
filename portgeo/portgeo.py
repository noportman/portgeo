"""Main module."""

import os
import ipyleaflet
import ipywidgets as widgets
from IPython.display import display
from IPython.display import HTML


class Map(ipyleaflet.Map):
    """Custom Map class to handle portgeos.

    Args:
        center (list): Center of the map.
        zoom (int): Zoom level of the map.
        scroll_wheel_zoom (bool): Enable scroll wheel zoom.
        height (str): Height of the map.
        **kwargs: Additional arguments for ipyleaflet.Map.
    """

    def __init__(
        self, center=[20, 0], zoom=2, scroll_wheel_zoom=True, height="400px", **kwargs
    ):
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.scroll_wheel_zoom = scroll_wheel_zoom
        self.layout.height = height
        self.add_toolkit()

    def add_basemap(self, basemap="OpenStreetMap"):
        """Add a basemap to the map.

        Args:
            Options: 'OpenStreetMap.Mapnik', 'OpenStreetMap.France', 'OpenStreetMap.HOT', 'OpenTopoMap',
                            'Gaode.Normal', 'Gaode.Satellite', 'Esri.WorldStreetMap', 'Esri.WorldTopoMap', 'Esri.WorldImagery',
                            'Esri.NatGeoWorldMap', 'CartoDB.Positron', 'CartoDB.DarkMatter', 'NASAGIBS.ModisTerraTrueColorCR',
                            'NASAGIBS.ModisTerraBands367CR', 'NASAGIBS.ModisTerraBands721CR', 'NASAGIBS.ModisAquaTrueColorCR',
                            'NASAGIBS.ModisAquaBands721CR', 'NASAGIBS.ViirsTrueColorCR', 'NASAGIBS.ViirsEarthAtNight2012',
                            'Strava.All', 'Strava.Ride', 'Strava.Run', 'Strava.Water', 'Strava.Winter'.
        """

        url = eval(f"ipyleaflet.basemaps.{basemap}").build_url()
        layer = ipyleaflet.TileLayer(url=url, name=basemap)
        self.add(layer)

    def add_toolkit(self, basemaps=None, position="topright"):
        import ipywidgets as widgets
        import ipyleaflet

        if basemaps is None:
            basemaps = [
                "OpenStreetMap.Mapnik",
                "OpenTopoMap",
                "Esri.WorldImagery",
                "Gaode.Satellite",
                "CartoDB.DarkMatter",
                "CartoDB.Positron",
            ]

        # Master toggle to open/close toolkit
        toolkit_toggle = widgets.ToggleButton(
            value=False,
            icon="cogs",  # Or "wrench", "tools", "gear"
            tooltip="Toggle widget toolkit",
            layout=widgets.Layout(width="38px", height="38px"),
        )

        # Individual toggles
        map_toggle = widgets.ToggleButton(
            value=False,
            icon="map",
            tooltip="Toggle basemap selector",
            layout=widgets.Layout(width="38px", height="38px"),
            button_style="info",
        )

        opacity_toggle = widgets.ToggleButton(
            value=False,
            icon="adjust",
            tooltip="Toggle opacity control",
            layout=widgets.Layout(width="38px", height="38px"),
            button_style="info",
        )

        # close_btn = widgets.Button(icon="times", tooltip="Close panel",
        #                         layout=widgets.Layout(width="38px", height="38px"))

        # Basemap dropdown
        basemap_dropdown = widgets.Dropdown(
            options=basemaps,
            value=basemaps[0],
            description="Basemap:",
            layout=widgets.Layout(width="250px", height="38px"),
            style={"description_width": "initial"},
        )

        # Opacity slider
        opacity_slider = widgets.IntSlider(
            value=100,
            min=0,
            max=100,
            step=1,
            description="Opacity (%)",
            layout=widgets.Layout(width="250px", height="38px"),
        )

        # Toolkit header row
        button_row = widgets.HBox([map_toggle, opacity_toggle])

        # Main container
        container = widgets.VBox([toolkit_toggle])  # initially only toolkit button

        # Helper to get current basemap
        def get_current_basemap():
            for layer in reversed(self.layers):
                if isinstance(layer, ipyleaflet.TileLayer):
                    return layer
            return None

        # Layout update logic
        def update_container():
            children = [toolkit_toggle]
            if toolkit_toggle.value:
                children.append(button_row)
                if map_toggle.value:
                    children.append(basemap_dropdown)
                if opacity_toggle.value:
                    children.append(opacity_slider)
            container.children = children

        # Event listeners
        toolkit_toggle.observe(lambda c: update_container(), names="value")
        map_toggle.observe(lambda c: update_container(), names="value")
        opacity_toggle.observe(lambda c: update_container(), names="value")
        # close_btn.on_click(lambda b: container.close())

        # Functional logic
        basemap_dropdown.observe(
            lambda change: (
                self.remove_layer(get_current_basemap()),
                self.add_basemap(change["new"]),
                setattr(get_current_basemap(), "opacity", opacity_slider.value / 100),
            ),
            names="value",
        )

        opacity_slider.observe(
            lambda change: setattr(
                get_current_basemap(), "opacity", change["new"] / 100
            ),
            names="value",
        )

        # Initial state
        update_container()

        # Add to map
        control = ipyleaflet.WidgetControl(widget=container, position=position)
        self.add(control)

    def add_widget(self, widget, position="topright", **kwargs):
        """Add a widget to the map.
        Args:
            widget (ipywidgets.Widget): Widget to add.
            position (str): Position of the widget.
            **kwargs: Additional arguments for ipyleaflet.WidgetControl.
        """

        control = ipyleaflet.WidgetControl(widget=widget, position=position, **kwargs)
        self.add(control)

    def add_google_map(self, map_type="roadmap"):
        """Add a Google Map to the map.

        Args:
            map_type (str): Type of Google Map to add.
                Options: 'roadmap', 'satellite', 'hybrid', 'terrain'.
        """

        map_types = {"roadmap": "r", "satellite": "s", "hybrid": "y", "terrain": "p"}
        map_type = map_types[map_type.lower()]

        url = f"https://mt1.google.com/maps/vt/lyrs={map_type}&x={{x}}&y={{y}}&z={{z}}"
        layer = ipyleaflet.TileLayer(
            url=url, name=f"Google {map_type.capitalize()}", attribution="Google"
        )
        self.add(layer)

    def add_geojson(self, data, zoom_to_layer=True, hover_style=None, **kwargs):
        """Add a GeoJSON layer to the map.

        Args:
            data (str or dict): Path to the GeoJSON file or GeoJSON data.
            zoom_to_layer (bool): Whether to zoom to the layer bounds.
            hover_style (dict): Style for hover effect.
            **kwargs: Additional arguments for ipyleaflet.GeoJSON.
        """

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
        """Add a shapefile layer to the map.

        Args:
            data (str): Path to the shapefile.
            **kwargs: Additional arguments for ipyleaflet.GeoJSON.
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
            **kwargs: Additional arguments for ipyleaflet.GeoJSON.
        """

        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_vector(self, data, **kwargs):
        """Add a vector layer to the map.

        Args:
            data (str or geopandas.GeoDataFrame or dict): Path to the vector file,
                GeoDataFrame, or GeoJSON data.
            **kwargs: Additional arguments for ipyleaflet.GeoJSON.

        Raises:
            ValueError: If the data type is unsupported.
        """

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

    def add_layer_control(self, **kwargs):
        """Add a layer control to the map.

        Args:
            **kwargs: Additional arguments for ipyleaflet.LayersControl.
        """

        layer_control = ipyleaflet.LayersControl(position="topright", **kwargs)
        self.add_control(layer_control)

    def add_fullscreen(self, **kwargs):
        """Add a fullscreen control to the map.

        Args:
            **kwargs: Additional arguments for ipyleaflet.FullScreenControl.
        """

        fullscreen = ipyleaflet.FullScreenControl(position="topright", **kwargs)
        self.add_control(fullscreen)

    def add_raster(self, filepath, **kwargs):
        """Add a raster layer to the map.
        Args:
            filepath (str): Path to the raster file.
            **kwargs: Additional arguments for localtileserver.TileClient.
        """

        from localtileserver import TileClient, get_leaflet_tile_layer

        client = TileClient(filepath)
        tile_layer = get_leaflet_tile_layer(client, **kwargs)

        self.add(tile_layer)
        self.center = client.center()
        self.zoom = client.default_zoom

    def add_image(self, image, bounds=None, **kwargs):
        """Add an image layer to the map.

        Args:
            image (str): Path to the image file.
            bounds (list, optional): Bounds of the image in the format [[lat1, lon1], [lat2, lon2]].
            **kwargs: Additional arguments for ipyleaflet.ImageOverlay.
        """

        if bounds is None:
            bounds = [[-90, -180], [90, 180]]

        layer = ipyleaflet.ImageOverlay(url=image, bounds=bounds, **kwargs)
        self.add(layer)

    def add_video(self, video, bounds=None, **kwargs):
        """Add a video layer to the map.

        Args:
            video (str): Path to the video file.
            bounds (list, optional): Bounds of the video in the format [[lat1, lon1], [lat2, lon2]].
            **kwargs: Additional arguments for ipyleaflet.VideoOverlay.
        """

        if bounds is None:
            bounds = [[-90, -180], [90, 180]]

        layer = ipyleaflet.VideoOverlay(url=video, bounds=bounds, **kwargs)
        self.add(layer)

    def add_wms_layer(
        self, url, layers, format="image/png", transparent=True, **kwargs
    ):
        """Add a WMS layer to the map.

        Args:
            url (str): URL of the WMS service.
            layers (str): Comma-separated list of layer names.
            **kwargs: Additional arguments for ipyleaflet.WMSLayer.
        """

        layer = ipyleaflet.WMSLayer(
            url=url, layers=layers, format=format, transparent=transparent, **kwargs
        )
        self.add(layer)
