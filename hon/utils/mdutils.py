
def flatten_tree(elements):
    flat_tree = []
    for e in elements:
        flat_tree.append(e)
        if len(e) > 0:
            flat_tree.extend(flatten_tree(e))
    return flat_tree
