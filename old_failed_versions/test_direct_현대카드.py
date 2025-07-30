from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

def test_direct_approach():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    wait = WebDriverWait(driver, 30)

    try:
        print("현대카드 가맹점 조회 페이지 접속 중...")
        driver.get("https://www.hyundaicard.com/cpb/gs/CPBGS2005_01.hc")
        
        # 페이지 완전 로딩 대기
        print("페이지 로딩 대기 중...")
        time.sleep(10)
        
        # 페이지에서 AJAX 호출을 직접 실행해보기
        print("JavaScript로 시도 데이터 직접 로드 시도...")
        
        # 현대카드 웹사이트의 AJAX 호출을 직접 실행
        result = driver.execute_script("""
            // 시도 데이터를 가져오는 함수 호출 시도
            try {
                // 일반적인 시도 데이터
                var sidoData = [
                    {code: '11', name: '서울특별시'},
                    {code: '26', name: '부산광역시'},
                    {code: '27', name: '대구광역시'},
                    {code: '28', name: '인천광역시'},
                    {code: '29', name: '광주광역시'},
                    {code: '30', name: '대전광역시'},
                    {code: '31', name: '울산광역시'},
                    {code: '36', name: '세종특별자치시'},
                    {code: '41', name: '경기도'},
                    {code: '42', name: '강원특별자치도'},
                    {code: '43', name: '충청북도'},
                    {code: '44', name: '충청남도'},
                    {code: '45', name: '전북특별자치도'},
                    {code: '46', name: '전라남도'},
                    {code: '47', name: '경상북도'},
                    {code: '48', name: '경상남도'},
                    {code: '50', name: '제주특별자치도'}
                ];
                
                // select 요소에 옵션 추가
                var select = document.getElementById('searchSido');
                if (select) {
                    // 기존 옵션 제거 (첫 번째 빈 옵션 제외)
                    while (select.options.length > 1) {
                        select.remove(1);
                    }
                    
                    // 새 옵션 추가
                    sidoData.forEach(function(item) {
                        var option = document.createElement('option');
                        option.value = item.code;
                        option.text = item.name;
                        select.add(option);
                    });
                    
                    return '시도 옵션 추가 완료';
                } else {
                    return 'searchSido 요소를 찾을 수 없음';
                }
            } catch (e) {
                return '오류: ' + e.message;
            }
        """)
        
        print(f"JavaScript 실행 결과: {result}")
        time.sleep(2)
        
        # 이제 시도 옵션 확인
        sido_options = driver.execute_script("""
            var select = document.getElementById('searchSido');
            var options = [];
            for(var i = 0; i < select.options.length; i++) {
                options.push({
                    value: select.options[i].value,
                    text: select.options[i].text
                });
            }
            return options;
        """)
        
        print(f"시도 옵션들: {sido_options}")
        
        # 경기도 선택
        gyeonggi_selected = driver.execute_script("""
            var select = document.getElementById('searchSido');
            for(var i = 0; i < select.options.length; i++) {
                if(select.options[i].text.includes('경기')) {
                    select.selectedIndex = i;
                    select.dispatchEvent(new Event('change'));
                    return '경기도 선택됨: ' + select.options[i].text;
                }
            }
            return '경기도 옵션을 찾을 수 없음';
        """)
        
        print(f"경기도 선택 결과: {gyeonggi_selected}")
        time.sleep(3)
        
        # 시군구 옵션 확인 (AJAX 로딩 후)
        print("시군구 옵션 로딩 대기 중...")
        for i in range(10):
            sigungu_options = driver.execute_script("""
                var select = document.getElementById('ajaxView_Sigungu');
                if (!select) return null;
                var options = [];
                for(var j = 0; j < select.options.length; j++) {
                    if(select.options[j].text.trim()) {
                        options.push({
                            value: select.options[j].value,
                            text: select.options[j].text
                        });
                    }
                }
                return options;
            """)
            
            print(f"시군구 옵션들 (시도 {i+1}): {sigungu_options}")
            
            if sigungu_options and len(sigungu_options) > 0:
                # 용인시 수지구 찾기
                suji_selected = driver.execute_script("""
                    var select = document.getElementById('ajaxView_Sigungu');
                    for(var i = 0; i < select.options.length; i++) {
                        if(select.options[i].text.includes('용인') && select.options[i].text.includes('수지')) {
                            select.selectedIndex = i;
                            select.dispatchEvent(new Event('change'));
                            return '용인시 수지구 선택됨: ' + select.options[i].text;
                        }
                    }
                    return '용인시 수지구 옵션을 찾을 수 없음';
                """)
                print(f"용인시 수지구 선택 결과: {suji_selected}")
                break
            
            time.sleep(1)
        
        # 테스트 검색
        print("\n=== 테스트 검색 시작 ===")
        test_store = "스타벅스"
        
        # 상호명 입력
        store_input_result = driver.execute_script(f"""
            var input = document.getElementById('textMrchConmNm');
            if (input) {{
                input.value = '{test_store}';
                return '상호명 입력 완료: {test_store}';
            }} else {{
                return '상호명 입력 필드를 찾을 수 없음';
            }}
        """)
        print(f"상호명 입력 결과: {store_input_result}")
        
        # 검색 버튼 클릭
        search_result = driver.execute_script("""
            var button = document.getElementById('storeSearch');
            if (button) {
                button.click();
                return '검색 버튼 클릭 완료';
            } else {
                return '검색 버튼을 찾을 수 없음';
            }
        """)
        print(f"검색 버튼 클릭 결과: {search_result}")
        
        # 검색 결과 대기
        print("검색 결과 대기 중...")
        time.sleep(5)
        
        # 결과 확인
        page_source = driver.page_source
        if "검색 결과가 없습니다" in page_source or "검색결과가 없습니다" in page_source:
            print("검색 결과: 없음 (X)")
        else:
            print("검색 결과: 있음 (O)")
        
        input("Enter를 눌러 브라우저를 닫습니다...")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    test_direct_approach()