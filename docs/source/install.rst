.. _install:

============
Installation
============

.. warning::
   Currently there is an issue with installing from conda (see `#15
   <https://github.com/decompositional-semantics-initiative/decomp/issues/15/>`_).
   

The most painless way to get started quickly is to use the included
barebones Python 3.6-based Dockerfile. To build the image and start a
python interactive prompt, use:

.. code-block:: bash

  git clone git://gitlab.hltcoe.jhu.edu/aswhite/decomp.git
  cd decomp
  docker build -t decomp .
  docker run -it decomp python
   
A jupyter notebook can then be opened in the standard way.

Decomp can also be installed to a local environment using ``pip``.

.. code-block:: bash

   pip install git+git://github.com/decompositional-semantics-initiative/decomp.git


As an alternative to ``pip`` you can clone the decomp repository and use the included ``setup.py`` with the ``install`` flag.

.. code-block:: bash

   git clone https://github.com/decompositional-semantics-initiative/decomp.git
   cd decomp
   pip install --user --no-cache-dir -r ./requirements.txt
   python setup.py install


If you would like to install the package for the purposes of development, you can use the included ``setup.py`` with the ``develop`` flag.

.. code-block:: bash

   git clone https://github.com/decompositional-semantics-initiative/decomp.git
   cd decomp
   pip install --user --no-cache-dir -r ./requirements.txt
   python setup.py develop


If you have trouble installing via setup.py or pip on OS X Mojave, adding the following environment variables may help.

.. code-block:: bash 

    CXXFLAGS=-stdlib=libc++ CFLAGS=-stdlib=libc++ python setup.py install



