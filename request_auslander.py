from selenium import webdriver
from selenium.webdriver.common.by import By
from parsel.selector import Selector
import logging
import time

from alert import send_mail

logging.basicConfig(
    filename="auslander-spider.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    filemode="a",
)

DELAY_TIME = 7
ERROR_MSG = "Für die gewählte Dienstleistung sind aktuell keine Termine frei! Bitte \nversuchen Sie es zu einem späteren Zeitpunkt erneut."
START_TIME = time.time()


def init_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"
    )
    options.add_argument("--lang=es")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--remote-debugging-port=9222")
    return webdriver.Chrome(options=options)


def fill_form(driver):
    driver.get(
        "https://otv.verwalt-berlin.de/ams/TerminBuchen/wizardng?sprachauswahl=en"
    )
    time.sleep(DELAY_TIME * 2)

    clic_by_class(driver, 'class="XItem XCheckbox left-right"')

    clic_by_class(driver, 'class="ui-button-text ui-c"')
    time.sleep(DELAY_TIME * 2)
    clic_by_class(driver, 'name="sel_staat"')
    clic_by_class(driver, 'value="323"', "option")
    time.sleep(DELAY_TIME)
    clic_by_class(driver, 'name="personenAnzahl_normal"', "select")
    clic_by_class(driver, 'value="1"', "option")
    time.sleep(DELAY_TIME)
    clic_by_class(driver, 'name="lebnBrMitFmly"', "select")
    clic_by_class(driver, 'id="xi-sel-427_2"', "option")
    time.sleep(DELAY_TIME)
    clic_by_class(driver, 'for="SERVICEWAHL_DE3323-0-2"', "label")

    time.sleep(DELAY_TIME)
    clic_by_class(driver, 'for="SERVICEWAHL_DE_323-0-2-1"', "label")
    time.sleep(DELAY_TIME)
    clic_by_class(driver, 'for="SERVICEWAHL_DE323-0-2-1-329328"', "label")
    time.sleep(DELAY_TIME * 2)
    clic_by_class(driver, 'id="applicationForm:managedForm:proceed"', "button")
    time.sleep(DELAY_TIME * 2)


def clic_by_class(driver, class_str, tag="*"):
    element = driver.find_element(By.XPATH, f"//{tag}[@{class_str}]")
    element.click()


def send_alive_signal(url_form):
    logging.info(
        f"Still working searching for appointments...\n\tCurrent url is: {url_form}"
    )


def main():
    logging.info("Auslander spider started")
    try:
        driver = init_webdriver()
        fill_form(driver)
        html = driver.page_source
        while True:
            if time.time() - START_TIME > 1800:
                logging.info(
                    "Session expired, closing program. See you on next cronjob"
                )
                break

            if (int(time.time() - START_TIME) % 300) < 15:
                send_alive_signal(url_form)

            if not ERROR_MSG in html:
                logging.info("An appointment was found?!")
                s = Selector(text=html)
                if (
                    s.xpath('//li[@class="antcl_active"]/span/text()').extract_first()
                    != "Servicewahl"
                ):
                    logging.info("Looks like it was!!... Send mail")
                    send_mail(url_form, url_turno)
                    driver.get(url_form)
                    logging.info("Lets sleep for 5 mins")

                    if time.time() - START_TIME > 1500:
                        break

                    time.sleep(DELAY_TIME * 40)
                else:
                    logging.info("False alarm.. lets keep refreshing :(")

            url_form = driver.current_url
            clic_by_class(driver, 'id="applicationForm:managedForm:proceed"', "button")
            time.sleep(DELAY_TIME * 2)

            url_turno = driver.current_url
            html = driver.page_source

        s = Selector(text=html)
        driver.close()
    except Exception as e:
        driver.close()
        logging.error(e, exc_info=True)
        raise Exception(e)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(e, exc_info=True)
        raise Exception(e)
