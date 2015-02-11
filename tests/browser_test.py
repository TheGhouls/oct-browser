import unittest
import lxml.html as lh
from octbrowser.browser import Browser


class TestBrowserFunctions(unittest.TestCase):

    def setUp(self):
        self.browser = Browser()

        with open('html_test.html') as f:
            self.html = f.read()

    def test_form(self):
        """Test the form functions
        """
        self.browser._html = lh.fromstring(self.html)
        self.browser.get_form('.form')  # test with class selector

        # check input
        self.assertEqual(self.browser.form.inputs['test'].name, 'test')

        self.assertEqual(self.browser.form_data['test'], 'OK')

        self.browser.get_form('div#content > form')  # test with advanced selector
        self.assertEqual(self.browser.form_data['test'], 'OK')

        self.browser.get_form(None, nr=0)  # test with nr param
        self.assertEqual(self.browser.form_data['test'], 'OK')

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
        self.browser._html = lh.fromstring(self.html)

        # get the single p tag
        p = self.browser.get_html_element('#myparaf')

        self.assertEqual(p.rstrip(), '<p id="myparaf"></p>')

        # get all p tags with class `paraf`
        tags = self.browser.get_html_elements('.paraf')

        self.assertTrue(len(tags) == 4)

if __name__ == '__main__':
    unittest.main()
