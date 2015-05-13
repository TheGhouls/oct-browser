"""This file contain the class for the basic history of the browser

All history management are present here
"""

from octbrowser.exceptions import EndOfHistory, NoPreviousPage, HistoryIsEmpty


class History(object):
    """Represent a basic browser history, it consist on a simple list and a property to keep the current
    element
    """

    def __init__(self):
        self.current = 0
        self.history = list()

    def append_item(self, item):
        """Add a new item to the history

        :param item: the item to add in the history list
        :type item: str
        :return: None
        """
        if self.current < (len(self.history) - 1):
            self.history = self.history[:self.current + 1]
        self.history.append(item)
        self.current = len(self.history) - 1

    def next(self):
        """Return the next element in comparision with the current element
        If the history doesn't have a next element, the method will raise an ``EndOfHistory`` exception

        :return: the next element
        :rtype: str
        :raises: EndOfHistory
        """
        try:
            item = self.history[self.current + 1]
            self.current += 1
        except IndexError:
            raise EndOfHistory()
        return item

    def previous(self):
        """Return the previous element in comparision with the current element
        If the history doesn't have a previous element, the method will raise an ``NoPreviousPage`` exception

        :return: the previous element
        :rtype: str
        :raises: NoPreviousPage
        """
        if self.current == 0:
            raise NoPreviousPage()
        try:
            item = self.history[self.current - 1]
            self.current -= 1
        except IndexError:
            raise NoPreviousPage()
        return item

    def get_current_item(self):
        """Simply return the current item

        :return: the current item
        :rtype: str
        """
        try:
            return self.history[self.current]
        except IndexError:
            raise HistoryIsEmpty()

    def clear_history(self):
        """Delete the current history and re initialise all values
        """
        del self.history
        self.history = list()
        self.current = 0
