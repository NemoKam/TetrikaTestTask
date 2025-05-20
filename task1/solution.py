def strict(func):
    def wrapper(*args, **kwargs):
        func_annot = func.__annotations__
        # Проверка обычных аргументов.
        # Типы данных аргументов приходят в том же порядке, что и аргументы
        for arg, expected_type in zip(args, func_annot.values()):
            if not isinstance(arg, expected_type):
                raise TypeError(f"Expected {expected_type}, got {type(arg)}")
        # Проверка keyword аргументов
        for keyword, value in kwargs.items():
            if keyword in func_annot and not isinstance(value, func_annot[keyword]):
                raise TypeError(f"Expected {func_annot[keyword]}, got {type(value)}")
        
        return func(*args, **kwargs)
    return wrapper
