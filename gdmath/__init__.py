import warnings

warnings.warn(
    (
        "GdMath: this package was renamed to \"Spatium\", "
        "the gdmath package is deprecated, "
        "please consider updating to Spatium. "
        "(https://pypi.org/project/spatium)"
    ),
    Warning
)
del warnings

from spatium import *
import spatium
__all__ = spatium.__all__
del spatium
