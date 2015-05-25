import os
import unittest
from collections import deque
import threading
try:
    # Python 2
    import SocketServer as socketserver
except ImportError:
    # Python 3
    import socketserver
try:
    # Python 2
    from SimpleHTTPServer import SimpleHTTPRequestHandler
except ImportError:
    # Python 3
    from http.server import SimpleHTTPRequestHandler

import requests

from octbrowser import __version__ as ob_version
from octbrowser.browser import Browser
from octbrowser.history.cached import CachedHistory
from octbrowser.history.base import BaseHistory
from octbrowser.exceptions import EndOfHistory, NoPreviousPage, HistoryIsNone, HistoryIsEmpty, NoFormWaiting, FormNotFoundException, NoUrlOpen, LinkNotFound

PORT = 8081
BASE_URL = "http://localhost:{}".format(PORT)
httpd = None


def start_http_server():
    """
    Run SimpleHTTPServer to serve files in test directory
    """
    global httpd
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler)
    t = threading.Thread(target=httpd.serve_forever)
    t.setDaemon(True)
    t.start()


def stop_http_server():
    try:
        httpd.shutdown()
    except AttributeError:
        pass


def setUpModule():
    # Start http server in tests directory
    os.chdir(os.path.dirname(__file__))
    start_http_server()


def tearDownModule():
    # Shutdown http server
    stop_http_server()


class TestBrowserFunctions(unittest.TestCase):

    def setUp(self):
        self.browser = Browser(base_url=BASE_URL)

    def test_headers(self):
        """Test the browser header functions
        """
        # Browser.set_headers
        self.browser.set_headers({'foo': 'bar'})
        self.assertEqual(self.browser.session.headers, {'foo': 'bar'})

        # Browser.add_header
        self.browser.add_header('foo', 'baz')
        self.assertEqual(self.browser.session.headers, {'foo': 'baz'})

        # Contained in request
        r = self.browser.open_url(BASE_URL + '/html_test.html')
        self.assertEqual(r.request.headers, {'foo': 'baz'})

        # Browser.del_header
        self.browser.del_header('foo')
        self.assertEqual(self.browser.session.headers, {})
        # Check if fails for invalid header key
        self.assertIsNone(self.browser.del_header('nonsense'))

    def test_navigation(self):
        """Test the browser navigation
        """
        # Start Fresh
        self.browser.clean_browser()

        # Test NoUrl behavior
        self.assertIsNone(self.browser._url)
        self.assertRaises(NoUrlOpen, self.browser.refresh)
        self.assertRaises(NoUrlOpen, self.browser.follow_link, 'a')

        # Check browser history None behavior
        self.assertRaises(HistoryIsNone, self.browser.back)
        self.assertRaises(HistoryIsNone, self.browser.forward)
        self.assertRaises(HistoryIsNone, self.browser.clear_history)
        self.assertRaises(HistoryIsNone, lambda: self.browser.history)
        self.assertIsNone(self.browser.history_object)
        self.assertRaises(HistoryIsNone, self.browser.history_object)

        # Browser.open_url POST
        # Post is not supported by HTTPServer. Ensure that the POST request
        # was correctly constructed and submitted
        url = BASE_URL + '/html_test.html'
        resp0 = self.browser.open_url(url, data={'user name': 'octbrowser[]'})
        self.assertIsInstance(resp0, requests.Response)
        self.assertEqual(resp0.request.body, 'user+name=octbrowser%5B%5D')
        self.assertEqual(resp0.status_code, 501)

        # Browser.open_url GET
        url = BASE_URL + '/html_test.html'
        resp1 = self.browser.open_url(url, headers={'foo': 'bar'})
        self.assertIsInstance(resp1, requests.Response)
        html_test_text = open('html_test.html').read()
        self.assertEqual(html_test_text, resp1.text)
        self.assertIn('foo', resp1.request.headers)
        self.assertEqual('bar', resp1.request.headers['foo'])
        self.assertEqual(resp1.status_code, 200)

        # Browser.refresh
        # Modify the PreparedRequest header of the most recent request
        # Do a refresh and make sure that the updated response includes those
        # headers
        self.assertIsInstance(self.browser._response, requests.Response)
        resp1 = self.browser._response
        resp1_refresh = self.browser.refresh()
        self.assertEqual(resp1.url, resp1_refresh.url)
        self.assertEqual(resp1.headers, resp1_refresh.headers)
        self.assertEqual(resp1.content, resp1_refresh.content)
        self.assertEqual(resp1.request, resp1_refresh.request)
        self.assertNotEqual(resp1.raw.fileno, resp1_refresh.raw.fileno)

        # Browser.follow_link
        self.browser._base_url = BASE_URL
        # Non-existent link
        r = self.browser.open_url(BASE_URL + '/html_test.html')
        self.assertRaises(LinkNotFound, self.browser.follow_link, '#nonsense')

        # Good link
        self.browser.open_url(BASE_URL + '/html_test.html')
        r = self.browser.follow_link('#test_link')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.url, BASE_URL + '/basic_page.html')

        # Good link + regex
        r = self.browser.open_url(BASE_URL + '/html_test.html')
        r = self.browser.follow_link('#test_link', url_regex='.*\.html')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.url, BASE_URL + '/basic_page.html')

        # Good link + bad regex
        self.assertRaises(
            LinkNotFound,
            self.browser.follow_link,
            '#test_link',
            url_regex='.*\.php')

        # Browser.clean_session
        # Verify browser is not clean
        self.assertIsNotNone(self.browser._url)
        self.assertIsNotNone(self.browser._html)
        self.assertIsNotNone(self.browser._response)
        self.browser.add_header('special', 'value')
        if self.browser.history_object is not None:
            self.browser.history_object.history.append('something')
            self.assertGreater(len(self.browser.history_object.history), 0)
        # Do browser clean
        self.browser.clean_browser()
        # Verify results
        self.assertIsNone(self.browser._url)
        self.assertIsNone(self.browser._html)
        self.assertIsNone(self.browser._response)
        self.assertNotIn('special', self.browser.session.headers)
        if self.browser.history_object is not None:
            self.assertIsNone(self.browser.history)

        # Browser._process_html
        self.assertIsNone(self.browser._url)
        self.assertIsNone(self.browser._html)
        self.assertIsNone(self.browser._response)
        r = self.browser.session.get(BASE_URL + '/html_test.html')
        r_html = self.browser._process_response(r)
        self.assertEqual(r.url, self.browser._url)
        self.assertIsNotNone(self.browser._html)
        self.assertEqual(self.browser._response, r_html)

    def test_form(self):
        """Test the form functions
        """
        # Start Fresh
        self.browser.clean_browser()

        # Exercise "no url" behavior
        self.assertFalse(self.browser._form_waiting)
        self.assertRaises(NoUrlOpen, self.browser.get_form)
        self.assertRaises(NoFormWaiting, self.browser.submit_form)
        self.assertRaises(NoFormWaiting, self.browser.get_select_values)

        # Browser.get_form/._form_waiting
        self.browser.open_url(BASE_URL + "/html_test.html")
        self.assertRaises(FormNotFoundException, self.browser.get_form, '.zz')
        self.browser.get_form('.form')  # test with class selector
        self.assertTrue(self.browser._form_waiting)
        # check input
        self.assertEqual(self.browser.form.inputs['test'].name, 'test')
        self.assertEqual(self.browser.form_data['test'], 'OK')

        # test with advanced selector
        self.browser.get_form('div#content > form')
        self.assertEqual(self.browser.form_data['test'], 'OK')

        # test with nr param
        self.browser.get_form(None, nr=0)
        self.assertEqual(self.browser.form_data['test'], 'OK')

        # TODO Browser.get_select_values
        # self.assertEqual(self.browser.get_select_values(), {'test': 'OK'})

        # Browser.submit_form/_open_session_http
        # Check data and headers of submit_form
        user_agent = 'python-octbrowser/{}'.format(ob_version)
        self.browser.add_header('User-Agent', user_agent)
        self.browser.form_data['test'] = 'octbrowser'
        r = self.browser.submit_form()
        self.assertFalse(self.browser._form_waiting)

        # Verify user-agent and post data in response
        self.assertIn('User-Agent',  r.request.headers)
        self.assertEqual(r.request.headers['User-Agent'], user_agent)
        self.assertEqual(r.request.body, 'test=octbrowser')

    def test_get_elements(self):
        """Testing the get_html_elements method
        """
        # Start Fresh
        self.browser.clean_browser()

        # Exercise NoUrl behavior
        self.assertRaises(NoUrlOpen, self.browser.get_html_element, 'a')
        self.assertRaises(NoUrlOpen, self.browser.get_html_elements, 'a')

        # Open url
        self.browser.open_url(BASE_URL + "/html_test.html")

        # Browser.get_html_element
        self.assertEqual(self.browser.get_html_element('#nonsense'), '')
        # get the single p tag
        p = self.browser.get_html_element('#myparaf')
        self.assertEqual(p.rstrip(), '<p id="myparaf"></p>')

        # Browser.get_html_elements
        self.assertEqual(self.browser.get_html_elements('#nonsense'), [])

        # get all p tags with class `paraf`
        tags = self.browser.get_html_elements('.paraf')
        self.assertTrue(len(tags) == 4)

        # TODO Browser.get_resource

    def tearDown(self):
        self.browser.session.close()


class TestCachedHistoryFunctions(unittest.TestCase):

    def setUp(self):
        self.maxlen = 4
        self.browser = Browser(base_url=BASE_URL,
                               history=CachedHistory(maxlen=self.maxlen))

    def test_cached_history(self):
        """Testing the browser cached history
        """
        # Using CachedHistory
        msg = ('CachedHistory tests requires the browser to use a '
               'CachedHistory history object')
        self.assertIsInstance(self.browser.history_object, CachedHistory, msg)
        self.assertEqual(self.browser.history, deque())
        self.assertEqual(self.browser.history.maxlen, self.maxlen)

        # Browser.history/CachedHistory.append_item
        resp0 = self.browser.open_url(BASE_URL + '/html_test.html')
        self.assertTrue(len(self.browser.history) == 1)

        # Browser.history_object/CachedHistory.get_current_item
        self.assertEqual(resp0, self.browser.history_object.get_current_item())
        self.assertRaises(NoPreviousPage, self.browser.back)
        self.assertRaises(EndOfHistory, self.browser.forward)
        resp1 = self.browser.open_url(BASE_URL + '/basic_page.html')
        resp2 = self.browser.open_url(BASE_URL + '/basic_page2.html')
        self.assertEqual(deque([resp0, resp1, resp2]), self.browser.history)

        # Browser.back/CachedHistory.back
        resp1_hist = self.browser.back()
        self.assertEqual(self.browser._url, resp1.url)  # Same as previous url
        self.assertEqual(resp1_hist, resp1)  # Same response
        resp0_hist = self.browser.back()
        self.assertEqual(resp0_hist, resp0)

        # Browser.forward/CachedHistory.forward
        resp1_hist = self.browser.forward()
        self.assertEqual(resp1_hist, resp1)

        # CachedHistory.append_item - Forget the newer history on append
        resp3 = self.browser.open_url(BASE_URL)
        self.assertEqual(deque([resp0, resp1, resp3]), self.browser.history)

        # CachedHistory.current/.history out of sync
        self.browser.history_object.current = 99
        self.assertRaises(NoPreviousPage, self.browser.back)
        self.assertRaises(EndOfHistory, self.browser.forward)

        # CachedHistory after submit_form
        self.browser.open_url(BASE_URL + "/html_test.html")
        self.browser.get_form('.form')  # test with class selector
        r = self.browser.submit_form()
        self.assertEqual(self.browser.history_object.get_current_item(), r)

        # Browser.clear_history/CachedHistory.clear_history
        self.browser.clear_history()
        self.assertIsInstance(self.browser.history, deque)
        self.assertTrue(len(self.browser.history) == 0)

        # CachedHistory.history.maxlen
        for i in range(self.maxlen + 2):
            self.browser.open_url(BASE_URL + '/html_test.html')
        self.assertEqual(len(self.browser.history), self.maxlen)

    def tearDown(self):
        self.browser.session.close()


class TestBaseHistoryFunctions(unittest.TestCase):

    def setUp(self):
        self.browser = Browser(base_url=BASE_URL, history=BaseHistory())

    def test_base_history(self):
        """Testing the browser base history
        """
        # Using BaseHistory
        msg = ('BaseHistory tests requires the browser to use a '
               'BaseHistory history object')
        self.assertIsInstance(self.browser.history_object, BaseHistory, msg)
        self.assertEquals(self.browser.history, [])

        history = self.browser.history_object
        self.assertRaises(NotImplementedError, history.append_item, '')
        self.assertRaises(NotImplementedError, history.forward)
        self.assertRaises(NotImplementedError, history.back)
        self.assertRaises(HistoryIsEmpty, history.get_current_item)

        # BaseHistory.clear_history
        history.history.append('')
        history.current = 1
        self.assertEqual(len(history.history), 1)
        self.browser.clear_history()
        self.assertEqual(history.history, [])
        self.assertEqual(history.current, 0)

    def tearDown(self):
        self.browser.session.close()

if __name__ == '__main__':
    unittest.main()
