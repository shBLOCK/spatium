import gc
import inspect
import itertools
from contextlib import contextmanager
# noinspection PyPep8Naming
from datetime import datetime as DateTime
from datetime import timezone
from types import FunctionType
from typing import Tuple, TypeVar, Type, Optional, Iterable, Generator

import colorama
from numerize.numerize import numerize

__all__ = (
    "SourceLines",
    "indent",
    "dedent",
    "extract_source",
    "compile_src",
    "validate_source",
    "extract_and_validate_source",
    "utc_now",
    "from_utc_stamp",
    "NoGC",
    "numerize",
    "_instance_from_id",
    "log",
    "indent_log",
    "temp_log",
    "iter_identity"
)

SourceLines = Tuple[str, ...]

def indent(src: SourceLines) -> SourceLines:
    return tuple(" "*4 + line for line in src)

def dedent(src: SourceLines) -> SourceLines:
    for i in itertools.count():
        if any(line[i:i+1] != " " for line in src):
            return tuple(line[i:] for line in src)

def extract_source(func: FunctionType) -> SourceLines:
    """
    Extract the source code of the body of func.
    Only support functions with a single-line header.
    """
    src = inspect.getsource(func).splitlines()
    src = list(dedent(src))
    if src[0][0] == "@": # delete decorator
        del src[0]
    del src[0] # delete function header
    return dedent(src)

def compile_src(src: SourceLines, name: str = "<BENCHMARK_SRC>"):
    return compile("\n".join(src), name, "exec", optimize=2)

def validate_source(src: SourceLines, name: str):
    try:
        exec(compile_src(src, name))
    except Exception as e:
        raise RuntimeError("Code validation failed.") from e

def extract_and_validate_source(func: FunctionType, name: str):
    src = extract_source(func)
    name += f"({func.__name__} in {func.__module__})"
    validate_source(src, name)
    return src

def utc_now() -> DateTime:
    return DateTime.now(timezone.utc)

def from_utc_stamp(stamp: float) -> DateTime:
    return DateTime.fromtimestamp(stamp, timezone.utc)

class _NoGC:
    def __init__(self):
        self._enter_depth = 0

    def __enter__(self):
        if self._enter_depth == 0:
            gc.disable()
        self._enter_depth += 1

    def __exit__(self, *_):
        self._enter_depth -= 1
        if self._enter_depth == 0:
            gc.enable()

NoGC = _NoGC()

T = TypeVar("T")
def _instance_from_id(cls: Type[T], identifier: str) -> Optional[T]:
    for inst in cls.instances:
        if inst.id == identifier:
            return inst
    return None

_log_indent = 0
@contextmanager
def indent_log(n=1):
    global _log_indent
    _log_indent += n
    yield
    _log_indent -= n
    assert _log_indent >= 0

_log_chrs_stack = []
@contextmanager
def temp_log(disable=False):
    if disable:
        yield
        return

    global _should_indent
    old_should_indent = _should_indent
    _log_chrs_stack.append(0)
    yield
    # print("\\b"+str(_log_chrs_stack[-1]))
    # print(colorama.ansi.clear_line(1), end="")
    # print(colorama.ansi.Cursor.UP())
    # print("\r", end="", flush=True)
    print("\r\033[K", end="", flush=True)
    # print("\b" * _log_chrs_stack.pop(-1), end="")
    _should_indent = old_should_indent

_should_indent = True
def log(msg="", new_line=True, color: str = None):
    global _should_indent
    msg = str(msg)
    if _should_indent:
        msg = "    " * _log_indent + msg
    if color is not None:
        msg = getattr(colorama.Fore, color.upper()) + msg + colorama.Back.RESET
    if new_line:
        msg += "\n"
    print(msg, end="", flush=True)
    if _log_chrs_stack:
        _log_chrs_stack[-1] += len(msg)

    _should_indent = new_line

def iter_identity(it: Iterable[T]) -> Generator[T, None, None]:
    got = set()
    for item in it:
        if item not in got:
            yield item
            got.add(item)
