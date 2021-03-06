"""
Basic classes for Pisak application.
"""
import sys
import os

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('ClutterGst', '2.0')
gi.require_version('GtkClutter', '1.0')

from gi.repository import GObject, Gtk, Clutter, Mx, ClutterGst, GtkClutter

import pisak
from pisak import res, logger, sound_effects, window, configurator, \
    dirs, unit, arg_parser


_LOG = logger.get_logger(__name__)


class _Application(configurator.Configurable):
    """
    Abstract application class. This is the entry point for all Pisak apps.
    On init it initializes the application stage, style and global
    sound effects player.

    :param argv: application arguments.
    :param descriptor: general application descriptor.
    """
    def __init__(self, argv, descriptor):
        super().__init__()
        Clutter.init(sys.argv)

        # application main window, instance of :see: :class: `window.Window`:
        self.window = None

        # path to a file with style definition:
        self.style = None

        # dictionary for all the application basic elements:
        self.box = {}

        # if playing of the sound effects should be enabled:
        self.sound_effects_enabled = False

        # indicator of the application main loop status, should be used
        # with caution as there will always be some non-zero time interval
        # between setting this flag 'True' and actual launching of the loop and
        # between actual quit of the loop and setting the flag 'False':
        self.main_loop_is_running = False

        # player of any audio effects:
        self.sound_effects_player = None

        self._sound_effects = {}

        self._read_descriptor(descriptor)
        self._configure()
        self._initialize_style()
        self._initialize_window(argv, descriptor)
        self._initialize_sound_effects_player()

    def _read_descriptor(self, descriptor):
        """
        Read the given descriptor and adjust the application.

        :param descriptor: dictionary with the application description.
        """
        app_elements = descriptor.get("elements")
        if app_elements:
            self._register_app_elements(app_elements)

    def _register_app_elements(self, elements):
        """
        Register all basic elements that will be used by the application. Elements are
        put inside the 'box' dictionary and then avalaible throughout the entire
        lifetime of the application.

        :param elements: dictionary with application basic elements.
        """
        self.box.update(elements)

    def _configure(self):
        self.apply_props()
        self.sound_effects_enabled = self.config.as_bool("sound_effects_enabled")
        self.style = dirs.get_css_path(self.config.get("skin"))
        for k, v in self.config.get("sound_effects").items():
            path = dirs.get_sound_path(v)
            if path:
                self._sound_effects[k] = path

    def _initialize_style(self):
        try:
            Mx.Style.get_default().load_from_file(self.style)
        except GObject.GError as e:
            _LOG.error(e)
            raise Exception("Failed to load default style.")

    def _initialize_window(self, argv, descriptor):
        self.window = self.create_window(argv, descriptor)

    def _initialize_sound_effects_player(self):
        if self.sound_effects_enabled:
            self.sound_effects_player = sound_effects.SoundEffectsPlayer(
                self._sound_effects)

    def play_sound_effect(self, sound_name):
        """
        Play one of the previously instantiated sound effects by the means of
        an internal player.

        :param sound_name: name of the sound to be played.
        """
        if self.sound_effects_player is not None:
            self.sound_effects_player.play(sound_name)

    def create_window(self, argv, descriptor):
        """
        Abstract method which should create Clutter.Stage instance.

        :param: argv: application arguments.
        :param descriptor: general application descriptor.
        """
        raise NotImplementedError

    def _do_main(self, message, loop):
        """
        Start the application main loop, set the proper flag,
        finally take any clean-up actions.

        :param message: debug message, should indicate the type of the
        application being started.
        :param loop: callable, main loop of the application.
        """
        _LOG.debug(message)
        self.main_loop_is_running = True
        try:
            loop()
        finally:
            self.main_loop_is_running = False

    def main(self):
        """
        Abstract method that starts the application main loop. Any child
        class overriding this method should call the `_do_main` method where
        the proper starting and any cleaning actions take place.
        """
        raise NotImplementedError

    def main_quit(self):
        """
        Quit the application. To be implemented by application classes based on some
        specific backend.
        """
        raise NotImplementedError


class ClutterApp(_Application):
    """
    Implementation of a Clutter-based application.
    """

    def create_window(self, argv, descriptor):
        """
        Create application main window as the Clutter.Stage.

        :param: argv: application arguments.
        :param descriptor: general application descriptor.
        """
        clutter_window = window.Window(self, Clutter.Stage(), descriptor)
        clutter_window.stage.set_title('PISAK')
        clutter_window.stage.set_position(unit.MONITOR_X, unit.MONITOR_Y)
        if arg_parser.get_args().debug:
            coeff = 0.7
            clutter_window.stage.set_size(coeff*unit.w(1), coeff*unit.h(1))
            clutter_window.stage.set_user_resizable(True)
        else:
            clutter_window.stage.set_size(unit.w(1), unit.h(1))
            clutter_window.stage.set_fullscreen(True)
        clutter_window.stage.connect("destroy", lambda _: Clutter.main_quit())
        return clutter_window

    def main(self):
        """
        Start the application main loop.
        """
        self.window.stage.show_all()
        self._do_main("Running Clutter loop.", Clutter.main)

    def main_quit(self):
        """
        Quit the application. Destroying the main window stage triggers
        `Clutter.main_quit` function which stops the main application loop.
        """
        self.window.stage.destroy()


class GtkApp(_Application):
    """
    Implementation of application for JSON descriptors inside GtkWindow.
    """

    def __init__(self, argv, descriptor):
        Gtk.init(sys.argv)
        super().__init__(argv, descriptor)

    def create_window(self, argv, descriptor):
        """
        Create application main window as the Gtk.Window.

        :param: argv: application arguments.
        :param descriptor: general application descriptor.
        """
        gtk_window = Gtk.Window()
        embed = GtkClutter.Embed()
        gtk_window.add(embed)
        gtk_window.stage = embed.get_stage()
        clutter_window = window.Window(self, gtk_window.stage, descriptor)
        clutter_window.wrapper = gtk_window
        gtk_window.stage.set_title('PISAK')
        gtk_window.stage.set_position(unit.MONITOR_X, unit.MONITOR_Y)
        if arg_parser.get_args().debug:
            coeff = 0.7
            size = coeff*unit.w(1), coeff*unit.h(1)
            gtk_window.stage.set_size(*size)
            gtk_window.set_default_size(*size)
            gtk_window.set_resizable(True)
        else:
            gtk_window.stage.set_size(unit.w(1), unit.h(1))
            gtk_window.stage.set_fullscreen(True)
            gtk_window.fullscreen()
        gtk_window.connect("destroy", lambda _: Gtk.main_quit())
        return clutter_window

    def main(self):
        """
        Start the application main loop.
        """
        self.window.wrapper.show_all()
        self._do_main("Running GTK loop.", Gtk.main)

    def main_quit(self):
        """
        Quit the application. Destroying the Gtk window triggers
        `Gtk.main_quit` function which stops the main application loop.
        """
        self.window.wrapper.destroy()
