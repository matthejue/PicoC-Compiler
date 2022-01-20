from dataclasses import dataclass


@dataclass(init=False, repr=False)
class Reference:
    val: Exception
