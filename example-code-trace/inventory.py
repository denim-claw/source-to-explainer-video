"""Fictional inventory service. No network, credentials or application code."""


def reserve(units, *, authenticate, load_stock, save_stock, clock):
    authenticated = authenticate('demo-reader')
    if not authenticated or units <= 0:
        raise ValueError('invalid reservation')
    stock = load_stock('demo-item')
    if stock < units:
        raise ValueError('insufficient stock')
    remaining = stock - units
    saved_at = clock()
    save_stock('demo-item', remaining, saved_at)
    return {'remaining': remaining, 'saved_at': saved_at}
