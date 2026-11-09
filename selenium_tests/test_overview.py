# - Verify that the Overview page displays the Welcome heading and exactly two chart cards titled Sessions Outcome and Latest Sessions.
# - Confirm that Latest Sessions displays the Hour, Day, Month, and Year buttons and a labeled range slider.
# - Check that exactly one Total number of sessions summary displays a whole number greater than or equal to zero.
# - Refresh the page and verify that both charts reload and the session count remains valid, with no duplicate cards or summaries.

import re
from collections import Counter

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

MIN_SESSION_COUNT = 0  # Minimum sessions count should be displayed on the summary

EXPECTED_CHARTS = {
    "sessionsOutcomeChart": "Sessions Outcome",
    "sessionChart": "Latest Sessions",
}


# Helper function to return the text content of the html element
def visible_texts(parent, selector):
    elements = parent.find_elements(By.CSS_SELECTOR, selector)
    return [element.text.strip() for element in elements if element.is_displayed()]


# Checks the overall layout
def check_overview_layout(driver):
    wait = WebDriverWait(driver, 60)

    # Each chart should become visible after its wrapper finishes loading.
    for chart_id in EXPECTED_CHARTS:
        wait.until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    f'app-chart-wrapper[data-ready="true"] canvas#{chart_id}',
                )
            ),
            message=f"Chart '{chart_id}' did not finish loading.",
        )

    # Check the header of the overview page.
    assert visible_texts(driver, ".overviewHeader h1") == ["Welcome"]

    # Check the number of cards
    cards = driver.find_elements(By.CSS_SELECTOR, ".body .graph")
    assert len(cards) == len(EXPECTED_CHARTS)

    # Check which title belongs to each canvas.
    actual_charts = {}
    for card in cards:
        assert card.is_displayed()
        canvases = card.find_elements(By.TAG_NAME, "canvas")
        assert len(canvases) == 1  # Check if there is only 1 canvas per card

        # Create a dict of "id": "title" for all canvases
        chart_id = canvases[0].get_attribute("id")
        actual_charts[chart_id] = visible_texts(card, "h2.title")

    # Check if chart titles match
    assert actual_charts == {
        chart_id: [title] for chart_id, title in EXPECTED_CHARTS.items()
    }

    # Check the controls specifically inside the Latest Sessions card.
    latest_card = driver.find_element(By.ID, "latestSessionsDiv")
    assert Counter(visible_texts(latest_card, "button")) == Counter(
        ["Hour", "Day", "Month", "Year"]
    )

    # Check the Range slider beneath the latest sessions chart.
    range_labels = visible_texts(latest_card, ".slider-container label")
    assert len(range_labels) == 1
    assert range_labels[0].startswith("Range:")
    assert latest_card.find_element(
        By.CSS_SELECTOR, 'input[type="range"]'
    ).is_displayed()


# Check the total number of sessions.
def check_session_count(driver):
    def has_loaded_count(browser):
        ready_stats = browser.find_elements(
            By.CSS_SELECTOR, '.overviewHeader .stats[data-ready="true"]'
        )
        if not ready_stats:
            return False

        summaries = visible_texts(browser, ".overviewHeader .stats h3")
        # Check if there is only 1 summary: Total number of sessions
        if len(summaries) != 1:
            return False

        # Check if there is an actual number displayed after 'Total number of sessions:'
        match = re.fullmatch(r"Total number of sessions:\s*([0-9]+)", summaries[0])
        return match is not None and int(match.group(1)) >= MIN_SESSION_COUNT

    WebDriverWait(driver, 60).until(
        has_loaded_count,
        message="Expected one loaded, nonnegative session count.",
    )


# 3 main tests are defined below
def test_overview_cards_and_labels(admin_driver):
    check_overview_layout(admin_driver)


def test_session_count_is_nonnegative(admin_driver):
    check_session_count(admin_driver)


# This test make sure that the charts and total number of sessions don't get duplicated when refreshing the page
def test_refresh_displays_valid_count_without_duplicates(admin_driver):
    check_overview_layout(admin_driver)
    check_session_count(admin_driver)

    admin_driver.refresh()  # Tells Chrome to reload the current page

    check_overview_layout(admin_driver)
    check_session_count(admin_driver)
