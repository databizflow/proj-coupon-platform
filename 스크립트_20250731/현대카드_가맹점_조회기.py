"""
현대카드 가맹점 조회 독립 실행 프로그램
hyundaicard_checker 모듈을 사용하여 CSV 파일의 상호명들을 자동으로 조회
"""

import os
import sys
import pandas as pd
from hyundaicard_checker import HyundaiCardChecker
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('현대카드_조회_로그.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def print_banner():
    """프로그램 시작 배너"""
    print("=" * 60)
    print("🏪 현대카드 가맹점 자동 조회 프로그램")
    print("=" * 60)
    print("📋 CSV 파일의 상호명들을 현대카드 웹사이트에서 자동 조회")
    print("📍 지역: 경기도 용인시 수지구")
    print("📊 결과: O(가맹점), X(비가맹점)")
    print("=" * 60)

def check_input_file(file_path):
    """입력 파일 존재 여부 및 구조 확인"""
    if not os.path.exists(file_path):
        print(f"❌ 오류: '{file_path}' 파일을 찾을 수 없습니다.")
        return False
    
    try:
        # 파일 읽기 테스트
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        if '상호명' not in df.columns:
            print(f"❌ 오류: '{file_path}' 파일에 '상호명' 컬럼이 없습니다.")
            print(f"📋 현재 컬럼: {list(df.columns)}")
            return False
        
        print(f"✅ 입력 파일 확인 완료")
        print(f"📊 총 {len(df)}개 상호명 발견")
        print(f"📋 컬럼: {list(df.columns)}")
        print(f"🔍 첫 5개 상호명:")
        for i, name in enumerate(df['상호명'].head()):
            print(f"   {i+1}. {name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 파일 읽기 오류: {e}")
        return False

def get_user_confirmation(input_file, output_file, total_count):
    """사용자 확인"""
    print("\n" + "=" * 50)
    print("📋 작업 요약")
    print("=" * 50)
    print(f"📁 입력 파일: {input_file}")
    print(f"📁 출력 파일: {output_file}")
    print(f"📊 처리할 상호명 개수: {total_count}개")
    print(f"⏱️  예상 소요 시간: 약 {total_count * 3 // 60}분")
    print("🌐 검색 지역: 경기도 용인시 수지구")
    print("=" * 50)
    
    while True:
        choice = input("\n🚀 작업을 시작하시겠습니까? (y/n): ").strip().lower()
        if choice in ['y', 'yes', '예', 'ㅇ']:
            return True
        elif choice in ['n', 'no', '아니오', 'ㄴ']:
            return False
        else:
            print("❌ 'y' 또는 'n'을 입력해주세요.")

def process_hyundai_card_check(input_file, output_file):
    """현대카드 가맹점 조회 실행"""
    try:
        print("\n🚀 현대카드 가맹점 조회 시작!")
        print("-" * 50)
        
        # HyundaiCardChecker 인스턴스 생성
        checker = HyundaiCardChecker()
        
        # CSV 파일 읽기
        df = pd.read_csv(input_file, encoding='utf-8-sig')
        df['현대카드_가맹여부'] = ''
        
        # 웹사이트 접속 및 지역 설정
        print("🌐 현대카드 웹사이트 접속 중...")
        if not checker.navigate_to_site():
            print("❌ 웹사이트 접속 실패")
            return False
        
        print("✅ 웹사이트 접속 및 지역 설정 완료")
        print("📍 지역: 경기도 용인시 수지구")
        
        # 각 상호명 검색
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            store_name = str(row['상호명']).strip()
            
            if not store_name or store_name == 'nan':
                df.at[index, '현대카드_가맹여부'] = '오류'
                error_count += 1
                continue
            
            print(f"\n🔍 [{index+1}/{len(df)}] 검색 중: {store_name}")
            
            try:
                # 검색 수행
                result = checker.search_store(store_name)
                df.at[index, '현대카드_가맹여부'] = result
                
                # 결과 표시
                if result == 'O':
                    print(f"✅ 결과: 가맹점 발견")
                elif result == 'X':
                    print(f"❌ 결과: 가맹점 없음")
                else:
                    print(f"⚠️  결과: {result}")
                    error_count += 1
                    continue
                
                success_count += 1
                
                # 진행률 표시
                progress = (index + 1) / len(df) * 100
                print(f"📊 진행률: {progress:.1f}% ({success_count}개 성공, {error_count}개 오류)")
                
                # 중간 저장 (100개마다)
                if (index + 1) % 100 == 0:
                    df.to_csv(output_file, index=False, encoding='utf-8-sig')
                    print(f"💾 중간 저장 완료: {index + 1}개 처리")
                
            except Exception as e:
                print(f"❌ 검색 오류: {e}")
                df.at[index, '현대카드_가맹여부'] = '오류'
                error_count += 1
        
        # 최종 저장
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        # 결과 통계
        result_counts = df['현대카드_가맹여부'].value_counts()
        
        print("\n" + "=" * 50)
        print("🎉 작업 완료!")
        print("=" * 50)
        print(f"📁 결과 파일: {output_file}")
        print(f"📊 처리 결과:")
        for result, count in result_counts.items():
            if result == 'O':
                print(f"   ✅ 가맹점: {count}개")
            elif result == 'X':
                print(f"   ❌ 비가맹점: {count}개")
            else:
                print(f"   ⚠️  {result}: {count}개")
        
        print(f"📈 성공률: {success_count}/{len(df)} ({success_count/len(df)*100:.1f}%)")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ 처리 중 오류 발생: {e}")
        return False
    
    finally:
        # WebDriver 종료
        try:
            checker.close()
            print("🔒 브라우저 종료 완료")
        except:
            pass

def main():
    """메인 함수"""
    print_banner()
    
    # 기본 파일 경로
    default_input = "suji_filtered.csv"
    default_output = "현대카드_가맹점_조회결과.csv"
    
    # 입력 파일 확인
    print(f"\n📁 기본 입력 파일: {default_input}")
    
    if os.path.exists(default_input):
        use_default = input(f"기본 파일을 사용하시겠습니까? (y/n): ").strip().lower()
        if use_default in ['y', 'yes', '예', 'ㅇ']:
            input_file = default_input
        else:
            input_file = input("입력 파일 경로를 입력하세요: ").strip()
    else:
        print(f"⚠️  기본 파일 '{default_input}'을 찾을 수 없습니다.")
        input_file = input("입력 파일 경로를 입력하세요: ").strip()
    
    # 입력 파일 검증
    if not check_input_file(input_file):
        print("❌ 프로그램을 종료합니다.")
        return
    
    # 출력 파일 설정
    output_file = input(f"\n출력 파일명 (기본값: {default_output}): ").strip()
    if not output_file:
        output_file = default_output
    
    # 파일 개수 확인
    df = pd.read_csv(input_file, encoding='utf-8-sig')
    total_count = len(df)
    
    # 사용자 확인
    if not get_user_confirmation(input_file, output_file, total_count):
        print("❌ 작업이 취소되었습니다.")
        return
    
    # 현대카드 가맹점 조회 실행
    success = process_hyundai_card_check(input_file, output_file)
    
    if success:
        print(f"\n🎊 모든 작업이 완료되었습니다!")
        print(f"📁 결과 파일을 확인하세요: {output_file}")
    else:
        print(f"\n💥 작업 중 오류가 발생했습니다.")
    
    input("\n⏎ Enter를 눌러 종료...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n💥 예상치 못한 오류: {e}")
        input("⏎ Enter를 눌러 종료...")