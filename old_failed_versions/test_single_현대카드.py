from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

def test_single_search():
    # 헤드리스 모드 끄기
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless=new')  # 주석 처리
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    try:
        print("현대카드 가맹점 조회 페이지 접속 중...")
        driver.get("https://www.hyundaicard.com/cpb/gs/CPBGS2005_01.hc")
        wait.until(EC.presence_of_element_located((By.ID, "searchSido")))
        
        # 시도 옵션이 로드될 때까지 기다리기
        print("시도 옵션 로딩 대기 중...")
        for i in range(10):  # 최대 10초 대기
            time.sleep(1)
            sido_select = Select(driver.find_element(By.ID, "searchSido"))
            sido_options = [option.text for option in sido_select.options if option.text.strip()]
            print(f"시도 옵션들 (시도 {i+1}): {sido_options}")
            if len(sido_options) > 0:
                break
        
        if len(sido_options) == 0:
            print("시도 옵션 로딩 실패 - 페이지 소스 확인")
            print("페이지 소스 일부:")
            print(driver.page_source[:2000])
            return
        
        gyeonggi_option = None
        for option_text in sido_options:
            if "경기" in option_text:
                gyeonggi_option = option_text
                break
        
        if gyeonggi_option:
            sido_select.select_by_visible_text(gyeonggi_option)
            print(f"'{gyeonggi_option}' 선택됨")
            time.sleep(3)
        else:
            print("경기도 옵션을 찾을 수 없음")
            return

        # 시군구 선택 (용인시 수지구)
        print("시군구 선택 중...")
        wait.until(EC.presence_of_element_located((By.ID, "ajaxView_Sigungu")))
        sigungu_select = Select(driver.find_element(By.ID, "ajaxView_Sigungu"))
        sigungu_options = [option.text for option in sigungu_select.options if option.text.strip()]
        print(f"시군구 옵션들: {sigungu_options}")
        
        suji_option = None
        for option_text in sigungu_options:
            if "용인" in option_text and "수지" in option_text:
                suji_option = option_text
                break
        
        if suji_option:
            sigungu_select.select_by_visible_text(suji_option)
            print(f"'{suji_option}' 선택됨")
            time.sleep(3)
        else:
            print("용인시 수지구 옵션을 찾을 수 없음")
            return

        # 동 선택 (선택사항)
        print("동 선택 중...")
        try:
            wait.until(EC.presence_of_element_located((By.ID, "ajaxView_Dong")))
            dong_select = Select(driver.find_element(By.ID, "ajaxView_Dong"))
            dong_options = [option.text for option in dong_select.options if option.text.strip()]
            print(f"동 옵션들: {dong_options}")
            if len(dong_options) > 0:
                dong_select.select_by_index(1 if len(dong_options) > 1 else 0)
                print(f"동 선택됨: {dong_options[1] if len(dong_options) > 1 else dong_options[0]}")
                time.sleep(2)
        except Exception as e:
            print(f"동 선택 실패: {e}")

        # 테스트용 상호명 입력
        test_stores = ["스타벅스", "맥도날드", "존재하지않는가게명12345"]
        
        for store_name in test_stores:
            print(f"\n=== '{store_name}' 검색 중 ===")
            
            # 상호명 입력
            store_input = driver.find_element(By.ID, "textMrchConmNm")
            store_input.clear()
            store_input.send_keys(store_name)
            print(f"상호명 입력: {store_name}")

            # 검색 버튼 클릭
            driver.find_element(By.ID, "storeSearch").click()
            print("검색 버튼 클릭")
            time.sleep(4)

            # 결과 확인
            page_source = driver.page_source
            
            # 다양한 "결과 없음" 메시지 패턴 확인
            no_result_patterns = [
                "검색 결과가 없습니다",
                "검색결과가 없습니다", 
                "조회된 결과가 없습니다",
                "결과가 없습니다",
                "검색된 가맹점이 없습니다",
                "가맹점이 없습니다"
            ]
            
            found_no_result = False
            for pattern in no_result_patterns:
                if pattern in page_source:
                    print(f"'{pattern}' 메시지 발견")
                    found_no_result = True
                    break
            
            if not found_no_result:
                print("결과 있음 또는 다른 메시지")
                # 결과 테이블 확인
                try:
                    result_elements = driver.find_elements(By.CSS_SELECTOR, "table, .result, .list")
                    print(f"결과 요소 개수: {len(result_elements)}")
                    for i, elem in enumerate(result_elements[:2]):
                        print(f"결과 요소 {i+1} 텍스트: {elem.text[:200]}...")
                except Exception as e:
                    print(f"결과 요소 확인 실패: {e}")
            
            result = 'X' if found_no_result else 'O'
            print(f"최종 결과: {result}")
            
            input("다음 검색을 위해 Enter를 누르세요...")

        input("테스트 완료. Enter를 눌러 브라우저를 닫습니다...")
        
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_single_search()