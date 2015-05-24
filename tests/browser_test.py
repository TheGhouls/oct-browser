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

from octbrowser import __version__ as ob_version
from octbrowser.browser import Browser
from octbrowser.history.cached import CachedHistory
from octbrowser.history.base import BaseHistory
from octbrowser.exceptions import EndOfHistory, NoPreviousPage, HistoryIsNone, HistoryIsEmpty

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
        pass
        # TODO Browser.add_header
        # TODO Browser.del_header
        # TODO Browser.set_headers

    def test_navigation(self):
        """Test the browser navigation
        """
        # Check browser history None
        self.assertRaises(HistoryIsNone, self.browser.back)
        self.assertRaises(HistoryIsNone, self.browser.forward)
        self.assertRaises(HistoryIsNone, self.browser.clear_history)
        self.assertRaises(HistoryIsNone, lambda: self.browser.history)
        self.assertIsNone(self.browser.history_object)
        self.assertRaises(HistoryIsNone, self.browser.history_object)

        # TODO Browser.clean_session
        # TODO Browser._parse_html
        # TODO Browser.open_url
        # TODO Browser.follow_link

    def test_form(self):
        """Test the form functions
        """
        # TODO Browser._form_waiting
        # TODO Browser.get_select_values
        # TODO Browser.get_form
        # TODO Browser.submit_form
        # TODO Browser._open_session_http
        self.browser.open_url(BASE_URL + "/html_test.html")
        self.browser.get_form('.form')  # test with class selector

        # check input
        self.assertEqual(self.browser.form.inputs['test'].name, 'test')

        self.assertEqual(self.browser.form_data['test'], 'OK')

        self.browser.get_form('div#content > form')  # test with advanced selector
        self.assertEqual(self.browser.form_data['test'], 'OK')

        self.browser.get_form(None, nr=0)  # test with nr param
        self.assertEqual(self.browser.form_data['test'], 'OK')

        # Check data and headers of submit_form
        user_agent = 'python-octbrowser/{}'.format(ob_version)
        self.browser.add_header('User-Agent', user_agent)
        self.browser.form_data['test'] = 'octbrowser'
        r = self.browser.submit_form()

        # Verify user-agent header
        self.assertTrue('User-Agent' in r.request.headers,
                        'User-Agent is in post headers')
        self.assertEqual(r.request.headers['User-Agent'], user_agent)

    def test_get_elements(self):
        """Testing the get_html_elements method
        """
        self.browser.open_url(BASE_URL + "/html_test.html")

        # Browser.get_html_element
        # get the single p tag
        p = self.browser.get_html_element('#myparaf')

        self.assertEqual(p.rstrip(), '<p id="myparaf"></p>')

        # Browser.get_html_elements
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
