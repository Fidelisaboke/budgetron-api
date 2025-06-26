"""Pagination utility module."""


def paginate_query(query, schema, page=1, limit=10):
    """Paginate a given query."""
    paginated = query.paginate(page=page, per_page=limit, error_out=False)
    return {
        'items': schema.dump(paginated.items),
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'has_next': paginated.has_next,
        'has_prev': paginated.has_prev,
    }
