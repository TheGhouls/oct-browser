import unittest
import lxml.html as lh
from octbrowser import __version__ as ob_version
from octbrowser.browser import Browser

import threading
import SocketServer
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
    httpd = SocketServer.TCPServer(("", PORT), SimpleHTTPRequestHandler)
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

    def test_navigation(self):
        """Testing history
        """
        self.browser.open_url('http://google.com')

        self.assertListEqual(self.browser.history, [None])

        resp = self.browser.open_url('http://google.com')

        self.assertEqual(200, resp.status_code)

        self.assertListEqual(self.browser.history, [None, 'http://google.com'])

        # main browser test
        self.assertEqual(self.browser._url, 'http://google.com')

        # back
        self.browser.back()

        # Same previous url
        self.assertEqual(self.browser._url, 'http://google.com')

        self.assertListEqual(self.browser.history, [None])

        self.browser.clean_session()

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

if __name__ == '__main__':
    httpd = start_http_server()
    try:
        unittest.main()
    finally:
        httpd.server_close()
