import logging

logger = logging.getLogger('hon.utils')

def find_first_element_by_tag(element, tag_name, skip=[]):
    logger.debug(f'Looking for first element in: {element} that matches the tag: {tag_name}')
    if element.tag == str(tag_name).lower():
        logger.debug(f'Successfully matched tag: {tag_name} to element: {element}')
        return element

    if len(element) > 0:
        for e in list(element):
            if skip and e.tag in skip:
                logger.debug(f'The tag {e.tag} was found in the list of tags not to be traversed. Skipping {e}')
                continue
            return find_first_element_by_tag(e, tag_name, skip=skip)
    return None


def find_elements_by_tag(element, tag_names=None, max_depth=0, current_depth=0):
    logger.debug(f'Looking for any elements matching: {tag_names} starting at: {element}')
    found = []

    #: If the element is empty, we can't match anything and therefore we should
    #: just return an empty array. [SWQ]
    if element is None or len(element) == 0:
        return []

    #: If None or * were passed into the ``tag_names`` argument, we're going to
    #: assume that the user wants all tags up to a certain depth. This is
    #: similar to how the iter(tag=...) function within ElementTree works. [SWQ]
    all_tags = False
    if tag_names is None or tag_names == '*':
        all_tags = True

    if all_tags or element.tag in tag_names:
        found.append(element)

    if current_depth < max_depth:
        if len(element) > 0:
            for e in list(element):
                if len(e) > 0:
                    found_subelements = find_elements_by_tag(e,
                        tag_names=tag_names, max_depth=max_depth,
                        current_depth=current_depth+1)
                    found.extend(found_subelements)
                elif all_tags or e.tag in tag_names:
                    found.append(e)
    return found
