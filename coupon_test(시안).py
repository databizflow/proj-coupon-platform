from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

# 크롬 드라이버 설정 (디버깅을 위한 옵션 추가)
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--headless")  # 필요시 주석 해제

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://search.konacard.co.kr/payable-merchants")

# 대기 시간 증가
wait = WebDriverWait(driver, 20)

# ▶ 1. 수원시 선택 (data-id="16")
try:
    print("페이지 로딩 중...")
    time.sleep(5)  # 페이지 완전 로딩 대기
    
    print("지역 목록 찾는 중...")
    area_list = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "area_list")))
    
    print("수원시 선택 중...")
    suwon = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li[data-id='16']")))
    driver.execute_script("arguments[0].click();", suwon)
    time.sleep(1)
    print("수원시 선택 완료")
    
    # 선택 버튼 클릭 (중요한 단계!)
    print("선택 버튼 클릭 중...")
    try:
        select_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn_select")))
        driver.execute_script("arguments[0].click();", select_button)
        print("선택 버튼 클릭 완료")
        time.sleep(2)
    except Exception as select_error:
        print(f"선택 버튼 클릭 오류: {select_error}")
        # 선택 버튼이 없어도 계속 진행
    
except Exception as e:
    print(f"지역 선택 오류: {e}")
    driver.quit()
    exit()

# ▶ 2. '다이소' 상호명 입력
try:
    print("검색어 입력 중...")
    search_input = wait.until(EC.element_to_be_clickable((By.NAME, "searchKey")))
    
    # 더 안전한 방법으로 입력 필드 클리어
    try:
        search_input.clear()
    except:
        # clear()가 실패하면 JavaScript로 값 제거
        driver.execute_script("arguments[0].value = '';", search_input)
    
    search_input.send_keys("올리브영")
    print("검색어 입력 완료")
    
    # ▶ 3. 검색 버튼 클릭
    print("검색 버튼 클릭 중...")
    search_button = driver.find_element(By.CSS_SELECTOR, "button.btn_search")
    driver.execute_script("arguments[0].click();", search_button)
    print("검색 버튼 클릭 완료")
    
    # ▶ 4. 결과 테이블 로딩 대기 (AJAX 요청 완료까지)
    print("검색 결과 로딩 대기 중...")
    
    # 테이블이 나타날 때까지 대기
    wait.until(EC.visibility_of_element_located((By.ID, "table_view")))
    
    # 데이터가 실제로 로드될 때까지 대기 (빈 테이블이 아닌)
    wait.until(lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "#dataList tbody tr")) > 0)
    
    # AJAX 로딩이 완료될 때까지 추가 대기
    time.sleep(3)
    print("검색 결과 로딩 완료")
    
except Exception as e:
    print(f"검색 과정 오류: {e}")
    driver.quit()
    exit()

# ▶ 5. 테이블 정보 수집
try:
    rows = driver.find_elements(By.CSS_SELECTOR, "#dataList tbody tr")
    results = []
    
    print(f"총 {len(rows)}개의 매장 정보를 수집 중...")
    
    for i, row in enumerate(rows):
        try:
            columns = row.find_elements(By.TAG_NAME, "td")
            if len(columns) >= 4:  # 정상적인 데이터 행인지 확인
                store_name = columns[0].text.strip()
                category = columns[1].text.strip()
                address = columns[2].text.strip()
                phone = columns[3].text.strip()
                
                # 빈 데이터나 "검색 결과 없음" 메시지 제외
                if store_name and "검색한 정보로" not in store_name:
                    results.append({
                        "매장명": store_name,
                        "업종": category,
                        "주소": address,
                        "전화번호": phone
                    })
                    print(f"{i+1}. {store_name} - {address}")
        except Exception as e:
            print(f"행 {i+1} 처리 중 오류: {e}")
            continue
    
    print(f"수집 완료: {len(results)}개 매장")
    
except Exception as e:
    print(f"데이터 수집 오류: {e}")
    results = []

# ▶ 6. Pandas로 보기 좋게 출력
df = pd.DataFrame(results)
print(df)

# ▶ 7. 크롬 종료
driver.quit()
