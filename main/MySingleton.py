from __future__ import annotations
from __future__ import annotations
from threading import Lock, Thread
from typing import Optional


class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """

    _instance = None

    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__call__(*args, **kwargs)
        return cls._instance