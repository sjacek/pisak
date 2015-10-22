"""
Module to govern all the user's directories that are used by Pisak applications.
"""
import os

from gi.repository import GLib

from pisak import res, logger


_LOG = logger.get_logger(__name__)


def ensure_dir(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    return dirpath


# ---------------------------

# HOME general specification

# ---------------------------

"""
Path to the user's home directory.
"""
HOME = os.path.expanduser("~")

"""
Path to a folder in user's home directory. Contains any files that user has
added and wants them to be available inside of some of the Pisak applications
or files that user has access to and can modify them in order to achieve some
kind of different behaviour or look of some of the Pisak applications.
"""
HOME_PISAK_DIR = ensure_dir(os.path.join(HOME, ".pisak"))


# ------------------------------

# HOME files and subdirectories

# ------------------------------
"""
Path to the configurations directory.
"""
HOME_PISAK_CONFIGS = ensure_dir(os.path.join(HOME_PISAK_DIR, "configs"))

"""
Path to the favouritess directory.
"""
HOME_PISAK_FAVOURITES = ensure_dir(os.path.join(HOME_PISAK_DIR, "favourites"))

"""
Path to the databases directory.
"""
HOME_PISAK_DATABASES = ensure_dir(os.path.join(HOME_PISAK_DIR, "databases"))

"""
Directory with logging files.
"""
HOME_LOGS_DIR = ensure_dir(os.path.join(HOME_PISAK_DIR, "logs"))

"""
Directory that contains custom icons created by the user. Each icon's name has
to correspond to the name of an generic icon that it is supposed to replace.
Accepted format of an icon file is SVG.
"""
HOME_ICONS_DIR = ensure_dir(os.path.join(HOME_PISAK_DIR, "icons"))

"""
Path to a subdirectory in user's home Pisak directory. Contains files in
json format, created and added by user when one wants to change the graphical
layout of some of the Pisak applications. Files structure: main 'json' folder
contains subfolders, each for every application, named as the related
application name, then each of these subfolders contains one or more json
files, each file with the same name as of the related view and 'json' extension.
"""
HOME_JSON_DIR = ensure_dir(os.path.join(HOME_PISAK_DIR, "json"))

"""
Path to a subdirectory in user's home Pisak directory. Contains files in
css format, created and added by user when one wants to change the look of
some elements of a graphical interface or of the whole view of some of
the Pisak applications. Files structure: in this folder there can be one
css file for every application, name of each file must be the same as the
application name with 'css' extension.
"""
HOME_STYLE_DIR = ensure_dir(os.path.join(HOME_PISAK_DIR, "css"))

"""
Folder in user's home Pisak directory, that contains custom made symbols
to be used within the 'symboler' application.
Each custom made symbol replaces a default one or, if there is no default,
extends the collection of all symbols.
"""
HOME_SYMBOLS_DIR = ensure_dir(os.path.join(HOME_PISAK_DIR, "symbols"))

"""
Folder in user's home Pisak directory, that contains custom sounds which can be played
during scanning and button selection.
"""
HOME_SOUNDS_DIR = ensure_dir(os.path.join(HOME_PISAK_DIR, "sounds"))

"""
Path to the spreadsheet containing custom symbols topology for
"symboler" application.
"""
HOME_SYMBOLS_SHEETS = ensure_dir(os.path.join(HOME_PISAK_DIR, "symboler_sheets"))


"""
Path to the main configuration file avalaible for the user.
"""
HOME_MAIN_CONFIG = os.path.join(HOME_PISAK_CONFIGS, "main_config.ini")

"""
Path to the symbols model for "symboler" application.
"""
HOME_SYMBOLS_MODEL = os.path.join(HOME_PISAK_DIR, "symbols_model.ini")

"""
Path to the symbols entries file generated by "symboler" application.
"""
HOME_SYMBOLS_ENTRY = os.path.join(HOME_PISAK_DIR, "symbols_entry.ini")

"""
Path to a file containing all information and list of URLs to blogs that are being
followed by the user.
"""
HOME_FOLLOWED_BLOGS = os.path.join(HOME_PISAK_DIR, "followed_blogs.ini")

"""
Path to a file with all the blog settings or configuration parameters, like: user
credentials, blog address etc.
"""
HOME_BLOG_CONFIG = os.path.join(HOME_PISAK_CONFIGS, "blog_config.ini")

"""
Path to a file where all the necessary setting of an email account are stored.
"""
HOME_EMAIL_CONFIG = os.path.join(HOME_PISAK_CONFIGS, "email_config.ini")

"""
Path to the file with email application address book.
"""
HOME_EMAIL_ADDRESS_BOOK = os.path.join(
    HOME_PISAK_DATABASES, "email_address_book.db")

"""
Database with info about text files generated by the 'speller' application.
"""
HOME_TEXT_DOCUMENTS_DB = os.path.join(HOME_PISAK_DATABASES,'documents.db')


# ---------------------------

# Default system directories

# ---------------------------

"""
Dictionary with paths to various file system default directories.
"""
USER_FOLDERS = {
    "desktop": GLib.USER_DIRECTORY_DESKTOP,
    "documents": GLib.USER_DIRECTORY_DOCUMENTS,
    "downloads": GLib.USER_DIRECTORY_DOWNLOAD,
    "music": GLib.USER_DIRECTORY_MUSIC,
    "pictures": GLib.USER_DIRECTORY_PICTURES,
    "public": GLib.USER_DIRECTORY_PUBLIC_SHARE,
    "templates": GLib.USER_DIRECTORY_TEMPLATES,
    "videos": GLib.USER_DIRECTORY_VIDEOS
}


# ----------------------------------------------------

# Functions managing content from various directories

# ----------------------------------------------------

def find_path(folder1, folder2, file_name, with_raise=False,
              custom_msg=''):
    """
    Helper function to check if the file is in one folder or the other.

    :param folder1: str, full path to user folder to check
    :param folder2: str, name of folder in PISAK res folder in which to check
    :param file_name: str, name of the file
    :param with_raise: bool, whether to raise an error or log a warning
    :param custom_msg: str, custom_msg for the error, should contain two '{}'
    specifying the places for the file paths

    :returns: path to the found file or None
    """
    msg = custom_msg or 'No such file found as {} or {}.'
    path = path1 = os.path.join(folder1, file_name)
    if not os.path.isfile(path1):
        path = path2 = os.path.join(res.get(folder2), file_name)
        if not os.path.isfile(path2):
            msg = msg.format(path1, path2)
            path = None
            if with_raise:
                raise FileNotFoundError(msg)
            else:
                _LOG.warning(msg)
    return path

def get_general_configs():
    """
    Get paths to files with general configuration.

    :returns: list of configuration files, from the most default
    to the most custom one
    """
    configs = []
    default = res.get(os.path.join('configs', 'default_config.ini'))
    if os.path.isfile(default):
        configs.append(default)
    else:
        raise FileNotFoundError(
            "Default general config not found in the res directory.")
    if os.path.isfile(HOME_MAIN_CONFIG):
        configs.append(HOME_MAIN_CONFIG)
    return configs


def get_icon_path(name):
    """
    Get path to an icon with the given name. First look for a custom one in
    user home directory, if nothing found, then look for a default one in
    res directory. Accepted file format is SVG.

    :param name: name of the icon, that is a name of the file containing the
    icon without an extension. Accepted file format is SVG.

    :returns: path to the icon or None if nothing was found
    """
    full_name = name + '.svg'
    icon_path = find_path(HOME_ICONS_DIR, 'icons', full_name,
                          with_raise=True,
                          custom_msg='No such icon found as {} or {}.')
    return icon_path


def get_css_path(skin='default'):
    """
    Get css file with the global style description for the whole program.
    Hierarchy of directories being scanned in search for the proper file is
    as follows: first the pisak directory in user's home,
    then css folder in res.

    Structure of style related directories: in pisak folder in user's home -
    'css' folder with css files named the same as the given skin;
    in res directory - the same as in the home.

    :param skin: name of the skin or None for default css

    :returns: path to css file
    """
    full_name = skin + '.css'
    css_path = find_path(HOME_STYLE_DIR, 'css', full_name, with_raise=True,
                         custom_msg="Css not found in {} or {}.")
    return css_path


def get_blog_css_path():
    """
    Get css file to style Blog posts.
    """
    full_name = 'blog_style.css'
    css_path = find_path(HOME_STYLE_DIR, 'css', full_name, with_raise=True,
                         custom_msg='CSS file not found as {} or {}.')
    return css_path


def get_json_path(view, layout='default', app='',):
    """
    Get a json file responsible for building one of the views of the given
    application. Shape of the view is described by 'layout' parameter.
    Hierarchy of directories being scanned in search for the proper file is
    as follows: first the pisak directory in user's home, then json
    directory in res for the specific layout and finally json directory in
    res for the default layout.

    Structure of json related directories: in pisak folder in user's home -
    'json' folder with subfolders for different applications, each named as
    the corresponding application, then in each of them subfolders for
    specific 'layout' with 'json' extended  files inside;
    in res directory - the same as for the home.

    :param view: name of the view
    :param layout: name of the layout of the view or None for default layout
    :param app: name of the application or None, when None then general
    jsons are looked for.

    :returns: path to the json file
    """
    # check home pisak dir
    view_path = os.path.join(HOME_JSON_DIR, app, layout, view) + ".json"
    # if none has been found look in res directory:
    if not os.path.isfile(view_path):
        json_dir = res.get(os.path.join("json", app, layout))
        view_path = os.path.join(json_dir, view) + ".json"
        if not os.path.isfile(view_path) and layout is not "default":
            default_json_dir = res.get(os.path.join("json", app, "default"))
            view_path = os.path.join(default_json_dir, view) + ".json"
    if not os.path.isfile(view_path):
        msg = "Default json for '{}' view of the '{}' application not " \
            "found in the res directory."
        raise FileNotFoundError(msg.format(view, app))
    return view_path


def get_user_dir(folder):
    """
    Get path to one of the XDG user folders.

    :param folder: folder name as str, lowercase, possible are:
    desktop, documents, downloads, music, pictures, public, templates, videos

    :returns: path to XDG user directory
    """
    return GLib.get_user_special_dir(USER_FOLDERS[folder])


def get_sound_path(name):
    """
    Get path to a sound with the given name. First look for a custom sound in
    user home directory, if nothing found, then look for a default sound in
    res directory. Accepted file format is wav.

    :param name: name of the sound file, that is a name of the file without an extension. 
    Accepted file format is WAV.

    :returns: path to the sound or None if nothing was found.
    """
    name = name.lower().replace(' ', '_').replace('\n', '_')
    sound_path = find_path(HOME_SOUNDS_DIR, 'sounds', name,
                           custom_msg='No sound file found as {} or {}.')
    return sound_path


def get_symbols_spreadsheet(name):
    """
    Get path to a spreadsheet with the given name.

    :param name: name of the spreadsheet.

    :return: path to the spreadsheet.
    """
    full_name = name + '.ods'
    path = find_path(HOME_SYMBOLS_SHEETS, 'symboler_sheets', full_name,
                     with_raise=True,
                     custom_msg='No such spreadsheet found as {} or {}.')
    return path


def get_symbol_path(name):
    """
    Get full path to a symbol with the given name.

    :param name: name of a symbol, without any extension.

    :return: path to a symbol, string.
    """
    full_name = name + '.png'
    path = find_path(HOME_SYMBOLS_DIR, 'symbols', full_name,
                     with_raise=True)
    return path
