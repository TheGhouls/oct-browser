"""This file contain the class for the basic history of the browser

All history management are present here
"""

from octbrowser.exceptions import HistoryIsEmpty


class BaseHistory(object):
    """Represent a base browser historic
    """

    def __init__(self):
        self.current = 0
        self.history = []

    def append_item(self, item):
        """Add a new item to the history

        :param item: the item to add in the history list
        :type item: requests.Response
        :return: None
        """
        raise NotImplemented("Append item must be implemented")

    def forward(self):
        """Return the next element in comparision with the current element
        If the history doesn't have a next element, the method will raise an ``EndOfHistory`` exception

        :return: the next element
        :rtype: requests.Response
        :raises: EndOfHistory
        """
        raise NotImplemented("Forward method must be implemented")

    def back(self):
        """Return the previous element in comparision with the current element
        If the history doesn't have a previous element, the method must raise an ``NoPreviousPage`` exception

        :return: the previous element
        :rtype: requests.Response
        :raises: NoPreviousPage
        """
        raise NotImplemented("Back method must be implemented")

    def get_current_item(self):
        """Simply return the current item

        :return: the current item
        :rtype: requests.Response
        """
        try:
            return self.history[self.current]
        except IndexError:
            raise HistoryIsEmpty()

    def clear_history(self):
        """Delete the current history and re initialise all values
        """
        del self.history
        self.history = []
        self.current = 0
