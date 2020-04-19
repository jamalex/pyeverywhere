import json
import os
import shutil
import struct
import subprocess

default_key = "default"
pew_config = {}

cwd = os.getcwd()
thisdir = os.path.dirname(os.path.abspath(__file__))
rootdir = os.path.abspath(os.path.join(thisdir, "..", "..", ".."))

config_dir = os.path.expanduser(os.path.join("~", ".pyeverywhere"))
if not os.path.exists(config_dir):
    os.makedirs(config_dir)

config_file = os.path.join(config_dir, "config.json")


def load_pew_config(filename=config_file):
    """
    Loads the current PyEverywhre configuration settings from disk.
    """
    global pew_config
    if not filename:
        filename = config_file

    if os.path.exists(filename):
        pew_config = json.load(open(filename))

    return pew_config


def save_pew_config(filename=config_file):
    """
    Save the current pew configuration settings to disk.

    :param filename: Path to file
    """
    global pew_config
    if pew_config:
        data = json.dumps(filename)
        f = open(config_file, 'w')
        f.write(data)
        f.close()


def set_project_info(info):
    global info_json
    info_json = info


def get_value_for_platform(key, platform_name, default_return=None):
    global info_json
    if key in info_json:
        if platform_name in info_json[key]:
            return info_json[key][platform_name]
        elif default_key in info_json[key]:
            return info_json[key][default_key]

    return default_return


def get_value_for_config(key, config_name, default_return=None):
    if key in info_json:
        if "configs" in info_json[key] and config_name in info_json[key]["configs"]:
            return info_json[key]["configs"][config_name]
        elif default_key in info_json[key]:
            return info_json[key][default_key]

    return default_return


def copy_files(src_dir, build_dir, ignore_paths):
    def _logpath(path, names):
        for ignore_dir in ignore_paths:
            if ignore_dir in path:
                print("Ignoring %s" % path)
                return names
        print("Copying %s" % path)
        return []
    ignore = _logpath

    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    print("Copying source files to build tree, please wait...")
    shutil.copytree(src_dir, build_dir, ignore=ignore)

    shutil.copy2(os.path.join(cwd, "project_info.json"), build_dir)

def copy_data_files(data_files, build_dir):
    for out_dir, files in data_files:
        out_dir = os.path.join(build_dir, out_dir)
        for filename in files:
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            shutil.copy(filename, out_dir)


def copy_pew_module(build_dir):
    pew_src_dir = os.path.join(rootdir, "src", "pew")
    pew_dest_dir = os.path.join(build_dir, "pew")
    # For now, we want to allow developers to use their own customized pew module
    # until we offer more advanced configuration options. If they don't though,
    # just copy ours over.
    if not os.path.exists(pew_dest_dir):
        shutil.copytree(pew_src_dir, pew_dest_dir)


def is_png(data):
    return (data[:8] == '\211PNG\r\n\032\n'and (data[12:16] == 'IHDR'))


def get_image_info(filename):
    f = open(filename, 'rb')
    data = f.read(25)
    if is_png(data):
        w, h = struct.unpack('>LL', data[16:24])
        width = int(w)
        height = int(h)
    else:
        raise Exception('not a png image')
    return width, height