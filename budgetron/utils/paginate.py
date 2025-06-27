"""Pagination utility module."""


def paginate_query(query, schema, page=None, limit=None):
    """Paginate a given query."""
    page = page or 1
    limit = limit or 10

    paginated = query.paginate(page=page, per_page=limit, error_out=False)
    return {
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'has_next': paginated.has_next,
        'has_prev': paginated.has_prev,
        'items': schema.dump(paginated.items),
    }
