#! usr/bin/env python3

"""Parses flood model outputs and sends out alerts as required."""

import argparse
import getpass
import sys
from collections import namedtuple
from pathlib import Path

import mailer
import model
from mailer import LoginResult
from model.secrets import EncryptedSecrets

DataFileInfo = namedtuple("DataFileInfo", ("description", "pattern"))


def parse_args():
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument(
        "--config_dir",
        type=Path,
        required=True,
        help="Path to the folder containing encrypted secrets and config files.",
    )
    parser.add_argument(
        "--data_dir",
        type=Path,
        required=True,
        help="Path to the folder containing forecast data files.",
    )

    # Do a raw parse of the args to detect if help was requested
    if any(arg.casefold() in ("-h", "--help") for arg in sys.argv[1:]) or len(sys.argv[1:]) == 0:
        parser.print_help()
        sys.exit(0)

    args, _ = parser.parse_known_args()

    # find missing args and display them to the user
    missing = []
    if args.config_dir is None:
        missing.append("--config_dir")
    if args.data_dir is None:
        missing.append("--data_dir")

    if missing:
        print(
            "\nMissing required arguments: ",
            *(f"  {m}" for m in missing),
            "",
            "Use --help to see available options.\n",
            sep="\n",
        )
        parser.print_help()
        sys.exit(1)
    return args


def get_email_credentials():
    return (input("Email address: ").strip(), getpass.getpass("Password: "))


def ensure_email_access(config_dir, secrets):
    updated_credentials = False
    if any(k not in secrets for k in ("email", "password")):
        print(
            "Email credentials not located.\n",
            "Enter the credentials for the email account used to send alerts.",
            sep="\n",
        )

        updated_credentials = True
        secrets["email"], secrets["password"] = get_email_credentials()

    # failed to log in; prompt to reenter
    while (
        lr := mailer.login(secrets["email"], secrets["password"])
    ) == LoginResult.InvalidCredentials:
        print(
            "Incorrect email credentials.\n",
            "Reenter the credentials for the email account used to send alerts.",
            sep="\n",
        )

        updated_credentials = True
        secrets["email"], secrets["password"] = get_email_credentials()

    # save updated credentials to the secrets file on successful login
    if lr == LoginResult.Success and updated_credentials:
        EncryptedSecrets(config_dir).save(secrets)

    return lr == LoginResult.Success


def main():
    """Main entry point for application."""

    print(
        f" {'':=^75}\n",
        f" {'GDZHIAO Flood Forecast System (GFFS)': ^75}",
        f" {'Flood Alert Notifier': ^75}\n",
        f" {'':=^75}",
        "",
        sep="\n",
    )
    run_args = parse_args()

    # initialize mail account
    secrets = EncryptedSecrets(run_args.config_dir.resolve()).load()
    mailer.initialize()

    # email addres or password not found; prompt to reenter
    if not ensure_email_access(run_args.config_dir.resolve(), secrets):
        print("Could not log in to alert dissemination email account.")
        sys.exit(1)

    have_all_files, data_files = read_data_files(run_args.data_dir.resolve())

    if not have_all_files:
        print(
            "",
            "One or more required data file was not found.",
            "The alert processor will retry on the next cycle.",
            sep="\n",
        )

    # initialize the model
    ap = model.AlertProcessor()
    ap.load_recipients(data_files["recipients"][0])
    ap.load_forecasts(data_files["forecasts"])

    for alert in ap.get_current_alerts():
        message = ap.compose_email_alert(alert.locations)
        mailer.send_mail(alert.email, message)

    print("The alert will re-run after six hours.")


def read_data_files(data_dir: Path):
    """Validate the data files in the given directory."""
    expected_files = {
        "recipients": DataFileInfo("Recipients CSV", "./recipients.csv"),
        "forecasts": DataFileInfo("Forecasts", "./forecasts/*.csv"),
    }

    result = {key: list(data_dir.glob(val.pattern)) for key, val in expected_files.items()}

    for name, info in expected_files.items():
        found_files = result[name]
        found_files_text = {0: "Not found", 1: found_files[0].name}.get(
            len(found_files), f"{len(found_files)} files"
        )
        print(f" > {info.description}: {found_files_text}")

    return all(len(v) > 0 for v in result.values()), result


def _ensure_min_python_version(min_ver):
    """Validates the version of the Python interpreter."""

    if sys.version_info < min_ver:
        print(
            "The minimum version required to run this script is "
            + ".".join(str(x) for x in min_ver)
        )
        return False

    return True


if __name__ == "__main__":
    try:
        if _ensure_min_python_version((3, 10)):
            main()

    except Exception as ex:  # pylint: disable=broad-except
        # pylint: disable=ungrouped-imports
        import tempfile
        from traceback import format_exc

        dump = "\n".join(
            [
                "An exception occurred while running the script.",
                "",
                "Type:      " + type(ex).__name__,
                "Message:   " + str(next(iter(ex.args), "")),
                "\n    ".join(format_exc().splitlines()[:-1]),
            ]
        )

        with tempfile.NamedTemporaryFile(
            prefix="GFFS_Alert_", suffix=".log", mode="w+", delete=False
        ) as tf:
            tf.write(dump)
            dump += f"\n\nError dump: {tf.name}"

        print(dump)

input("\n\nPress <ENTER> to exit. ")
