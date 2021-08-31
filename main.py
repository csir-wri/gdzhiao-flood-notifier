#! usr/bin/env python3

"""Parses flood model outputs and sends out alerts as required.
"""

from pathlib import Path
from sys import version_info
from typing import Tuple
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
    towns_file = input(
        "Enter the path to the towns shape file:\n > ").strip('"')

    # initialize the model
    ap = model.AlertProcessor()

    ap.load_recipients(recipient_file)
    ap.load_rois(sorted(Path(roi_dir).glob('**/*.shp')))
    ap.load_towns(towns_file)

    # # print(f"  Loaded {len(ap.rois)} ROIs and " +
    # #       f"{sum(len([v['towns'] for v in ap.rois.values()]))} towns.", end='\n')

    print("")

    # use the model output
    model_file = input(
        "Enter the path to the model output TIF file:\n > ").strip('"')

    mailer.initialize()
    for alert in ap.get_alerts(model_file):
        message = _compose_message(alert['roi'], alert['towns'])
        mailer.send_mail(alert["email"], message)

    print("The alert will re-run after 1 hour.")


def _compose_message(roi_name: str, towns: Tuple[str, float]):
    """Composes a an alert email to be sent to the recipients in the system.

    Args:
        roi_name (str): Name of the ROI for which the message is being composed
        towns (Tuple[str, float]): List of tuples containing the names of towns and risk level.

    Returns:
        str: Content of the email to be composed.
    """

    from datetime import datetime  # pylint: disable=import-outside-toplevel

    message = []
    message.extend((f" {'':=^75} ", "",
                    f" {'MiFMASS Flood Alert': ^75} ", "",
                    f" {'':=^75} ", ""))

    message.append(
        f" {'Generated on': <16}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    message.append(f" {'Location': <16}: {roi_name}")
    message.append(f" {'Max Alert Level': <16}: {max(x[2] for x in towns)}")
    message.append("")
    message.append(" Affected Communities:")
    message.append("-" * len(message[-1]))
    message.append("")
    message.append(f" {'Name': <40} {'Level': >10}")
    message.extend(f" {x[1]: <40} {x[2]: >10}"
                   for x in sorted(towns, key=lambda tup: tup[1]))
    message.append("")
    message.append(f" {'':=^75} ")

    return "\n".join(message)


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

except Exception:               # pylint: disable=broad-except
    from sys import exc_info    # pylint: disable=ungrouped-imports

    exc = tuple(str(v) for v in exc_info())
    print("\n".join(["An exception of type occurred while running the script.",
                     "",
                     "Type:     ", exc[0],
                     "Message:  ", exc[1],
                     "Traceback:", exc[2]]))

input("\n\nPress <ENTER> to exit. ")
