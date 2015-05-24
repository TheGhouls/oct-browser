import unittest
from octbrowser import __version__ as ob_version
from octbrowser.browser import Browser
from octbrowser.history.cached import CachedHistory
from octbrowser.exceptions import EndOfHistory, NoPreviousPage

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

PORT = 8081
BASE_URL = "http://localhost:{}".format(PORT)


def start_http_server():
    """
    Run SimpleHTTPServer to serve files in test directory
    """
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler)
    t = threading.Thread(target=httpd.serve_forever)
    t.setDaemon(True)
    t.start()
    return httpd


class TestBrowserFunctions(unittest.TestCase):

    def setUp(self):
        self.browser = Browser(base_url=BASE_URL)

    def test_form(self):
        """Test the form functions
        """
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

        # get the single p tag
        p = self.browser.get_html_element('#myparaf')

        self.assertEqual(p.rstrip(), '<p id="myparaf"></p>')

        # get all p tags with class `paraf`
        tags = self.browser.get_html_elements('.paraf')

        self.assertTrue(len(tags) == 4)

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
        resp0 = self.browser.open_url(BASE_URL + '/html_test.html')
        self.assertTrue(len(self.browser._history.history) == 1)
        self.assertEqual(resp0, self.browser._history.get_current_item())
        self.assertRaises(NoPreviousPage, self.browser.back)
        self.assertRaises(EndOfHistory, self.browser.forward)
        resp1 = self.browser.open_url(BASE_URL + '/basic_page.html')
        resp2 = self.browser.open_url(BASE_URL + '/basic_page2.html')
        self.assertEqual(deque([resp0, resp1, resp2]),
                         self.browser._history.history)

        # Back
        resp1_hist = self.browser.back()
        # Same as previous url
        self.assertEqual(self.browser._url, resp1.url)
        # Same response object
        self.assertEqual(resp1_hist, resp1)

        # Back again
        resp0_hist = self.browser.back()
        self.assertEqual(resp0_hist, resp0)

        # Forward
        resp1_hist = self.browser.forward()
        self.assertEqual(resp1_hist, resp1)

        # Forget some history
        resp3 = self.browser.open_url(BASE_URL)
        self.assertEqual(deque([resp0, resp1, resp3]),
                         self.browser._history.history)

        # Clear history
        self.browser.clear_history()
        self.assertTrue(isinstance(self.browser._history.history, deque))
        self.assertTrue(len(self.browser._history.history) == 0)

        # Check max history len
        for i in range(self.maxlen + 2):
            self.browser.open_url(BASE_URL + '/html_test.html')
        self.assertEqual(len(self.browser._history.history), self.maxlen)

    def tearDown(self):
        self.browser.session.close()

if __name__ == '__main__':
    httpd = start_http_server()
    try:
        unittest.main()
    finally:
        httpd.shutdown()
