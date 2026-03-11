import time


def wait_for_element(page, selector):

    page.wait_for_selector(selector)

    return True


def take_screenshot(page, name="debug"):

    timestamp = int(time.time())

    path = f"screenshots/{name}_{timestamp}.png"

    page.screenshot(path=path)

    return path