from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

def debug_search():
    # 헤드리스 모드 끄고 디버깅
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless=new')  # 주석 처리
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    try:
        driver.get("https://www.hyundaicard.com/cpb/gs/CPBGS2005_01.hc")
        wait.until(EC.presence_of_element_located((By.ID, "searchSido")))

        # 시도 선택
        Select(driver.find_element(By.ID, "searchSido")).select_by_visible_text("경기")
        time.sleep(1)

        # 시군구 선택
        Select(driver.find_element(By.ID, "ajaxView_Sigungu")).select_by_visible_text("용인시 수지구")
        time.sleep(1)

        # 동(읍면동) 선택
        dong_list = driver.find_element(By.ID, "ajaxView_Dong").text
        print(f"동 목록: {dong_list}")
        dong_to_select = "풍덕천1동" if "풍덕천1동" in dong_list else driver.find_element(By.ID, "ajaxView_Dong").find_elements(By.TAG_NAME, "option")[1].text
        Select(driver.find_element(By.ID, "ajaxView_Dong")).select_by_visible_text(dong_to_select)
        time.sleep(1)

        # 테스트용 상호명 입력 (실제 존재하는 가맹점)
        test_store = "스타벅스"
        driver.find_element(By.ID, "textMrchConmNm").clear()
        driver.find_element(By.ID, "textMrchConmNm").send_keys(test_store)

        # 검색 버튼 클릭
        driver.find_element(By.ID, "storeSearch").click()
        time.sleep(3)

        # 결과 페이지 소스 확인
        page_source = driver.page_source
        print("=== 검색 결과 페이지 소스 일부 ===")
        
        # 결과 관련 텍스트 찾기
        if "검색 결과가 없습니다" in page_source:
            print("'검색 결과가 없습니다' 메시지 발견")
        elif "검색결과가 없습니다" in page_source:
            print("'검색결과가 없습니다' 메시지 발견")
        elif "조회된 결과가 없습니다" in page_source:
            print("'조회된 결과가 없습니다' 메시지 발견")
        elif "결과가 없습니다" in page_source:
            print("'결과가 없습니다' 메시지 발견")
        else:
            print("검색 결과 있음 또는 다른 메시지")
            
        # 결과 테이블이나 리스트 확인
        try:
            result_elements = driver.find_elements(By.CSS_SELECTOR, "table, .result, .list, .search-result")
            print(f"결과 요소 개수: {len(result_elements)}")
            for i, elem in enumerate(result_elements[:3]):  # 처음 3개만
                print(f"결과 요소 {i+1}: {elem.text[:100]}...")
        except:
            print("결과 요소를 찾을 수 없음")

        input("Enter를 눌러 계속...")  # 수동으로 페이지 확인 가능
        
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_search()