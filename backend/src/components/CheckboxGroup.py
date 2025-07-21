import streamlit as st
from components.utils import NUM_COLUMNS


class CheckboxGroup:
    """
    A checkbox group is a group of checkbox objects
    laid out in four columns.
    """

    def __init__(self, options: set[str], title: str, help: dict[str, str] = None):
        """
        Initializes a set of options, all set to False.
        """
        if help is None:
            help = dict()
        self.selected: dict[str, bool] = dict()
        self.title = title
        self.help = help

        for option in options:
            self.selected[option] = False

    def display(self):
        if self.title:
            st.subheader(self.title)
        # Pass 1: Get all names of files

        cols = st.columns(NUM_COLUMNS)
        n = len(self.selected)
        listed_options = sorted(list(self.selected.keys()))

        for i in range(NUM_COLUMNS):
            with cols[i]:
                for name in listed_options[i:n:NUM_COLUMNS]:
                    help_string = self.help[name] if name in self.help else None
                    self.selected[name] = st.checkbox(name, key=f"{self.title}-{name}",
                                                      help=help_string)

    def get_value(self):
        """
        Returns all the selected options.
        """
        return [x for x in self.selected if self.selected[x]]
