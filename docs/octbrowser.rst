Browser
=======

Basic usages
------------

The browser is a part of oct.core module, and is instantiate by the `GenericTransaction` class in its `__init__` method.
The browser can be used as a stand-alone, and for advanced scripts it's good to know how to use it. So how to use it ?
First, you need to instantiate a new Browser object:

.. code-block:: python

    from oct.core.browser import Browser

    br = Browser()

The `Browser` object takes two optional parameters :

    * `sessions` if you want to use custom session manager, default value : `requests.Session()`
    * `base_url` for setting up your links when parsing, default to empty string

Now you can use the browser to access urls :

.. code-block:: python

    response = br.open_url('http://localhost/index.html')
    print(response.status_code)
    response = br.open_url('http://localhost/other_page.html')
    print(response.status_code)

This script opens two urls, and for each one display the `status_code` of the response object returned by the `open_url` method.

Since the return value is simply the return of the `requests.get` or of the `requests.post` method, you can access all properties of
a basic `requests.Response` object. But we add one thing to it, an `html` property, containing an
`lxml.html` object, representing the opened page.

The html property can be used for parsing or getting elements with the `lxml` syntax, since it's a standard object from `lxml.html` parsing.

For example you can access all forms object by using :

.. code-block:: python

    response.html.forms

Or even use the xpath syntax

And can you check the render of the page ? Of course, you don't need other imports, we've implemented an `open_in_browser` static method, calling the `lxml.html.open_in_browser` method. You can use it like this :

.. code-block:: python

    response = br.open_url('http://localhost/index.html')
    br.open_in_browser(response)

This will open the page in your default system browser.

A last thing you need to know. Each time the `.html` property is filled, the browser make a call to the
`make_links_absolute` method of `lxml`. If you want to avoid that, simply do not provide a `base_url` for your browser instance, it's used only for this call

Form manipulation
-----------------

Like we said in the previous part of this documentation, you can use all the `lxml` methods for parsing your page. But again, we
have done a part of the job for you.

Let's say that we have a simple html page like this at the index of your localhost favorite web server:

.. code-block:: html

    <!DOCTYPE html>
    <html>

    <head>
        <title> My test page </title>
    </head>

    <body>
        <div id="my_form_block">
            <form action="/action.py" method="post">
                <input type="text" name="firstname" />
            </form>
        </div>
    </body>

    </html>

A very simple page, but it's just for the example.

Now let's say that we want to get this form and submit it from the browser object :

.. code-block:: python

    from oct.core.browser import Browser

    # instantiate the browser
    br = Browser(base_url='http://localhost')

    # open the url
    br.open_url('http://localhost')

    # now we getting the form, using css selector
    br.get_form(selector='div#my_form_block > form')

    # we now have two properties for handling the form
    # br.form, containing the lxml for object
    # br.form_data, a dict containing all fields and values
    # let's just set the value and submit it
    br.form_data['firstname'] = 'my name'

    # and submit it
    response = br.submit_form()

    # and check the status code
    print(response.status_code)

And yes, that's it ! Simple, no ?
Thanks to the awesome cssselector python library, getting your forms are now simpler (unless you know nothing about css selectors)
but even if we don't want or can not use it, we can still use the `get_form` method, and use the `nr` parameter.
The `nr` param simply represent the position of the form in our page. Here, simple we only have one form, so let's update our script :

.. code-block:: python

    from oct.core.browser import Browser

    # instantiate the browser
    br = Browser(base_url='http://localhost')

    # open the url
    br.open_url('http://localhost')

    # now we getting the form, using css selector
    br.get_form(nr=0)

    # we now have two properties for handling the form
    # br.form, containing the lxml for object
    # br.form_data, a dict containing all fields and values
    # let's just set the value and submit it
    br.form_data['firstname'] = 'my name'

    # and submit it
    response = br.submit_form()

    # and check the status code
    print(response.status_code)

And here it is, same result !

For more information about form manipulation, please see the `lxml`_ documentation

.. _lxml: http://lxml.de/lxmlhtml.html

More navigation
---------------

You can follow links inside the html page like this :

.. code-block:: python

    from oct.core.browser import Browser

    # instantiate the browser
    br = Browser(base_url='http://localhost')

    # open the url
    br.open_url('http://localhost')

    # now we can follow any link using css selector or a regex
    # the regex will look at the text or the href attribute of the link
    response = br.follow_link('a.my_links', '.*this link.*')

    # oooops wrong link ! (yeah i know, that's doesn't append in script by try to imagine)
    # let's go back
    response = br.back() # after this we will be again at the index page
    # wait no ! go forward ! it was good
    response = br.next() # and here we go
    # go back again !
    response = br.back()
    # access another page now
    response = br.open_url('index')
    # going forward ?
    br.next() # This will raise an EndOfHistory Exception


And that's it ! The `follow_link` method is pretty simple actually, it just finds a link by regex and / or css selector,
and then opens the url contained in the `href` attribute of this link.

What about the navigation history ?
Well at this point the navigation history is managed by an object, who keep traces of all visited url. The history object
tries to fit the beaviour of a standard browser and gave you those methods :

* ``back`` for going back in the history
* ``next`` for going the the next element
* ``clear_history`` for removing all urls of the history

.. note:: If you use the ``back`` method, and then open an other url, the ``next`` method won't be avaible anymore, since
once you open an url, there a no next address yet.

Those methods allow you to navigate more easily with the octbrowser.
But if you want to use all the methods / properties of the History object, you can use the ``history_object`` property
of the browser to retreive it.
See the history documentation below to see all methods avaibles for the history object

Module details
--------------

octbrowser.browser module
-------------------------

.. automodule:: octbrowser.browser
    :members:
    :undoc-members:
    :show-inheritance:

octbrowser.exceptions module
----------------------------

.. automodule:: octbrowser.exceptions
    :members:
    :undoc-members:
    :show-inheritance:


octbrowser.history module
-------------------------

.. automodule:: octbrowser.history
    :members:
    :undoc-members:
    :show-inheritance:
