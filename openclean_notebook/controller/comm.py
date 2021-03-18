# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (c) 2018-2021 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Helper functions to register callbacks for web socket messages."""

from typing import Callable

import logging


def register_handler(message: str, callback: Callable):
    """Register a given callable to handle incomming requests for the given
    message name.

    Parameters
    ----------
    message: string
        Unique message name (identifier).
    callback: callable
        Handler that is called on incomming messages. The message data will be
        passed to the handler as the only argument.
    """
    try:
        register_jupyter_handler(message=message, callback=callback)
    except NameError:
        logging.warning('Not in a notebook environment')


def register_jupyter_handler(message: str, callback: Callable):
    """Register a given callable to handle incomming requests for the given
    message name in a Jupyter Notebook environment. This function raises a
    NameError if called outside of a Jupyter Notebook environment.

    Parameters
    ----------
    message: string
        Unique message name (identifier).
    callback: callable
        Handler that is called on incomming messages. The message data will be
        passed to the handler as the only argument.

    Raises
    ------
    NameError
    """
    # Create handler that calls the given callback function on incomming
    # requests.
    def _msg_handler(comm, open_msg):  # pragma: no cover
        @comm.on_msg
        def _recv(msg):
            # Call the given callback handler with the message data and send
            # the returned response.
            resp = callback(msg['content']['data'])
            comm.send(resp)
    # Attempt to register the Web Socket message handler. THis will raise
    # a NameError if called outside of a Jupyter Notebook environment.
    comm_manager = get_ipython().kernel.comm_manager  # noqa: F821
    comm_manager.register_target(message, _msg_handler)  # pragma: no cover
