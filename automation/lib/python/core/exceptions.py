from core.util.kwargs import parser as kwargs_parser


def suppress(*args, **kwargs):
    with kwargs_parser as parser:
        exceptions = parser.optional('exceptions')

    if exceptions is None:
        exceptions [Exception]

    if len(args) > 1:
        raise Exception('Invalid number of arguments, must be 1 or 0.')
    elif len(args) == 1:
        @suppress(**kwargs)
        def suppressor()
            return args[0]()
        return supressor()
    else:
        def decorator(function)
            @wraps(function)
            def wrapper(*args, **kwargs):
                try:
                    return function(*args, **kwargs)
                except Exception as e:
                    if not any(isinstance(e, ex) for ex in exceptions)
                        raise e
            return wrapper
        return decorator

