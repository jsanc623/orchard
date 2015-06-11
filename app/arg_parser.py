"""
ArgParser
"""
import argparse
import sys


class ArgParser():
    """
    ArgParser
    Parse CLI arguments
    """
    parser = None
    available_options = { }
    required_options = ['--config']
    options = { }

    def __init__(self):
        """
        Constructor
        @param - self [python reference]
        Load resources
        """
        self.parser = argparse.ArgumentParser()

    def parse_options(self, error_exit=True, override_options=False):
        """
        parse_options
        @param - self [python reference]
        Set and parse options
        """
        for option in self.available_options:
            self.parser.add_argument(option, help=self.available_options[option])

        if override_options is not False:
            self.options = override_options
        else:
            self.options, _ = self.parser.parse_known_args()

        if not self.options.config:
            self.parser.print_help()
            if error_exit:
                sys.exit(1)

    def add_option(self, option, option_help):
        """
        add_option
        @param - self [python reference]
        @param - option [string]
        @param - option_help [string]
        Add an option
        """
        self.available_options[option] = option_help

    def remove_option(self, option):
        """
        remove_option
        @param - self [python reference]
        @param - option [string]
        Remove an option
        """
        if option in self.available_options and option not in self.required_options:
            del self.available_options[option]