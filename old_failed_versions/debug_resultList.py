from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def debug_resultList():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    # 헤드리스 모드 끄기 - 실제 브라우저에서 확인
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    wait = WebDriverWait(driver, 20)

    try:
        print("현대카드 가맹점 조회 페이지 접속 중...")
        driver.get("https://www.hyundaicard.com/cpb/gs/CPBGS2005_01.hc")
        wait.until(EC.presence_of_element_located((By.ID, "searchSido")))
        time.sleep(5)
        
        # 시도 데이터 추가
        setup_result = driver.execute_script("""
            try {
                var sidoData = [
                    {code: '41', name: '경기도'}
                ];
                
                var select = document.getElementById('searchSido');
                if (select) {
                    while (select.options.length > 1) {
                        select.remove(1);
                    }
                    
                    sidoData.forEach(function(item) {
                        var option = document.createElement('option');
                        option.value = item.code;
                        option.text = item.name;
                        select.add(option);
                    });
                    
                    return 'success';
                } else {
                    return 'select not found';
                }
            } catch (e) {
                return 'error: ' + e.message;
            }
        """)
        print(f"시도 설정: {setup_result}")
        
        # 경기도 선택
        gyeonggi_result = driver.execute_script("""
            var select = document.getElementById('searchSido');
            for(var i = 0; i < select.options.length; i++) {
                if(select.options[i].text.includes('경기')) {
                    select.selectedIndex = i;
                    select.dispatchEvent(new Event('change'));
                    return 'success';
                }
            }
            return 'not found';
        """)
        print(f"경기도 선택: {gyeonggi_result}")
        time.sleep(3)
        
        # 테스트할 상호명들 (실제 존재하는 것과 존재하지 않는 것)
        test_stores = ["스타벅스", "맥도날드", "존재하지않는가게명12345"]
        
        for store_name in test_stores:
            print(f"\n=== '{store_name}' 검색 테스트 ===")
            
            # 상호명 입력 및 검색
            search_result = driver.execute_script(f"""
                try {{
                    var input = document.getElementById('textMrchConmNm');
                    var button = document.getElementById('storeSearch');
                    
                    if (input && button) {{
                        input.value = '{store_name}';
                        button.click();
                        return 'success';
                    }} else {{
                        return 'elements not found';
                    }}
                }} catch (e) {{
                    return 'error: ' + e.message;
                }}
            """)
            print(f"검색 실행: {search_result}")
            time.sleep(5)
            
            # 페이지 상태 상세 분석
            analysis = driver.execute_script("""
                try {
                    var result = {
                        pageTitle: document.title,
                        currentUrl: window.location.href,
                        bodyText: document.body.innerText.substring(0, 500),
                        resultListExists: !!document.getElementById('resultList'),
                        resultListContent: '',
                        allTables: [],
                        allDivs: []
                    };
                    
                    // resultList 상세 분석
                    var resultList = document.getElementById('resultList');
                    if (resultList) {
                        result.resultListContent = resultList.innerHTML;
                        result.resultListText = resultList.innerText;
                        result.resultListRows = resultList.querySelectorAll('tr').length;
                    }
                    
                    // 모든 테이블 분석
                    var tables = document.querySelectorAll('table');
                    for (var i = 0; i < tables.length; i++) {
                        var table = tables[i];
                        result.allTables.push({
                            id: table.id,
                            className: table.className,
                            rowCount: table.querySelectorAll('tr').length,
                            text: table.innerText.substring(0, 200)
                        });
                    }
                    
                    // 결과 관련 div들 찾기
                    var divs = document.querySelectorAll('div');
                    for (var j = 0; j < divs.length; j++) {
                        var div = divs[j];
                        if (div.innerText.includes('검색') || div.innerText.includes('결과') || div.innerText.includes('가맹점')) {
                            result.allDivs.push({
                                id: div.id,
                                className: div.className,
                                text: div.innerText.substring(0, 100)
                            });
                        }
                    }
                    
                    return result;
                } catch (e) {
                    return {error: e.message};
                }
            """)
            
            print("=== 페이지 분석 결과 ===")
            print(f"URL: {analysis.get('currentUrl', 'unknown')}")
            print(f"resultList 존재: {analysis.get('resultListExists', False)}")
            
            if analysis.get('resultListExists'):
                print(f"resultList 행 개수: {analysis.get('resultListRows', 0)}")
                print(f"resultList 텍스트: {analysis.get('resultListText', '')[:200]}...")
            
            print(f"전체 테이블 개수: {len(analysis.get('allTables', []))}")
            for i, table in enumerate(analysis.get('allTables', [])[:3]):
                print(f"  테이블 {i+1}: ID='{table['id']}', 행수={table['rowCount']}, 텍스트='{table['text'][:50]}...'")
            
            print(f"관련 div 개수: {len(analysis.get('allDivs', []))}")
            for i, div in enumerate(analysis.get('allDivs', [])[:3]):
                print(f"  div {i+1}: ID='{div['id']}', 텍스트='{div['text'][:50]}...'")
            
            print(f"페이지 텍스트 일부: {analysis.get('bodyText', '')[:200]}...")
            
            input("다음 검색을 위해 Enter를 누르세요...")
        
        input("테스트 완료. Enter를 눌러 브라우저를 닫습니다...")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_resultList()