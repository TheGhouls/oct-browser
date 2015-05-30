"""This file contain the class for the cached history of the browser

All history management are present here
"""

import requests
from octbrowser.exceptions import EndOfHistory, NoPreviousPage
from octbrowser.history.base import BaseHistory
from collections import deque


class CachedHistory(BaseHistory):

    """A browser hisory that caches the history items
    """

    def __init__(self, maxlen=None):
        """Initialize CachedHistory object

        :param maxlen: the max len of history items to cache
        :type maxlen: int or None
        :return: None
        """
        self.current = 0
        self.history = deque(maxlen=maxlen)
        self._maxlen = maxlen

    def append_item(self, item):
        """Add a new item to the history

        :param item: the item to add in the history list
        :type item: requests.Response
        :return: None
        """
        assert isinstance(item, requests.Response)
        # Remove all items in front of the current item
        if self.current < (len(self.history) - 1):
            for i in range(len(self.history) - 1 - self.current):
                self.history.pop()  # deque doesn't support slicing
        # Append the new item
        self.history.append(item)
        self.current = len(self.history) - 1

    def forward(self):
        """Return the next element in comparision with the current element
        If the history doesn't have a next element, the method will raise an ``EndOfHistory`` exception

        :return: the next element
        :rtype: requests.Response
        :raises: EndOfHistory
        """
        try:
            item = self.history[self.current + 1]
            self.current += 1
        except IndexError:
            raise EndOfHistory()
        return item

    def back(self):
        """Return the previous element in comparision with the current element
        If the history doesn't have a previous element, the method must raise an ``NoPreviousPage`` exception

        :return: the previous element
        :rtype: requests.Response
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

    def clear_history(self):
        """Delete the current history and re initialise all values
        """
        del self.history
        self.history = deque(maxlen=self._maxlen)
        self.current = 0
