
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time
import random

def random_sleep(min_time=1, max_time=2):
    time.sleep(random.uniform(min_time, max_time))

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def extract_region_city(address):
    try:
        if "용인시 수지구" in address:
            return "경기", "용인시 수지구"
        elif "서울" in address:
            return "서울", "종로구"
        else:
            return "기타", "기타"
    except:
        return "기타", "기타"

def search_coupon(driver, region, city, keyword):
    driver.get("https://www.shinhancard.com/mob/MOBFM591N/MOBFM591R03.shc")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "impr-aria-list")))
    random_sleep()

    # 시도 선택
    try:
        city_radio = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//div[text()='{region}']")))
        city_radio.click()
        random_sleep()
    except:
        return False

    driver.find_element(By.ID, "nextBtn").click()
    random_sleep()

    try:
        gu_radio = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//div[text()='{city} ']")))
        gu_radio.click()
        random_sleep()
    except:
        return False

    driver.find_element(By.ID, "confirmBtn").click()
    random_sleep()

    try:
        search_box = driver.find_element(By.ID, "placeSearch")
        search_box.clear()
        search_box.send_keys(keyword)
        random_sleep()
        driver.find_element(By.XPATH, "//button[@aria-label='검색']").click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "result-list")))
        results = driver.find_elements(By.XPATH, "//div[contains(@class, 'store-list')]")
        return True if results else False
    except:
        return False

# 실행
df = pd.read_csv("지역화폐 가맹점 용인시 수지구.csv", encoding="cp949")
df["신한카드 소비쿠폰"] = ""

driver = setup_driver()
for i in range(len(df)):
    name = df.loc[i, '상호명']
    addr = df.loc[i, '소재지도로명주소']
    region, city = extract_region_city(addr)
    result = search_coupon(driver, region, city, name)
    df.loc[i, "신한카드 소비쿠폰"] = "✅" if result else "❌"
driver.quit()

df.to_excel("신한카드_소비쿠폰_결과.xlsx", index=False)
print("✅ 결과 저장 완료: 신한카드_소비쿠폰_결과.xlsx")
