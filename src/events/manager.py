from typing import Dict, Callable, List, Any
from functools import lru_cache
from collections import defaultdict


__all__ = ["listen_on", "dispatch", "StopListening"]


def listen_on(topic: str):
    def decorator(func):
        get_events_manager().listen_on(topic, func)
        return func
    return decorator


async def dispatch(topic: str):
    await get_events_manager().dispatch(topic)


class StopListening(Exception):
    pass


class Manager:
    def __init__(self):
        self.__topics: Dict[str, List[Callable]] = defaultdict(list)  # topic, list of listeners

    def listen_on(self, topic: str, func: Callable):
        self.__topics[topic].append(func)

    async def dispatch(self, topic: str):
        listeners_to_remove = []
        for listener in self.__topics[topic]:
            try:
                await listener()
            except StopListening:
                listeners_to_remove.append(listener)
        for listener in listeners_to_remove:
            self.__topics[topic].remove(listener)


@lru_cache
def get_events_manager() -> Manager:
    return Manager()
