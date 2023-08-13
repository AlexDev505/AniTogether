"""

Функции, которые используются в различных модулях приложения.

"""

import typing as ty


def pretty_view(data: dict | list, _indent=0) -> str:
    """
    Преобразует `data` в более удобный для восприятия вид.
    """

    def adapt_value(obj: ty.Any) -> ty.Any:
        if isinstance(obj, (int, float, bool, dict)) or obj is None:
            return obj
        elif obj.__repr__().startswith("{"):
            return obj.__dict__
        elif obj.__repr__().startswith("["):
            return list(obj)
        else:
            return str(obj)

    def tag(t: str, content: ty.Any) -> str:
        return f"<{t}>{content}</{t}>"

    def dict_(content: dict) -> list[str]:
        values = []
        for k, v in content.items():
            k = tag("le", f'"{k}"' if isinstance(k, str) else k)
            v = adapt_value(v)
            if isinstance(v, str):
                v = tag("y", '"%s"' % v.replace("\n", "\\n"))
            elif isinstance(v, (dict, list)):
                v = pretty_view(v, _indent=_indent + 1)
            else:
                v = tag("lc", v)
            values.append(f"{k}: {v}")
        return values

    def list_(content: list) -> list[str]:
        items = []
        for item in content:
            item = adapt_value(item)
            if isinstance(item, str):
                items.append(tag("y", f'"{item}"'))
            elif isinstance(item, (dict, list)):
                items.append(pretty_view(item, _indent=_indent + 1))
            else:
                items.append(tag("lc", item))
        return items

    result = ""

    if isinstance(data, dict):
        if len(data) > 2 or not all(
            isinstance(x, (str, int, float, bool)) or x is None for x in data.values()
        ):
            result = (
                "{\n"
                + "    " * (_indent + 1)
                + f",\n{'    ' * (_indent + 1)}".join(dict_(data))
                + "\n"
                + "    " * _indent
                + "}"
            )
        else:
            result = "{" + ", ".join(dict_(data)) + "}"

    elif isinstance(data, list):
        if len(data) > 15 or not all(
            isinstance(x, (str, int, float, bool)) for x in data
        ):
            result = (
                "[\n"
                + "    " * (_indent + 1)
                + f",\n{'    ' * (_indent + 1)}".join(list_(data))
                + "\n"
                + "    " * _indent
                + "]"
            )
        else:
            result = "[" + ", ".join(list_(data)) + "]"

    return tag("w", result)


def debug_title_data(title: dict) -> str:
    """
    Преобразует экземпляр релиза в читаемый формат для DEBUG записи.
    :param title: Экземпляр релиза.
    :return: Строка.
    """
    return pretty_view(
        dict(
            name=title["names"]["ru"],
            type=title["type"]["string"],
            episodes_count=title["type"]["episodes"] or len(title["player"]["list"]),
        )
    )


def trace_title_data(title: dict) -> str:
    """
    Преобразует экземпляр релиза в читаемый формат для TRACE записи.
    :param title: Экземпляр релиза.
    :return: Строка.
    """
    return pretty_view(title)
