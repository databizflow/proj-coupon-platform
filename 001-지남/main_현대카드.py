
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import random

# 랜덤 시간 지연 함수
def random_sleep(min_time=1, max_time=3):
    time.sleep(random.uniform(min_time, max_time))

# Selenium WebDriver 설정
def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# 현대카드 가맹점 검색 함수
def search_hyundaicard_store(driver, keyword):
    try:
        driver.get("https://www.hyundaicard.com/cpb/gs/CPBGS2005_01.hc")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "textMrchConmNm")))
        random_sleep()

        search_input = driver.find_element(By.ID, "textMrchConmNm")
        search_input.clear()
        search_input.send_keys(keyword)
        random_sleep()

        search_button = driver.find_element(By.CLASS_NAME, "btn_srch")
        search_button.click()
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "resultArea")))
        random_sleep()

        page = driver.page_source
        if "검색 결과가 없습니다" in page:
            return "❌ 검색 결과가 없습니다."
        else:
            return "✅ 가맹점이 존재합니다."
    except Exception as e:
        print(f"에러: {e}")
        return "⚠️ 검색 중 오류가 발생했습니다."

# Streamlit 인터페이스
def main():
    st.title("현대카드 가맹점 여부 조회기")

    keyword = st.text_input("상호명을 입력하세요:", "이마트")
    if st.button("현대카드 가맹 여부 확인"):
        with st.spinner("검색 중입니다..."):
            driver = setup_driver()
            try:
                result = search_hyundaicard_store(driver, keyword)
                st.success(f"검색 결과: {result}")
            finally:
                time.sleep(3)
                driver.quit()

if __name__ == "__main__":
    main()
