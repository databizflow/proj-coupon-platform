from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

def debug_search_v2():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless=new')  # 주석 처리해서 브라우저 보기
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    try:
        print("현대카드 가맹점 조회 페이지 접속 중...")
        driver.get("https://www.hyundaicard.com/cpb/gs/CPBGS2005_01.hc")
        
        # 페이지 로딩 대기
        time.sleep(3)
        
        print("페이지 제목:", driver.title)
        
        # 모든 select 요소 찾기
        selects = driver.find_elements(By.TAG_NAME, "select")
        print(f"페이지에서 찾은 select 요소 개수: {len(selects)}")
        
        for i, select in enumerate(selects):
            try:
                select_id = select.get_attribute("id")
                select_name = select.get_attribute("name")
                print(f"Select {i+1}: ID='{select_id}', Name='{select_name}'")
                
                # 옵션들 확인
                options_list = select.find_elements(By.TAG_NAME, "option")
                print(f"  옵션 개수: {len(options_list)}")
                for j, option in enumerate(options_list[:5]):  # 처음 5개만
                    print(f"    옵션 {j+1}: {option.text}")
            except Exception as e:
                print(f"  Select {i+1} 정보 가져오기 실패: {e}")
        
        # 입력 필드 찾기
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"\n페이지에서 찾은 input 요소 개수: {len(inputs)}")
        
        for i, input_elem in enumerate(inputs):
            try:
                input_id = input_elem.get_attribute("id")
                input_name = input_elem.get_attribute("name")
                input_type = input_elem.get_attribute("type")
                if input_id or input_name:
                    print(f"Input {i+1}: ID='{input_id}', Name='{input_name}', Type='{input_type}'")
            except:
                pass
        
        # 버튼 찾기
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\n페이지에서 찾은 button 요소 개수: {len(buttons)}")
        
        for i, button in enumerate(buttons):
            try:
                button_id = button.get_attribute("id")
                button_text = button.text
                if button_id or button_text:
                    print(f"Button {i+1}: ID='{button_id}', Text='{button_text}'")
            except:
                pass
        
        print("\n페이지 소스 일부:")
        print(driver.page_source[:1000])
        
        input("Enter를 눌러 브라우저를 닫습니다...")
        
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_search_v2()