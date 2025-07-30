from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def simple_test():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        print("페이지 접속 중...")
        driver.get("https://www.hyundaicard.com/cpb/gs/CPBGS2005_01.hc")
        time.sleep(10)  # 충분히 대기
        
        print("현재 페이지 제목:", driver.title)
        print("현재 URL:", driver.current_url)
        
        # 페이지 소스에서 resultList 찾기
        page_source = driver.page_source
        if 'resultList' in page_source:
            print("✅ resultList가 페이지 소스에 존재합니다")
        else:
            print("❌ resultList가 페이지 소스에 없습니다")
        
        # 검색 관련 요소들 확인
        elements_to_check = ['searchSido', 'textMrchConmNm', 'storeSearch']
        for element_id in elements_to_check:
            try:
                element = driver.find_element(By.ID, element_id)
                print(f"✅ {element_id} 요소 존재")
            except:
                print(f"❌ {element_id} 요소 없음")
        
        input("브라우저를 확인하고 Enter를 누르세요...")
        
    except Exception as e:
        print(f"오류: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    simple_test()