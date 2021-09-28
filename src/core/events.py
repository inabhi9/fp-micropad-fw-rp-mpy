import uasyncio as asyncio

handlers = {}


def _make_id(o):
    return id(o)


def on(event):
    def inner(func):
        events = event
        if not isinstance(event, list):
            events = [event]

        for e in events:
            event_name = _make_id(e)
            handlers[event_name] = handlers.get(event_name) or []
            handlers[event_name].append(func)

    return inner


class Event:
    async def send(self, **kwargs):
        handlers_ = handlers.get(_make_id(self))
        if handlers_:
            await asyncio.gather(*[handler(**kwargs) for handler in handlers_])


post_boot_auth_change = Event()
boot_auth_invalid = Event()
fp_auth = Event()
fp_auth_invalid = Event()
keypress = Event()
