"""Local title aliases for catalog providers that index English titles."""
import unicodedata


def normalize(value):
    value = ''.join(c for c in unicodedata.normalize('NFD', value) if not unicodedata.combining(c))
    return ' '.join(value.casefold().split())


TITLE_ALIASES = {
    'The Owl House': ('la casa buho', 'la casa del buho', 'casa buho'),
    'The Apothecary Diaries': ('los diarios de la boticaria', 'diarios de la boticaria', 'el diario de la boticaria', 'diario de una boticaria', 'boticaria', 'kusuriya no hitorigoto', 'kusuriya'),
}
LOCAL_TITLES = {35073: 'La casa búho', 67017: 'Los diarios de la boticaria'}


def resolve_title(query):
    normalized = normalize(query)
    for title, aliases in TITLE_ALIASES.items():
        if normalized == normalize(title) or normalized in aliases:
            return title
    # Resolve an unambiguous prefix while the user is still typing.
    if len(normalized) >= 5:
        matches = [title for title, aliases in TITLE_ALIASES.items()
                   if any(alias.startswith(normalized) for alias in aliases)]
        if len(matches) == 1:
            return matches[0]
    return query.strip()
