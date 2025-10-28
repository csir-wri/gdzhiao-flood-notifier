"""Flood alert recipient"""

import enum


class Expertise(enum.IntFlag):
    """Represents the level of expertise of an alert recipient"""

    Basic = 0
    Intermediate = 1
    Expert = 2


class Recipient:
    """Flood alert recipient"""

    # HIGH: Update the tuple when more fields are added
    csv_fields = ("name", "rois", "expertise", "email", "phone")

    def __init__(self, **kwargs):
        """Initializes a new instance of a flood alert recipient."""
        self._name = kwargs["name"]
        self._rois = tuple(roi.strip().lower() for roi in str(kwargs["rois"]).split(";"))
        self._expertise = Expertise(int(kwargs["expertise"]))
        self._emails = tuple(email.strip() for email in str(kwargs["email"]).split(";"))
        self._phone_nums = tuple(num.strip() for num in str(kwargs["phone"]).split(";"))

    @property
    def full_name(self) -> str:
        """Returns the name of the recipient."""
        return self._name

    @property
    def expertise(self) -> Expertise:
        """Gets the expertise of the recipient."""
        return self._expertise

    @property
    def emails(self) -> tuple[str, ...]:
        """Gets this recipient's email addresses.

        Returns:
            tuple[str]: Email addresses of the recipient.
        """
        return self._emails

    @property
    def phone_numbers(self) -> tuple[str, ...]:
        """Gets this recipient's phone numbers.

        Returns:
            tuple[str]: Phone numbers of the recipient.
        """
        return self._phone_nums

    @property
    def rois(self) -> tuple[str, ...]:
        """Gets the IDs of this recipient's regions of interest.

        Returns:
            tuple[str]: Tuple containing the IDs of this recipient's
            regions of interest.
        """
        return self._rois
