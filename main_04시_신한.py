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
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# 신한카드 사이트에서 쿠폰을 검색하고 결과를 반환하는 함수
def search_coupon(driver, region, city, keyword):
    # 신한카드 사이트 접속
    driver.get("https://www.shinhancard.com/mob/MOBFM591N/MOBFM591R03.shc")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "impr-aria-list")))
    random_sleep(1, 2)

    # 지역 선택
    city_radio_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//div[text()='{region}']")))
    city_radio_button.click()
    random_sleep(1, 2)

    # 다음 버튼 클릭
    nextBtn = driver.find_element(By.ID, "nextBtn")
    nextBtn.click()
    random_sleep(1, 2)

    # 구/동 선택 스크롤 및 클릭
    scroll_until_element_found_and_click(driver)


    confirmBtn = driver.find_element(By.ID, "confirmBtn")
    confirmBtn.click()
    random_sleep()
    # 키워드 입력 및 검색
    search_box = driver.find_element(By.ID, "placeSearch")
    search_box.clear()
    search_box.send_keys(keyword)
    random_sleep(1, 2)

    # 검색 버튼 클릭
    search_button = driver.find_elements(By.XPATH, "//button[@aria-label='검색']")[1]
    search_button.click()
    random_sleep(2, 3)

    # 결과 확인
    try:
        # 검색결과가 있을 경우 display: none 확인
        place_list = driver.find_element(By.CLASS_NAME, "place-list")
        display_style = driver.execute_script("return window.getComputedStyle(arguments[0]).getPropertyValue('display');", place_list)
        
        if display_style == 'none':
            return "검색결과가 없습니다."
        else:
            return "검색결과가 있습니다."
            
    except Exception as e:
        print(f"에러코드: {e}")
        return "검색 중 오류가 발생했습니다."
# 스크롤하여 요소를 찾고 클릭하는 함수
def scroll_until_element_found_and_click(driver, max_scroll_attempts=10):
    attempts = 0
    while attempts < max_scroll_attempts:
        try:
            element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//div[text()='용인시 수지구']"))
            )
            driver.execute_script("arguments[0].scrollIntoView();", element)
            random.uniform(2,3)
            element.click()
            random.uniform(2,3)
            return
        except Exception:
            driver.execute_script(f"window.scrollBy(0, {random.randint(480, 520)});")
            random_sleep(0.3, 0.5)
            attempts += 1

# Streamlit 인터페이스 설정
def main():
    st.title("신한카드 소비쿠폰 검색")
    
    # 사용자가 검색할 지역과 키워드 입력받기
    region = st.selectbox("지역을 선택하세요:", ["경기", "인천", "부산", "대구"])
    city = st.selectbox("구/동을 선택하세요:", ["용인시 수지구", "강남구", "마포구", "수원시", "대전시"])
    keyword = st.text_input("검색할 키워드를 입력하세요:", "이마트")

    # 시작 버튼 클릭
    if st.button("쿠폰 검색 시작"):
        # 로딩 화면 표시
        with st.spinner("로딩 중... 기다려 주세요..."):
            driver = setup_driver()
            try:
                result = search_coupon(driver, region, city, keyword)
                # 결과 출력
                st.success(f"검색 결과: {result}")
            finally:
                time.sleep(10)
                driver.quit()
    
if __name__ == "__main__":
    main()
