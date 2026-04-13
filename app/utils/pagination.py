from typing import Tuple


def pagination_params(page: int = 1, page_size: int = 20) -> Tuple[int, int]:
    page = max(1, page)
    page_size = min(max(1, page_size), 200)
    skip = (page - 1) * page_size
    return skip, page_size
