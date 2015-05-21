

class OctGenericException(Exception):
    """
    Provide generic exception for reports

    """
    pass


class FormNotFoundException(Exception):
    """
    Raised in case of FormNotFound with browser

    """
    pass


class NoUrlOpen(Exception):
    """
    Raised in case of no url open but requested inside browser class

    """
    pass


class LinkNotFound(Exception):
    """
    Raised in case of link not found in current html document

    """
    pass


class NoFormWaiting(Exception):
    """
    Raised in case of action required form if no form selected

    """
    pass


class EndOfHistory(Exception):
    """Raised if the ``next`` method of an history is called but the actual page is the last element
    """
    pass


class NoPreviousPage(Exception):
    """Raised if the ``previous`` method of an history is called but the actual page is the first element
    """
    pass


class HistoryIsEmpty(Exception):
    """Raised if the ``get_current_item`` method of an history is called but the history is empty
    """
    pass


class HistoryIsNone(Exception):
    """Raised if the ``_history`` property of the browser is set to None and one method using it is called
    """
    pass
