from abc import abstractmethod


class Component:
    """
    A Component is displayed in the user interface (in this case, Streamlit).
    """

    @abstractmethod
    def display(self) -> None:
        """
        Displays the component in Streamlit.
        """
        pass
