import json
import requests
from fake_headers import Headers
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


MAX_PAGE = 1


def get_headers():
    return Headers(browser="chrome", os="win").generate()


def get_text(url):
    return requests.get(url, headers=get_headers()).text


def wait_element(driver, delay_seconds=1, by=By.TAG_NAME, value=None):
    return WebDriverWait(driver, delay_seconds).until(
        expected_conditions.presence_of_element_located((by, value))
    )


def parse_page(page_num):
    url = f"https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&page={page_num}"
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    div = driver.find_element(By.CLASS_NAME, "vacancy-serp-content")
    page_span = []
    for d in div.find_elements(By.CLASS_NAME, "serp-item"):
        tag_a = d.find_element(By.TAG_NAME, 'a')
        title = tag_a.text
        link = tag_a.get_attribute("href")
        price_list = [el.text.strip() for el in d.find_elements(By.CLASS_NAME, 'bloko-header-section-3')]
        price = price_list[-1].replace("\u202f", "") if len(price_list) > 1 else ""
        city_and_company = d.find_element(By.CLASS_NAME, 'vacancy-serp-item__info').text.strip().split("\n")
        if ('django' in title.lower() or 'flask' in title.lower()) and price[-3:] != 'USD':
            page_span.append({'title': title,
                              'link': link,
                              'price': price,
                              'company': city_and_company[0],
                              'city': city_and_company[1]})
    print(f"Vacancies count on page {page_num}: {len(page_span)}")
    return page_span


if __name__ == '__main__':
    res = []
    for page in range(0, MAX_PAGE):
        print('Number of page:', page)
        parsed = parse_page(page)
        if parsed:
            res += parsed
    print('Result list of vacancies in file output_data.json')

    with open("output_data.json", "w", encoding='windows-1251') as f:
        json.dump(res, f, ensure_ascii=False)
