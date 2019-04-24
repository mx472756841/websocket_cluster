# -*- coding: utf-8 -*-
import logging
import uuid

logger = logging.getLogger(__file__)


def recursive_int(obj):
    """
    """
    if isinstance(obj, dict):
        return dict((recursive_int(k), recursive_int(v)) for (k, v) in obj.items())
    elif isinstance(obj, list):
        return list(recursive_int(i) for i in obj)
    elif isinstance(obj, tuple):
        return tuple(recursive_int(i) for i in obj)
    elif isinstance(obj, set):
        return set(recursive_int(i) for i in obj)
    elif isinstance(obj, (bytes, str, float)):
        return int(obj)
    else:
        return obj


def get_uuid():
    return str(uuid.uuid1())

