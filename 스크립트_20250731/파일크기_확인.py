import pandas as pd

try:
    # Excel 파일 읽기
    excel_file = pd.ExcelFile('비가맹점1_정제(실행해).xlsx')
    print('📋 시트 목록:', excel_file.sheet_names)
    
    total = 0
    for sheet in excel_file.sheet_names:
        df = pd.read_excel('비가맹점1_정제(실행해).xlsx', sheet_name=sheet)
        count = len(df)
        total += count
        print(f'   {sheet}: {count:,}개')
    
    print(f'\n📊 총 처리 대상: {total:,}개')
    print(f'⏱️  예상 소요 시간: 약 {total * 4 / 60:.0f}분 (단일 처리 시)')
    
    # 분할 권장사항
    if total > 1000:
        chunks = (total // 1000) + 1
        print(f'\n💡 분할 권장: {chunks}개로 나누어 병렬 처리')
        print(f'   예상 완료 시간: 약 {total * 4 / 60 / chunks:.0f}분')
    else:
        print(f'\n✅ 단일 처리 가능 (1000개 이하)')

except Exception as e:
    print(f'❌ 오류: {e}')