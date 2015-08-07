import re
import sys
import json


dateformat = re.compile(r"^20\d{2}_[0,1]\d_[0-3]\d$")
emailformat = re.compile(r"^\w+@\w+\.[a-z]{2,3}$")
booleanformat = re.compile(r"^(yes|no|Yes|No)$")
timingformat = re.compile(r"^\d{2}:[0-5]\d:[0-5]\d$")


class Card(object):
    _data = None
    _loaded = False
    _has_errors = True  # assume the card is malformed until tested

    def __init__(self, filepath, strict=True):
        self.filepath = filepath
        self.strict = strict

    def parse(self):
        with open(self.filepath) as _file:
            self._data = json.loads(_file.read())
        self._loaded = True
        if self._has_errors:
            self.check_data()
        return self._data

    @property
    def data(self):
        if not self._loaded:
            return self.parse()
        return self._data

    def flush(self):
        """resets all the values and reloads the file
        """
        self._loaded = False
        self._has_errors = True
        self._data = None
        return self.data

    def get_time_tuples(self):
        timings = []
        for work in self.data["works"]:
            timings.append((work["start_time"], work["end_time"]))
        return timings

    def check_data(self):
        """since formatting is going to matter then we need to tell the client
        if they have made any mistakes
        """
        try:
            invalid_format = "value {0} for field {1} is not formatted properly"
            assert self.data["concert_title"], "concert_tile field is required"
            assert dateformat.match(self.data["concert_date"]), "{0} is not in the form"\
                " YYYY_MM_DD".format(self.data["concert_date"])

            if self.strict:
                assert self.data["curators"], "curators field must not be blank"
            assert isinstance(self.data["curators"], list), "curators field must be a list"
            for curator in self.data["curators"]:
                if self.strict:
                    assert curator["name"], "curator.name field must not be blank"
                    assert curator["email"], "curator.email field must not be blank"
                if curator["email"]:
                    assert emailformat.match(curator["email"]), \
                        invalid_format.format(curator["email"], "curator.email")

            assert self.data["works"] and isinstance(self.data["works"], list), \
                "works field must be a non-empty list."
            for work in self.data["works"]:
                if self.strict:
                    assert work["title"], "work.title field must not be blank"

                if self.strict:
                    assert work["composers"], "work.composers field must not be blank"
                assert isinstance(work["composers"], list), "work.composers field must be a list"
                for composer in work["composers"]:
                    if self.strict:
                        assert composer["name"], "composer.name field must not be blank"
                        assert composer["email"], "composer.email field must not be blank"
                    if composer["email"]:
                        assert emailformat.match(composer["email"]), \
                            invalid_format.format(composer["email"], "composer.email")

                assert work["performers"] and isinstance(work["performers"], list), \
                    "work.performers field must be a non-empty list"
                for performer in work["performers"]:
                    if self.strict:
                        assert performer["name"], "performer.name field must not be blank"
                        assert performer["email"], "performer.email field must not be blank"
                    if performer["email"]:
                        assert emailformat.match(performer["email"]), \
                            invalid_format.format(performer["email"], "performer.email")
                    if self.strict:
                        assert performer["instruments"], \
                            "performer.instruments field must be a non-empty list"
                    assert isinstance(performer["instruments"], list), \
                        "performer.instruments field must be a list"

                assert work["allow_streaming"] and booleanformat.match(work["allow_streaming"]), \
                    invalid_format.format(work["allow_streaming"], "work.allow_streaming")
                assert work["allow_download"] and booleanformat.match(work["allow_download"]), \
                    invalid_format.format(work["allow_download"], "work.allow_download")
                assert work["start_time"] and timingformat.match(work["start_time"]), \
                    invalid_format.format(work["start_time"], "work.start_time")
                assert work["end_time"] and timingformat.match(work["end_time"]), \
                    invalid_format.format(work["end_time"], "work.end_time")
                assert sum(int(t) for t in work["end_time"].split(":")) > sum(int(t) for t in work["start_time"].split(":")), "field work.end_time must be greater than field work.start_time"

        except (AssertionError, KeyError) as err:
            error_message = "Error while parsing ::\n\t{0}"
            sys.exit(error_message.format(err))
        else:
            self._has_errors = False
        return self._has_errors


def run():
    import argparse
    import os.path
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filepath",
        help="path to the card you would like to review. for syntax errors."
    )
    parser.add_argument(
        "--notstrict",
        default=False,
        action="store_true",
        help="tell the parser to not be so strict about certain syntax errors."
    )

    args = parser.parse_args()
    if not os.path.exists(args.filepath):
        raise OSError("File at {0} does not exist.".format(args.filepath))

    card = Card(args.filepath, args.notstrict)
    data = card.data  # this will check for syntax errors

