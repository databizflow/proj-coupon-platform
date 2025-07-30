from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time

def test_alternative_approach():
    # Chrome 옵션 설정 - JavaScript 실행을 위해 더 많은 옵션 추가
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    # options.add_argument('--headless=new')  # 주석 처리해서 브라우저 보기
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    wait = WebDriverWait(driver, 20)

    try:
        print("현대카드 가맹점 조회 페이지 접속 중...")
        driver.get("https://www.hyundaicard.com/cpb/gs/CPBGS2005_01.hc")
        
        # 페이지 완전 로딩 대기
        print("페이지 로딩 대기 중...")
        time.sleep(5)
        
        # JavaScript 실행 완료 대기
        driver.execute_script("return document.readyState") == "complete"
        
        # 모든 스크립트 로딩 대기
        wait.until(lambda driver: driver.execute_script("return jQuery.active == 0") if driver.execute_script("return typeof jQuery !== 'undefined'") else True)
        
        print("페이지 제목:", driver.title)
        
        # select 요소 찾기 및 옵션 확인
        try:
            sido_element = driver.find_element(By.ID, "searchSido")
            print(f"시도 select 요소 찾음: {sido_element}")
            
            # JavaScript로 직접 옵션 확인
            options_js = driver.execute_script("""
                var select = document.getElementById('searchSido');
                var options = [];
                for(var i = 0; i < select.options.length; i++) {
                    options.push(select.options[i].text);
                }
                return options;
            """)
            print(f"JavaScript로 가져온 옵션들: {options_js}")
            
            # 만약 옵션이 없다면 페이지 새로고침 후 재시도
            if len(options_js) <= 1:
                print("옵션이 없음 - 페이지 새로고침 후 재시도")
                driver.refresh()
                time.sleep(10)
                
                options_js = driver.execute_script("""
                    var select = document.getElementById('searchSido');
                    var options = [];
                    for(var i = 0; i < select.options.length; i++) {
                        options.push(select.options[i].text);
                    }
                    return options;
                """)
                print(f"새로고침 후 옵션들: {options_js}")
            
            # 경기도 선택 시도
            if len(options_js) > 1:
                gyeonggi_found = False
                for i, option_text in enumerate(options_js):
                    if "경기" in option_text:
                        print(f"경기도 옵션 발견: {option_text} (인덱스: {i})")
                        
                        # JavaScript로 직접 선택
                        driver.execute_script(f"""
                            var select = document.getElementById('searchSido');
                            select.selectedIndex = {i};
                            select.dispatchEvent(new Event('change'));
                        """)
                        gyeonggi_found = True
                        break
                
                if gyeonggi_found:
                    print("경기도 선택 완료 - 시군구 로딩 대기")
                    time.sleep(5)
                    
                    # 시군구 옵션 확인
                    sigungu_options = driver.execute_script("""
                        var select = document.getElementById('ajaxView_Sigungu');
                        var options = [];
                        for(var i = 0; i < select.options.length; i++) {
                            options.push(select.options[i].text);
                        }
                        return options;
                    """)
                    print(f"시군구 옵션들: {sigungu_options}")
                else:
                    print("경기도 옵션을 찾을 수 없음")
            else:
                print("시도 옵션이 로드되지 않음")
                
        except Exception as e:
            print(f"select 요소 처리 중 오류: {e}")
        
        # 현재 페이지 상태 확인
        print("\n=== 현재 페이지 상태 ===")
        print("URL:", driver.current_url)
        print("제목:", driver.title)
        
        # 모든 select 요소 확인
        selects = driver.find_elements(By.TAG_NAME, "select")
        print(f"페이지의 select 요소 개수: {len(selects)}")
        
        for i, select in enumerate(selects):
            select_id = select.get_attribute("id")
            select_name = select.get_attribute("name")
            options_count = len(select.find_elements(By.TAG_NAME, "option"))
            print(f"Select {i+1}: ID='{select_id}', Name='{select_name}', 옵션수={options_count}")
        
        input("Enter를 눌러 브라우저를 닫습니다...")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    test_alternative_approach()