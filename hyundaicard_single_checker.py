import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def random_sleep(a=1.0, b=2.0):
    time.sleep(random.uniform(a, b))

# WebDriver 설정
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    return driver

# 현대카드 가맹점 사이트 접속 및 지역 설정
def navigate_to_hyundaicard(driver):
    url = "https://www.hyundaicard.com/cpb/gs/CPBGS2005_01.hc"
    driver.get(url)
    random_sleep(3, 4)

    # 시도 선택 (경기)
    sido_select = driver.find_elements(By.TAG_NAME, "select")[0]
    driver.execute_script("""
        var select = arguments[0];
        for (let i = 0; i < select.options.length; i++) {
            if (select.options[i].text.includes('경기')) {
                select.selectedIndex = i;
                select.dispatchEvent(new Event('change', { bubbles: true }));
                break;
            }
        }
    """, sido_select)
    random_sleep(2, 3)

    # 시군구 선택 (용인시 수지구)
    sigungu_select = driver.find_elements(By.TAG_NAME, "select")[1]
    driver.execute_script("""
        var select = arguments[0];
        for (let i = 0; i < select.options.length; i++) {
            if (select.options[i].text.includes('용인시') && select.options[i].text.includes('수지구')) {
                select.selectedIndex = i;
                select.dispatchEvent(new Event('change', { bubbles: true }));
                break;
            }
        }
    """, sigungu_select)
    random_sleep(2, 3)

# 상호명 검색 및 결과 확인
def search_store(driver, store_name):
    try:
        search_input = driver.find_element(By.ID, "textMrchConmNm")
        search_input.clear()
        search_input.send_keys(store_name)
        driver.find_element(By.ID, "storeSearch").click()
        random_sleep(3, 4)

        page_source = driver.page_source
        if f"{store_name}</span>상호 검색 결과가 없습니다" in page_source or \
           f"{store_name}상호 검색 결과가 없습니다" in page_source:
            return "❌ 가맹점 아님"
        elif f"{store_name}</span>상호 검색 결과입니다" in page_source or \
             f"{store_name}상호 검색 결과입니다" in page_source:
            return "✅ 가맹점 맞음"
        else:
            return "⚠️ 결과 확인 불가"
    except Exception as e:
        logger.error(f"검색 중 오류: {e}")
        return "❌ 오류 발생"

# Streamlit 인터페이스
def main():
    st.title("💳 현대카드 가맹점 단일 조회")
    store_name = st.text_input("🔍 상호명을 입력하세요:", placeholder="예: 스타벅스")

    if st.button("가맹점 검색"):
        with st.spinner("검색 중입니다..."):
            driver = setup_driver()
            try:
                navigate_to_hyundaicard(driver)
                result = search_store(driver, store_name)
                st.success(f"검색 결과: {result}")
            finally:
                driver.quit()

if __name__ == "__main__":
    main()
