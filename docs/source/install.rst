.. _install:

============
Installation
============

.. tab-set::

    .. tab-item:: Docker

        The most painless way to get started quickly is to use the included
        Dockerfile based on jupyter/datascience-notebook with Python 3.12.
        
        To build the image and start a Jupyter Lab server:

        .. code-block:: bash

            git clone git://github.com/decompositional-semantics-initiative/decomp.git
            cd decomp
            docker build -t decomp .
            docker run -it -p 8888:8888 decomp
           
        This will start a Jupyter Lab server accessible at http://localhost:8888
        (with authentication disabled for convenience).
        
        To start a Python interactive prompt instead:
        
        .. code-block:: bash
        
            docker run -it decomp python

    .. tab-item:: pip

        Decomp can also be installed to a local environment using ``pip``.

        .. code-block:: bash

            pip install git+git://github.com/decompositional-semantics-initiative/decomp.git

    .. tab-item:: setup.py

        As an alternative to ``pip`` you can clone the decomp repository and use the included ``setup.py`` with the ``install`` flag.

        .. code-block:: bash

            git clone https://github.com/decompositional-semantics-initiative/decomp.git
            cd decomp
            pip install --user --no-cache-dir -r ./requirements.txt
            python setup.py install

    .. tab-item:: Development

        If you would like to install the package for the purposes of development, you can use the included ``setup.py`` with the ``develop`` flag.

        .. code-block:: bash

            git clone https://github.com/decompositional-semantics-initiative/decomp.git
            cd decomp
            pip install --user --no-cache-dir -r ./requirements.txt
            python setup.py develop


If you have trouble installing via setup.py or pip on OS X Mojave, adding the following environment variables may help.

.. code-block:: bash 

    CXXFLAGS=-stdlib=libc++ CFLAGS=-stdlib=libc++ python setup.py install