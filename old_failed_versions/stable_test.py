from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def stable_test():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("현대카드 페이지 접속 중...")
        driver.get("https://www.hyundaicard.com/cpb/gs/CPBGS2005_01.hc")
        
        print("페이지 로딩 대기 중... (10초)")
        time.sleep(10)
        
        print(f"현재 페이지 제목: {driver.title}")
        print(f"현재 URL: {driver.current_url}")
        
        # 기본 요소들 확인
        try:
            sido_element = driver.find_element(By.ID, "searchSido")
            print("✅ searchSido 요소 찾음")
        except Exception as e:
            print(f"❌ searchSido 요소 없음: {e}")
            
        try:
            input_element = driver.find_element(By.ID, "textMrchConmNm")
            print("✅ textMrchConmNm 요소 찾음")
        except Exception as e:
            print(f"❌ textMrchConmNm 요소 없음: {e}")
            
        try:
            button_element = driver.find_element(By.ID, "storeSearch")
            print("✅ storeSearch 버튼 찾음")
        except Exception as e:
            print(f"❌ storeSearch 버튼 없음: {e}")
        
        print("\n브라우저가 열려있습니다. 수동으로 검색을 시도해보세요:")
        print("1. 경기도 선택")
        print("2. 상호명에 '스타벅스' 입력")
        print("3. 검색하기 버튼 클릭")
        print("4. 결과 확인")
        
        input("\n검색 완료 후 Enter를 누르세요...")
        
        # 검색 후 페이지 상태 확인
        print("\n=== 검색 후 페이지 분석 ===")
        
        # 페이지 소스에서 키워드 찾기
        page_source = driver.page_source.lower()
        
        keywords_to_check = ['resultlist', '검색 결과', '가맹점', '업종', '주소', '전화번호']
        for keyword in keywords_to_check:
            if keyword in page_source:
                print(f"✅ '{keyword}' 키워드 발견")
            else:
                print(f"❌ '{keyword}' 키워드 없음")
        
        # 모든 테이블 확인
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"\n페이지의 테이블 개수: {len(tables)}")
        
        for i, table in enumerate(tables):
            rows = table.find_elements(By.TAG_NAME, "tr")
            table_text = table.text[:100].replace('\n', ' ')
            print(f"테이블 {i+1}: {len(rows)}행, 내용: {table_text}...")
        
        # 결과 관련 div들 찾기
        all_divs = driver.find_elements(By.TAG_NAME, "div")
        result_divs = []
        
        for div in all_divs:
            div_text = div.text.lower()
            if any(word in div_text for word in ['검색', '결과', '가맹점', '업종']):
                result_divs.append(div)
        
        print(f"\n결과 관련 div 개수: {len(result_divs)}")
        for i, div in enumerate(result_divs[:5]):  # 처음 5개만
            div_id = div.get_attribute('id')
            div_class = div.get_attribute('class')
            div_text = div.text[:100].replace('\n', ' ')
            print(f"div {i+1}: ID='{div_id}', Class='{div_class}', 내용: {div_text}...")
        
        input("\n분석 완료. Enter를 눌러 브라우저를 닫습니다...")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        input("오류 발생. Enter를 눌러 브라우저를 닫습니다...")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    stable_test()