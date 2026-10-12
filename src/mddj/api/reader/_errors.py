from .._errors import MDDJError


class MissingRequiredField(MDDJError, LookupError):
    pass


class NotALowerBound(MDDJError, ValueError):
    pass
