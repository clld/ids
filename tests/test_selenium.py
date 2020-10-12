import time
import pytest


@pytest.mark.selenium
def test_ui(selenium):
    selenium.browser.get(selenium.url('/download'))
    time.sleep(3)
