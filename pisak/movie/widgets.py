"""
Module with widgets specific to movie player.
"""
import os

from gi.repository import Mx, Clutter, GObject

import pisak
from pisak import pager, widgets, layout, handlers, unit
from pisak.movie import model


class FlatSource(pager.DataSource):
    """
    Communicate with the library manager and dynamically generates the
    required number of PhotoTiles, each representing one movie from
    the library. Data source suitable for the flat structure of library.
    """
    __gtype_name__ = "PisakMovieFlatSource"

    def __init__(self):
        super().__init__()
        self.data = sorted(list(model.get_library().get_all_items()),
                           key=lambda movie: os.path.basename(movie.path))

    def _produce_item(self, movie):
        tile = widgets.PhotoTile()
        self._prepare_item(tile)
        tile.style_class = "PisakMoviePhotoTile"
        tile.connect("clicked", self.item_handler, movie.id)
        tile.hilite_tool = widgets.Aperture()
        tile.scale_mode = Mx.ImageScaleMode.FIT
        self._set_preview(tile, movie.extra.get("cover"))
        tile.label_text = os.path.splitext(
            os.path.split(movie.path)[-1])[0]
        return tile

    def _set_preview(self, tile, preview_path):
        if not os.path.isfile(preview_path):
            self._schedule_set_preview(tile, preview_path)
        else:
            self._do_set_preview(tile, preview_path)

    def _schedule_set_preview(self, tile, preview_path):
        Clutter.threads_add_timeout(
                0, 1000, self._do_set_preview, tile, preview_path)

    def _do_set_preview(self, tile, preview_path):
        if os.path.isfile(preview_path):
            tile.preview_path = preview_path
            return False
        else:
            return True


class MovieFullscreen(layout.Bin):
    """
    Widget that displays movie in the fullscreen mode.
    """
    __gtype_name__ = "PisakMovieFullscreen"
    __gproperties__ = {
        "engine": (
            Clutter.Actor.__gtype__,
            "", "", GObject.PARAM_READWRITE),
        "exit-button": (
            Clutter.Actor.__gtype__,
            "", "", GObject.PARAM_READWRITE),
        "menu": (
            Clutter.Actor.__gtype__,
            "", "", GObject.PARAM_READWRITE)
    }

    def __init__(self):
        super().__init__()
        self._exit_button = None
        self._engine = None
        self._menu = None
        self._middleware = None
        self._exit_handler = 0
        self._prev_content = None

        self._cover = Clutter.Actor()
        self._cover.set_layout_manager(Clutter.BinLayout())
        self._cover.set_size(unit.w(1), unit.h(1))

        self.fullscreen = False

    @property
    def engine(self):
        """
        Engine that plays the movie.
        """
        return self._engine

    @engine.setter
    def engine(self, value):
        self._engine = value

    @property
    def exit_button(self):
        """
        Button that can be clicked in order to exit a fullscreen mode.
        """
        return self._exit_button

    @exit_button.setter
    def exit_button(self, value):
        self._exit_button = value
        self._cover.add_child(value)

    @property
    def menu(self):
        """
        Button menu of the movie player.
        """
        return self._menu

    @menu.setter
    def menu(self, value):
        self._menu = value

    def toggle_fullscreen(self, *args):
        """
        Enter or exit the fullscreen mode. When entering this widget
        is expanded and put on the top of the main window.

        :param args: args passed by a signal emiter.
        """
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.stage = self.engine.get_stage()
            self.parent = self.engine.get_parent()
            self.parental_idx = self.parent.get_children().index(self.engine)
            self.parent.remove_child(self.engine)
            self.stage.add_child(self.engine)
            self.engine.set_x_expand(True)
            self.engine.set_y_expand(True)
            self._handle_middleware_on()
        else:
            self.stage.remove_child(self.engine)
            self.parent.insert_child_at_index(self.engine, self.parental_idx)
            self._handle_middleware_off()

    def _handle_middleware_on(self):
        self._middleware = pisak.app.window.input_group.middleware
        if self._middleware in (None, "sprite"):
            self.stage.add_child(self._cover)
            if self._middleware == "sprite":
                self._prev_content = pisak.app.window.input_group.content
                pisak.app.window.input_group.stop_middleware()
                pisak.app.window.input_group.load_content(self._cover)
        else:
            pisak.app.window.input_group.stop_middleware()
            signal =  pisak.app.window.input_group.action_signal
            self.engine.set_reactive(True)
            self.stage.set_key_focus(self.engine)
            self._exit_handler = self.engine.connect(signal,
                                                    self.toggle_fullscreen)

    def _handle_middleware_off(self):
        if self._middleware in (None, "sprite"):
            self.stage.remove_child(self._cover)
            if self._middleware == "sprite":
                pisak.app.window.input_group.stop_middleware()
                pisak.app.window.input_group.load_content(self._prev_content)
        else:
            self.engine.set_reactive(False)
            self.engine.disconnect(self._exit_handler)
            pisak.app.window.input_group.run_middleware()

