def wait_for_element(page, selector):

    page.wait_for_selector(selector)

    return True


def take_screenshot(page, path="screenshot.png"):

    page.screenshot(path=path)

    return {"screenshot": path}