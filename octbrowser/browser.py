"""This file contain the main class for the octbrowser

It represent a simple browser object with all methods
"""

import requests
import re
import os
import lxml.html as lh
from lxml.cssselect import CSSSelector
from octbrowser.exceptions import FormNotFoundException, NoUrlOpen, LinkNotFound, NoFormWaiting, HistoryIsNone
from octbrowser.history.base import BaseHistory


class Browser(object):

    """This class represent a minimal browser. Build on top of lxml awesome library it let you write script for accessing
    or testing website with python scripts

    :param session: The session object to use. If set to None will use requests.Session
    :param base_url: The base url for the website, will append it for every link without a full url
    :param history: The history object to use. If set to None no history will be stored.
    :type history: octbrowser.history.base.BaseHistory instance
    """

    def __init__(self, session=None, base_url='', history=None):
        self._sess_bak = session
        if history is not None:
            assert isinstance(history, BaseHistory)
        self._history = history
        self._response = None
        self._base_url = base_url
        self.form = None
        self.form_data = None
        self.session = session or requests.Session()

    def clean_browser(self):
        """Clears browser history, session, current page, and form state

        self._base_url is unmodified
        :return: None
        """
        self.clean_session()
        self._response = None
        self.form = None
        self.form_data = None
        try:
            self.clear_history()
        except HistoryIsNone:
            pass

    def add_header(self, name, value):
        """Allow you to add custom header, one by one.
        Specify existing name for update
        Headers will be used by every request

        :param name: the key of the header
        :type name: str
        :param value: the associated value
        :type value: str
        :return: None
        """
        self.session.headers[name] = value

    def del_header(self, key):
        """Try to delete the 'key' of headers property

        :param key: the key to delete
        :type key: mixed
        :return: None
        """
        self.session.headers.pop(key, None)

    def set_headers(self, headers):
        """Setter for headers property

        :param headers: a dict containing all headers
        :type headers: dict
        :return: None
        """
        self.session.headers.clear()
        self.session.headers.update(headers)

    def clean_session(self):
        """This function is called by the core of multi-mechanize. It cleans the session for avoiding cache or cookies
        errors, or giving false results based on cache

        :return: None
        """
        del self.session
        self.session = self._sess_bak or requests.Session()

    @property
    def _url(self):
        """Url of the current page or None if there isn't one

        :return: url of current page or None if there isn't one
        """
        try:
            return self._response.url
        except AttributeError:
            return None

    @property
    def _html(self):
        """Parsed html of the current page or None if there isn't any

        :return: html of current page or None if there isn't any
        """
        try:
            return self._response.html
        except AttributeError:
            return None

    @property
    def _form_waiting(self):
        """Check if a form is actually on hold or not

        :return: True or False
        """
        if self.form is not None:
            return True
        return False

    def _process_response(self, response):
        """Update the response object with parsed html and browser properties

        Html property is a lxml.Html object, needed for parsing the content, getting elements like form, etc...
        If you want the raw html, you can use both::

            response.read() # or .content for urllib response objects

        Or use lxml::

            lxml.html.tostring(response.html)

        :param response: requests.Response or urllib.Response object
        :return: the updated Response object
        """
        if not hasattr(response, 'html'):
            try:
                html = response.content
            except AttributeError:
                html = response.read()
                response.content = html
            tree = lh.fromstring(html)
            tree.make_links_absolute(base_url=self._base_url)
            response.html = tree
        self._response = response
        return response

    def get_form(self, selector=None, nr=0, at_base=False):
        """Get the form selected by the selector and / or the nr param

        Raise:
            * oct.core.exceptions.FormNotFoundException
            * oct.core.exceptions.NoUrlOpen

        :param selector: A css-like selector for finding the form
        :param nr: the index of the form, if selector is set to None, it will search on the hole page
        :param at_base: must be set to true in case of form action is on the base_url page
        :return: None
        """
        if self._html is None:
            raise NoUrlOpen('No url open')

        if selector is None:
            self.form = self._html.forms[nr]
            self.form_data = dict(self._html.forms[nr].fields)
        else:
            sel = CSSSelector(selector)
            for el in sel(self._html):
                if el.forms:
                    self.form = el.forms[nr]
                    self.form_data = dict(el.forms[nr].fields)

        if self.form is None:
            raise FormNotFoundException('Form not found with selector {0} and nr {1}'.format(selector, nr))

        # common case where action was empty before make_link_absolute call
        if (self.form.action == self._base_url and
                self._url is not self._base_url and
                not at_base):
            self.form.action = self._url

    def get_select_values(self):
        """Get the available values of all select and select multiple fields in form

        :return: a dict containing all values for each fields
        :raises: NoFormWaiting
        """
        if not self._form_waiting:
            raise NoFormWaiting('No form waiting')
        data = {}
        for i in self.form.inputs:
            if isinstance(i, lh.SelectElement):
                data[i.name] = i.value_options
        return data

    def submit_form(self):
        """Submit the form filled with form_data property dict

        Raise:
            oct.core.exceptions.NoFormWaiting

        :return: Response object after the submit
        """
        if not self._form_waiting:
            raise NoFormWaiting('No form waiting to be send')

        self.form.fields = self.form_data
        r = lh.submit_form(self.form, open_http=self._open_session_http)
        resp = self._process_response(r)
        if self._history is not None:
            self._history.append_item(resp)
        self.form_data = None
        self.form = None
        return resp

    def _open_session_http(self, method, url, values):
        """Custom method for form submission, send to lxml submit form method

        :param method: the method of the form (POST, GET, PUT, DELETE)
        :param url: the url of the action of the form
        :param values: the values of the form
        :return: Response object from requests.request method
        """
        return self.session.request(method, url, None, values)

    def open_url(self, url, data=None, **kwargs):
        """Open the given url

        :param url: The url to access
        :param data: Data to send. If data is set, the browser will make a POST request
        :return: The Response object from requests call
        """
        if data:
            response = self.session.post(url, data, **kwargs)
        else:
            response = self.session.get(url, **kwargs)
        response = self._process_response(response)
        if self._history is not None:
            self._history.append_item(response)
        response.connection.close()
        return response

    def back(self):
        """Go to the previous url in the history

        :return: the Response object
        :rtype: requests.Response
        :raises: NoPreviousPage, HistoryIsNone
        """
        if self._history is None:
            raise HistoryIsNone("You must set history if you need to use historic methods")
        response = self._history.back()
        return self._process_response(response)

    def forward(self):
        """Go to the next url in the history

        :return: the Response object
        :rtype: requests.Response
        :raises: EndOfHistory, HistoryIsNone
        """
        if self._history is None:
            raise HistoryIsNone("You must set history if you need to use historic methods")
        response = self._history.forward()
        return self._process_response(response)

    def refresh(self):
        """Refresh the current page by resending the request

        :return: the Response object
        :rtype: requests.Response
        :raises: NoUrlOpen
        """
        if self._response is None:
            raise NoUrlOpen("Can't perform refresh. No url open")
        response = self.session.send(self._response.request)
        return self._process_response(response)

    def clear_history(self):
        """Re initialise the history
        """
        if self._history is None:
            raise HistoryIsNone("You must set history if you need to use historic methods")
        self._history.clear_history()

    @property
    def history(self):
        """Return the actual history list

        :return: the history list
        :rtype: list
        :raises: HistoryIsNone
        """
        if self._history is None:
            raise HistoryIsNone("You must set history if you need to use historic methods")
        return self._history.history

    @property
    def history_object(self):
        """Return the actual history object

        :return: the _history property
        :rtype: History
        """
        return self._history

    def follow_link(self, selector, url_regex=None):
        """Will access the first link found with the selector

        Raise:
            oct.core.exceptions.LinkNotFound

        :param selector: a string representing a css selector
        :param url_regex: regex for finding the url, can represent the href attribute or the link content
        :return: Response object
        """
        sel = CSSSelector(selector)
        resp = None

        if self._html is None:
            raise NoUrlOpen

        for e in sel(self._html):
            if url_regex:
                r = re.compile(url_regex)
                if r.match(e.get('href')) or r.match(e.xpath('string()')):
                    return self.open_url(e.get('href'))
            else:
                return self.open_url(e.get('href'))

        if resp is None:
            raise LinkNotFound('Link not found')

    def get_html_element(self, selector):
        """Return a html element as string. The element will be find using the `selector` param

        Use this method for get single html elements, if you want to get a list of elements,
        please use `get_html_elements`

        :param selector: a string representing a css selector
        :type selector: str
        :return: a string containing the element, if multiples elements are find, it will concat them
        :rtype: str
        """
        if self._html is None:
            raise NoUrlOpen()
        elements = self._html.cssselect(selector)
        ret = ""
        for elem in elements:
            ret += lh.tostring(elem, encoding='unicode', pretty_print=True)
        return ret

    def get_html_elements(self, selector):
        """Return a list of lxml.html.HtmlElement matching the `selector` argument

        :param selector: a string representing a css selector
        :type selector: str
        :return: a list of lxml.html.HtmlElement of finded elements
        :rtype: list
        """
        if self._html is None:
            raise NoUrlOpen()
        return self._html.cssselect(selector)

    def get_ressource(self, selector, output_dir, source_attribute='src'):
        """Get a specified ressource and write it to the output dir

        Raise:
            OSError

        :param selector: a string representing a css selector
        :type selector: str
        :param output_dir: the directory where the ressources will be wright
        :type output_dir: str
        :param source_attribute: the attribute to retreive the url needed for downloading the ressource
        :type source_attribute: str
        :return: True if ressources as been correctly downled, False in other case
        """
        if self._html is None:
            raise NoUrlOpen()
        elements = self._html.cssselect(selector)

        if not elements or len(elements) == 0:
            return False

        for elem in elements:
            src = elem.get(source_attribute)
            if not src:
                continue
            response = requests.get(src, stream=True)

            if not response.ok:
                continue

            filename = re.search('((.*)\.[a-zA-Z]+)', response.url).group(0)
            path = os.path.join(output_dir, filename)
            with open(path, 'wb') as f:
                for block in response.iter_content(1024):

                    if not block:
                        break

                    f.write(block)

        return True

    @staticmethod
    def open_in_browser(response):
        """Provide a simple interface for `lxml.html.open_in_browser` function.
        Be careful, use this function only for debug purpose

        :param response:
        :return:
        """
        lh.open_in_browser(response.html)
