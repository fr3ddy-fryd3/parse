import pandas as pd
from functools import wraps


def dataframe(func):
    """Декоратор, возвращающий датафрейм вместо выходных данных функции"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        # Если функция вернула None, возвращаем пустой DataFrame
        if result is None:
            return pd.DataFrame()
        # Если результат уже DataFrame, возвращаем его без изменений
        if isinstance(result, pd.DataFrame):
            return result
        # Иначе пытаемся создать DataFrame из результата
        try:
            return pd.DataFrame(result)
        except Exception as e:
            raise ValueError(
                f"Не удалось преобразовать результат функции {func.__name__} в DataFrame: {e}"
            )

    return wrapper
