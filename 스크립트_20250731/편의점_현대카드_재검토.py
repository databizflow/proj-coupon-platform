"""
편의점 현대카드 가맹점 재검토 프로그램
편의점시트추출수정완료.xlsx 파일의 편의점들을 현대카드 사이트에서 재검토
"""

import os
import sys
import pandas as pd
from hyundaicard_checker import HyundaiCardChecker
import logging
import time
from datetime import datetime

def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('편의점_현대카드_재검토_로그.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def process_convenience_stores():
    """편의점 현대카드 가맹점 재검토"""
    logger = setup_logging()
    
    try:
        print("🏪 편의점 현대카드 가맹점 재검토 시작!")
        print("=" * 60)
        
        # Excel 파일 읽기
        file_path = '편의점시트추출수정완료.xlsx'
        
        if not os.path.exists(file_path):
            print(f"❌ 오류: '{file_path}' 파일을 찾을 수 없습니다.")
            return False
        
        # 시트 목록 확인
        excel_file = pd.ExcelFile(file_path)
        print(f"📋 파일의 시트 목록: {excel_file.sheet_names}")
        
        # 두 시트 읽기
        sheets_data = {}
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            sheets_data[sheet_name] = df
            print(f"📊 {sheet_name} 시트: {len(df)}개")
        
        # HyundaiCardChecker 인스턴스 생성
        checker = HyundaiCardChecker()
        
        # 웹사이트 접속 및 지역 설정
        print("\n🌐 현대카드 웹사이트 접속 중...")
        if not checker.navigate_to_site():
            print("❌ 웹사이트 접속 실패")
            return False
        
        print("✅ 웹사이트 접속 및 지역 설정 완료")
        print("📍 지역: 경기도 용인시 수지구")
        print("🔗 사이트: https://www.hyundaicard.com/cpb/gs/CPBGS2005_01.hc")
        
        # 각 시트별로 처리
        total_processed = 0
        total_success = 0
        
        for sheet_name, df in sheets_data.items():
            print(f"\n🔄 {sheet_name} 시트 처리 시작...")
            print("-" * 50)
            
            # 현대카드_가맹여부 컬럼이 없으면 추가
            if '현대카드_가맹여부_재검토' not in df.columns:
                df['현대카드_가맹여부_재검토'] = ''
            
            success_count = 0
            error_count = 0
            start_time = time.time()
            
            for index, row in df.iterrows():
                store_name = str(row['상호명']).strip()
                
                if not store_name or store_name == 'nan':
                    df.at[index, '현대카드_가맹여부_재검토'] = '오류'
                    error_count += 1
                    continue
                
                print(f"\n🔍 {sheet_name} [{index+1}/{len(df)}] 검색 중: {store_name}")
                
                try:
                    # 검색 수행
                    result = checker.search_store(store_name)
                    df.at[index, '현대카드_가맹여부_재검토'] = result
                    
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
                    total_success += 1
                    
                    # 진행률 및 예상 시간 표시
                    progress = (index + 1) / len(df) * 100
                    elapsed_time = time.time() - start_time
                    avg_time_per_item = elapsed_time / (index + 1)
                    remaining_items = len(df) - (index + 1)
                    estimated_remaining_time = remaining_items * avg_time_per_item
                    
                    print(f"📊 {sheet_name} 진행률: {progress:.1f}% ({success_count}개 성공, {error_count}개 오류)")
                    print(f"⏱️  예상 남은 시간: {estimated_remaining_time/60:.1f}분")
                    
                    # 중간 저장 (10개마다)
                    if (index + 1) % 10 == 0:
                        temp_file = f'편의점_재검토_중간저장_{sheet_name}.csv'
                        df.to_csv(temp_file, index=False, encoding='utf-8-sig')
                        print(f"💾 중간 저장: {temp_file}")
                    
                except Exception as e:
                    print(f"❌ 검색 오류: {e}")
                    df.at[index, '현대카드_가맹여부_재검토'] = '오류'
                    error_count += 1
                
                total_processed += 1
            
            # 시트별 결과 통계
            result_counts = df['현대카드_가맹여부_재검토'].value_counts()
            
            print(f"\n📊 {sheet_name} 시트 완료!")
            print(f"   처리 결과:")
            for result, count in result_counts.items():
                if result == 'O':
                    print(f"     ✅ 가맹점: {count}개")
                elif result == 'X':
                    print(f"     ❌ 비가맹점: {count}개")
                else:
                    print(f"     ⚠️  {result}: {count}개")
            
            # 업데이트된 데이터 저장
            sheets_data[sheet_name] = df
        
        # 최종 Excel 파일 저장
        output_file = '편의점_현대카드_재검토_완료.xlsx'
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for sheet_name, df in sheets_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"💾 시트 저장: {sheet_name} ({len(df)}개)")
        
        print(f"\n💾 최종 파일 저장 완료!")
        print(f"📁 파일명: {output_file}")
        
        # 전체 결과 통계
        print(f"\n📊 전체 재검토 결과:")
        print(f"   총 처리: {total_processed}개")
        print(f"   성공: {total_success}개")
        print(f"   성공률: {total_success/total_processed*100:.1f}%")
        
        # 시트별 비교 분석
        print(f"\n🔍 시트별 재검토 결과:")
        for sheet_name, df in sheets_data.items():
            if '현대카드_가맹여부' in df.columns and '현대카드_가맹여부_재검토' in df.columns:
                # 기존 결과와 재검토 결과 비교
                original_o = (df['현대카드_가맹여부'] == 'O').sum()
                original_x = (df['현대카드_가맹여부'] == 'X').sum()
                new_o = (df['현대카드_가맹여부_재검토'] == 'O').sum()
                new_x = (df['현대카드_가맹여부_재검토'] == 'X').sum()
                
                print(f"   {sheet_name}:")
                print(f"     기존: ✅{original_o}개, ❌{original_x}개")
                print(f"     재검토: ✅{new_o}개, ❌{new_x}개")
                print(f"     변화: ✅{new_o-original_o:+d}개, ❌{new_x-original_x:+d}개")
        
        print(f"\n🎉 모든 재검토 작업이 완료되었습니다!")
        
        return True
        
    except Exception as e:
        print(f"❌ 처리 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
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
    print("🏪 편의점 현대카드 가맹점 재검토 프로그램")
    print("=" * 60)
    print("📁 대상 파일: 편의점시트추출수정완료.xlsx")
    print("🔗 검토 사이트: https://www.hyundaicard.com/cpb/gs/CPBGS2005_01.hc")
    print("📍 검색 지역: 경기도 용인시 수지구")
    print("=" * 60)
    
    # 사용자 확인
    while True:
        choice = input("\n🚀 재검토를 시작하시겠습니까? (y/n): ").strip().lower()
        if choice in ['y', 'yes', '예', 'ㅇ']:
            break
        elif choice in ['n', 'no', '아니오', 'ㄴ']:
            print("❌ 작업이 취소되었습니다.")
            return
        else:
            print("❌ 'y' 또는 'n'을 입력해주세요.")
    
    # 재검토 실행
    success = process_convenience_stores()
    
    if success:
        print(f"\n🎊 모든 작업이 완료되었습니다!")
        print(f"📁 결과 파일을 확인하세요: 편의점_현대카드_재검토_완료.xlsx")
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