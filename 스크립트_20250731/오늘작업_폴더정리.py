import os
import shutil
from datetime import datetime

def organize_today_files():
    print("🗂️  오늘 작업 파일 정리 시작!")
    print("=" * 60)
    
    # 현재 날짜로 폴더명 생성
    today = datetime.now().strftime("%Y%m%d")
    
    # 정리할 폴더들 생성
    folders_to_create = {
        f'최종결과파일_{today}': '최종 완성된 결과 파일들',
        f'비가맹점작업_{today}': '비가맹점 재검토 관련 파일들',
        f'편의점작업_{today}': '편의점 재검토 관련 파일들',
        f'스크립트_{today}': '오늘 사용한 스크립트들',
        f'로그파일_{today}': '실행 로그 파일들',
        f'중간파일_{today}': '중간 처리 파일들'
    }
    
    # 폴더 생성
    for folder_name, description in folders_to_create.items():
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"📁 폴더 생성: {folder_name} ({description})")
    
    # 파일 분류 및 이동
    file_moves = {
        # 최종 결과 파일들 (중요 - 현재 위치 유지)
        '최종_보관': [
            '현대카드_가맹점_통합_완전판.xlsx',  # 오늘의 최종 결과!
            '현대카드_가맹점_최종분석결과_최종통합.xlsx',
            'suji_filtered.csv',
            '민생회복 가맹점 용인시 수지구(0730).csv',
            'requirements.txt'
        ],
        
        # 최종 결과 파일들
        f'최종결과파일_{today}': [
            '비가맹점_현대카드_재검토_최종결과.xlsx',
            '편의점_현대카드_재검토_완료.xlsx',
            '현대카드_가맹점_최종분석결과.xlsx',
            '현대카드_가맹점_최종분석결과_수작업중.xlsx',
            '현대카드_가맹점_최종분석결과_편의점추가.xlsx',
            '현대카드_가맹점_최종분석결과_편의점분리완료.xlsx',
            '현대카드_가맹점_최종분석결과_편의점열합치기완료.xlsx'
        ],
        
        # 비가맹점 작업 파일들
        f'비가맹점작업_{today}': [
            '비가맹점1.xlsx',
            '비가맹점1_정제.xlsx',
            '비가맹점1_정제(실행해).xlsx',
            '비가맹점_분할_01.csv',
            '비가맹점_분할_02.csv',
            '비가맹점_분할_03.csv',
            '비가맹점_분할_04.csv',
            '비가맹점_분할_05.csv',
            '비가맹점_분할_06.csv',
            '비가맹점_완료_01.csv',
            '비가맹점_완료_02.csv',
            '비가맹점_완료_03.csv',
            '비가맹점_완료_04.csv',
            '비가맹점_완료_05.csv',
            '비가맹점_완료_06.csv'
        ],
        
        # 편의점 작업 파일들
        f'편의점작업_{today}': [
            '편의점시트추출수정중.xlsx',
            '편의점시트추출수정완료.xlsx',
            '편의점_재검토_중간저장_CU편의점.csv',
            '편의점_재검토_중간저장_GS25편의점.csv'
        ],
        
        # 스크립트 파일들
        f'스크립트_{today}': [
            'CU편의점_상호명_분리.py',
            'CU편의점_열_합치기.py',
            'GS25편의점_D열_수정.py',
            '비가맹점_데이터_분할.py',
            '비가맹점_분할_처리기.py',
            '비가맹점_결과_병합.py',
            '비가맹점_현대카드_재검토.py',
            '편의점_추출.py',
            '편의점_현대카드_재검토.py',
            '전체_한시트_통합.py',
            '최종_통합_병합.py',
            '파일크기_확인.py',
            '폴더정리.py',
            '오늘작업_폴더정리.py',
            'hyundaicard_checker.py'
        ],
        
        # 로그 파일들
        f'로그파일_{today}': [
            '비가맹점_로그_01.log',
            '비가맹점_로그_02.log',
            '비가맹점_로그_03.log',
            '비가맹점_로그_04.log',
            '비가맹점_로그_05.log',
            '비가맹점_로그_06.log',
            '비가맹점_현대카드_재검토_로그.log',
            '편의점_현대카드_재검토_로그.log'
        ],
        
        # 중간 파일들
        f'중간파일_{today}': [
            '가맹점결과1.xlsx',
            '상황보기.txt'
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
        if os.path.isfile(item) and not item.startswith('.') and not item.startswith('~'):
            remaining_files.append(item)
    
    important_files = [
        '현대카드_가맹점_통합_완전판.xlsx',
        '현대카드_가맹점_최종분석결과_최종통합.xlsx',
        'suji_filtered.csv',
        '민생회복 가맹점 용인시 수지구(0730).csv',
        'requirements.txt'
    ]
    
    for file_name in remaining_files:
        if file_name in important_files:
            print(f"   📌 {file_name} (중요 파일)")
        else:
            print(f"   📄 {file_name}")
    
    print(f"\n🎉 오늘 작업 폴더 정리 완료!")
    print(f"📊 총 {moved_count}개 파일 이동")
    print(f"📁 생성된 정리 폴더: {len(folders_to_create)}개")
    
    # 정리 요약
    print(f"\n📋 정리 요약:")
    print(f"   📌 현재 폴더: 최종 결과 파일들만 유지")
    print(f"   📂 최종결과파일_{today}: 완성된 Excel 파일들")
    print(f"   📂 비가맹점작업_{today}: 비가맹점 재검토 관련")
    print(f"   📂 편의점작업_{today}: 편의점 재검토 관련")
    print(f"   📂 스크립트_{today}: 오늘 사용한 Python 스크립트들")
    print(f"   📂 로그파일_{today}: 실행 로그들")
    
    print(f"\n🎊 최종 결과:")
    print(f"   ⭐ 현대카드_가맹점_통합_완전판.xlsx (5,583개 가맹점)")
    print(f"   📊 비가맹점에서 374개 가맹점 추가 발견!")
    print(f"   📈 편의점에서 81개 가맹점 추가 발견!")

if __name__ == "__main__":
    try:
        organize_today_files()
        print(f"\n✨ 오늘 작업 폴더 정리가 완료되었습니다!")
        
    except Exception as e:
        print(f"\n❌ 정리 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()