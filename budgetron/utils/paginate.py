"""Pagination utility module."""
from flask import request


def paginate_query(query, schema, page=None, limit=None):
    """Paginate a given query."""
    page = page or 1
    limit = limit or 10

    paginated = query.paginate(page=page, per_page=limit, error_out=False)

    base_url = request.base_url
    args = request.args.to_dict()
    args['limit'] = limit

    # Build API hyperlinks
    prev_url = build_url(args, page - 1, base_url) if paginated.has_prev else None
    next_url = build_url(args, page + 1, base_url) if paginated.has_next else None

    return {
        'total': paginated.total,
        'page': paginated.page,
        'per_page': limit,
        'pages': paginated.pages,
        'next': next_url,
        'prev': prev_url,
        'items': schema.dump(paginated.items),
    }


def build_url(request_args, new_page, base_url):
    """Build the URL used in API hyperlinks."""
    request_args['page'] = new_page
    query_string = '&'.join([f'{k}={v}' for k, v in request_args.items()])
    return f"{base_url}?{query_string}"
