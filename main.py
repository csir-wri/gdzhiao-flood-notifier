#! usr/bin/env python3

"""Parses flood model outputs and sends out alerts as required.
"""

from pathlib import Path
from sys import version_info
import mailer
import model


def main():
    """Main entry point for application."""

    print(f" {'':=^75}\n",
          f" {'Flood Alert Notifier': ^75}\n",
          f" {'':=^75}", sep="\n")

    # prompt for path to data files.
    recipient_file = input(
        "Enter the path to the recipient database:\n > ").strip('"')
    roi_dir = input(
        "Enter the path to the folder with the ROI shape files:\n > ").strip('"')
    towns_dir = input(
        "Enter the path to the folder with the towns shape files:\n > ").strip('"')

    # initialize the model
    ap = model.AlertProcessor()

    ap.load_recipients(recipient_file)
    ap.load_rois(sorted(Path(roi_dir).glob('**/*.shp')))
    ap.load_towns(sorted(Path(towns_dir).glob('**/*.shp')))

    # # print(f"  Loaded {len(ap.rois)} ROIs and " +
    # #       f"{sum(len([v['towns'] for v in ap.rois.values()]))} towns.", end='\n')

    print("")

    # use the model output
    model_file = input(
        "Enter the path to the model output TIF file:\n > ").strip('"')

    mailer.initialize()
    for alert in ap.get_alerts(model_file):
        message = mailer.compose_message(alert['roi'], alert['towns'])
        mailer.send_mail(alert["email"], message)

    print("The alert will re-run after 1 hour.")


def _validate_py_version(min_ver):
    """Validates the version of the Python interpreter."""

    if version_info < min_ver:
        print("The minimum version required to run this script is " +
              ".".join(str(x) for x in min_ver))
        return False

    return True


try:
    if _validate_py_version((3, 6)):
        if __name__ == "__main__":
            main()

except Exception as ex:                 # pylint: disable=broad-except
    from traceback import format_exc    # pylint: disable=ungrouped-imports

    print("\n".join(["An exception occurred while running the script.",
                     "",
                     "Type:      " + type(ex).__name__,
                     "Message:   " + next(iter(ex.args), ""),
                     "\n    ".join(format_exc().splitlines()[:-1])]))

input("\n\nPress <ENTER> to exit. ")
