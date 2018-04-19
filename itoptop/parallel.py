def tmap(fn, args, workers=1):
    """
    Multithread map, wait threads and return results in a list.
    :param fn: function
    :param args: list
    :param workers: número de threads máximo
    :return: list of results
    """
    if workers == 1:
        return list(map(fn, args))

    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(workers) as ex:
        res = ex.map(fn, args)
        ex.shutdown(wait=True)

    return list(res)