import pandas as pd

# 완료된 결과 파일 읽기
df = pd.read_csv('현대카드_가맹점_조회결과_완료.csv', encoding='utf-8-sig')

# 미처리 데이터 (현대카드_가맹여부가 비어있는 것들) 필터링
unprocessed = df[df['현대카드_가맹여부'].isna() | (df['현대카드_가맹여부'] == '')]

print(f"전체 데이터: {len(df)}개")
print(f"미처리 데이터: {len(unprocessed)}개")

# 미처리 데이터를 새 파일로 저장
unprocessed.to_csv('미처리_상호명_목록.csv', index=False, encoding='utf-8-sig')
print(f"미처리 데이터 저장 완료: 미처리_상호명_목록.csv")

# 처리 완료된 데이터 통계
processed = df[df['현대카드_가맹여부'].notna() & (df['현대카드_가맹여부'] != '')]
print(f"\n처리 완료 데이터: {len(processed)}개")
if len(processed) > 0:
    result_counts = processed['현대카드_가맹여부'].value_counts()
    print("결과 통계:")
    for result, count in result_counts.items():
        if result == 'O':
            print(f"  ✅ 가맹점: {count}개")
        elif result == 'X':
            print(f"  ❌ 비가맹점: {count}개")
        else:
            print(f"  ⚠️ {result}: {count}개")