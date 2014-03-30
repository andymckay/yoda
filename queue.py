queue = set()


def add(name):
    if name:
        queue.add(name)


def remove(name):
    queue.discard(name)


def listing():
    return list(queue)


def reset():
    queue.clear()
