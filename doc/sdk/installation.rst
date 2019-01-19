Installation
============

Prerequisites
*************

* OpenDXL Python Client library installed
   `<https://github.com/opendxl/opendxl-client-python>`_

* The OpenDXL Python Client prerequisites must be satisfied
   `<https://opendxl.github.io/opendxl-client-python/pydoc/installation.html>`_

* Python 2.7.9 or higher installed within a Windows or Linux environment. (Python 3 is not supported at this time)

Installation
************

This distribution contains a ``lib`` sub-directory that includes the application library files.

Use ``pip`` to automatically install the library:

    .. parsed-literal::

        pip install vormetricservice-\ |version|\-py2-none-any.whl

Or with:

    .. parsed-literal::

        pip install vormetricservice-\ |version|\.zip

As an alternative (without PIP), unpack the vormetricservice-\ |version|\.zip (located in the lib folder) and run the setup
script:

    .. parsed-literal::

        python setup.py install
