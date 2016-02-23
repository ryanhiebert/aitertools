import functools


async def aiter(aiterable):
    """The async version of the builtin ``iter``."""
    return await aiterable.__aiter__()


_sentinel = object()
async def anext(aiterable, default=_sentinel):
    """The async version of the builtin ``next``."""
    try:
        return await aiterable.__anext__()
    except StopAsyncIteration:
        if default is _sentinel:
            raise
        return default


def coroutine_iterator(afunc):
    class _CoroutineIteratorType(type):
        def __repr__(cls):
            return "<class '{module}.{name}'>".format(
                module=cls.__module__, name=cls.__name__)

    class CoroutineIterator(metaclass=_CoroutineIteratorType):
        def __init__(self, *args, **kwargs):
            self.__args = args
            self.__kwargs = kwargs
            self.__anext = _sentinel

        async def __aiter__(self):
            return self

        async def __anext__(self):
            if self.__anext is _sentinel:
                self.__anext = await afunc(*self.__args, **self.__kwargs)
                del self.__args, self.__kwargs
            return await self.__anext()

    CoroutineIterator.__name__ = afunc.__name__
    CoroutineIterator.__module__ = afunc.__module__
    return CoroutineIterator


@coroutine_iterator
async def to_aiter(iterable):
    iterator = iter(iterable)
    async def __anext__():
        try:
            return next(iterator)
        except StopIteration as e:
            raise StopAsyncIteration() from e
    return __anext__


def to_async(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
