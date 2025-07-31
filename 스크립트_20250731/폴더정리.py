import os
import shutil
from datetime import datetime

def organize_files():
    print("🗂️  폴더 정리 시작!")
    print("=" * 50)
    
    # 현재 날짜로 폴더명 생성
    today = datetime.now().strftime("%Y%m%d")
    
    # 정리할 폴더들 생성
    folders_to_create = {
        f'완료파일_{today}': '최종 완료된 결과 파일들',
        f'로그파일_{today}': '실행 로그 파일들', 
        f'중간파일_{today}': '중간 처리 파일들',
        f'스크립트_{today}': '사용한 스크립트 파일들',
        f'원본데이터_{today}': '원본 데이터 파일들'
    }
    
    # 폴더 생성
    for folder_name, description in folders_to_create.items():
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"📁 폴더 생성: {folder_name} ({description})")
    
    # 파일 분류 및 이동
    file_moves = {
        # 최종 완료 파일들 (중요 - 남겨둘 것들)
        '최종_보관': [
            '현대카드_가맹점_최종분석결과.xlsx',
            'suji_filtered.csv',
            '민생회복 가맹점 용인시 수지구(0730).csv'
        ],
        
        # 완료 파일들
        f'완료파일_{today}': [
            '현대카드_가맹점_조회결과_완료.csv',
            '현대카드_가맹점_조회결과_최종완료.csv',
            '현대카드_가맹점_분석결과.xlsx',
            '완료_분할_01.csv',
            '완료_분할_02.csv', 
            '완료_분할_03.csv',
            '완료_분할_04.csv',
            '완료_분할_05.csv',
            '완료_분할_06.csv',
            '완료_분할_07.csv'
        ],
        
        # 로그 파일들
        f'로그파일_{today}': [
            '로그_분할_01.log',
            '로그_분할_02.log',
            '로그_분할_03.log', 
            '로그_분할_04.log',
            '로그_분할_05.log',
            '로그_분할_06.log',
            '로그_분할_07.log',
            '현대카드_재조회_로그.log',
            '현대카드_조회_로그.log'
        ],
        
        # 중간 처리 파일들
        f'중간파일_{today}': [
            '미처리_분할_01.csv',
            '미처리_분할_02.csv',
            '미처리_분할_03.csv',
            '미처리_분할_04.csv', 
            '미처리_분할_05.csv',
            '미처리_분할_06.csv',
            '미처리_분할_07.csv',
            '미처리_상호명_목록.csv',
            '미처리_상호명_목록_진행중.csv',
            '미처리_상호명_목록_진행중.csv 내가_확인할_파일.csv',
            '4'
        ],
        
        # 스크립트 파일들
        f'스크립트_{today}': [
            '현대카드_가맹점_조회기.py',
            '현대카드_미처리_재조회.py',
            '현대카드_분할_처리기.py',
            '미처리_데이터_분할.py',
            '미처리_데이터_추출.py',
            '결과_병합.py',
            '전체_결과_병합.py',
            '비가맹점_추출.py',
            '진행상황_모니터.py',
            'hyundaicard_checker.py',
            'hyundaicard_single_checker.py',
            'main_04시_신한.py',
            'main_현대카드_단일검색.py'
        ]
    }
    
    # 파일 이동 실행
    moved_count = 0
    for folder_name, file_list in file_moves.items():
        if folder_name == '최종_보관':
            print(f"\n📌 최종 보관 파일들 (현재 위치 유지):")
            for file_name in file_list:
                if os.path.exists(file_name):
                    print(f"   ✅ {file_name}")
                else:
                    print(f"   ⚠️  {file_name} (파일 없음)")
            continue
            
        print(f"\n📂 {folder_name} 폴더로 이동:")
        for file_name in file_list:
            if os.path.exists(file_name):
                try:
                    shutil.move(file_name, os.path.join(folder_name, file_name))
                    print(f"   ✅ {file_name}")
                    moved_count += 1
                except Exception as e:
                    print(f"   ❌ {file_name} 이동 실패: {e}")
            else:
                print(f"   ⚠️  {file_name} (파일 없음)")
    
    # 기타 파일들 확인
    print(f"\n📋 현재 폴더에 남은 파일들:")
    remaining_files = []
    for item in os.listdir('.'):
        if os.path.isfile(item) and not item.startswith('.'):
            remaining_files.append(item)
    
    important_files = [
        '현대카드_가맹점_최종분석결과.xlsx',
        'suji_filtered.csv', 
        '민생회복 가맹점 용인시 수지구(0730).csv',
        'requirements.txt'
    ]
    
    for file_name in remaining_files:
        if file_name in important_files:
            print(f"   📌 {file_name} (중요 파일)")
        else:
            print(f"   📄 {file_name}")
    
    print(f"\n🎉 폴더 정리 완료!")
    print(f"📊 총 {moved_count}개 파일 이동")
    print(f"📁 생성된 정리 폴더: {len(folders_to_create)}개")
    
    # 정리 요약
    print(f"\n📋 정리 요약:")
    print(f"   📌 현재 폴더: 중요 파일들만 유지")
    print(f"   📂 완료파일_{today}: 최종 결과 파일들")
    print(f"   📂 로그파일_{today}: 실행 로그들")
    print(f"   📂 중간파일_{today}: 중간 처리 파일들")
    print(f"   📂 스크립트_{today}: 사용한 스크립트들")

if __name__ == "__main__":
    try:
        organize_files()
        print(f"\n✨ 폴더 정리가 완료되었습니다!")
        
    except Exception as e:
        print(f"\n❌ 정리 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()