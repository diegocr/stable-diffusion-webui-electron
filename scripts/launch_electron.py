from modules.shared import cmd_opts
from modules import script_callbacks
from modules import shared
from pathlib import Path
from shutil import which
import subprocess
import os

electron_exe = None


def setup_electron():
    global electron_exe
    try:
        electron_dir = Path(__file__).parents[1].joinpath("electron")
        if not os.path.exists(electron_dir):
            os.makedirs(electron_dir)
            subprocess.run([which("npm"), "init", "-y"], cwd=electron_dir)
            subprocess.run([which("npm"), "install", "electron", "--save-dev"], cwd=electron_dir)
        electron_exe = subprocess.check_output(["node", "-p", "require('electron')"], cwd=electron_dir).strip()
        os.environ.setdefault('SD_WEBUI_RESTARTING', '1')  # test use
    except Exception as e:
        print(e)


def test_auto_launch():
    auto_launch_browser = False
    if os.getenv('SD_WEBUI_RESTARTING') != '1':
        try:
            if shared.opts.auto_launch_browser == "Remote" or cmd_opts.autolaunch:
                auto_launch_browser = True
            elif shared.opts.auto_launch_browser == "Local":
                auto_launch_browser = not any([cmd_opts.listen, cmd_opts.share, cmd_opts.ngrok])
        except AttributeError:  # compatibility for webui < 1.6.0
            auto_launch_browser = cmd_opts.autolaunch and os.getenv('SD_WEBUI_RESTARTING') != '1'

    if auto_launch_browser:
        setup_electron()


def launch_electron(demo, _):
    if electron_exe:
        try:
            electron_args = [
                "--disable-renderer-backgrounding"
            ]
            subprocess.run([electron_exe] + electron_args + [demo.local_url])
        except OSError as ex:
            print('Failed running electron...', ex)


script_callbacks.on_before_ui(test_auto_launch)
script_callbacks.on_app_started(launch_electron)
