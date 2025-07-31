import pandas as pd
import os

def merge_non_member_results():
    print("🔄 비가맹점 분할 처리 결과 병합 시작!")
    print("=" * 60)
    
    # 완료 파일들 확인
    completion_files = []
    for i in range(1, 7):  # 1~6
        file_name = f'비가맹점_완료_{i:02d}.csv'
        if os.path.exists(file_name):
            completion_files.append(file_name)
            print(f"✅ 발견: {file_name}")
        else:
            print(f"⚠️  누락: {file_name}")
    
    if not completion_files:
        print("❌ 완료된 파일이 없습니다.")
        return
    
    print(f"\n📊 병합할 파일: {len(completion_files)}개")
    
    # 각 파일 읽기 및 병합
    all_results = []
    total_processed = 0
    
    for file_name in completion_files:
        try:
            df = pd.read_csv(file_name, encoding='utf-8-sig')
            
            # 처리된 데이터만 필터링 (현대카드_가맹여부_재검토가 있는 것들)
            if '현대카드_가맹여부_재검토' in df.columns:
                processed = df[df['현대카드_가맹여부_재검토'].notna() & (df['현대카드_가맹여부_재검토'] != '')]
                all_results.append(processed)
                total_processed += len(processed)
                print(f"   📁 {file_name}: {len(processed)}개 처리됨")
            else:
                print(f"   ⚠️  {file_name}: 재검토 컬럼 없음")
                
        except Exception as e:
            print(f"   ❌ {file_name}: 읽기 오류 - {e}")
    
    if not all_results:
        print("❌ 병합할 데이터가 없습니다.")
        return
    
    # 모든 결과 병합
    print(f"\n🔄 결과 병합 중...")
    merged_df = pd.concat(all_results, ignore_index=True)
    print(f"✅ 병합 완료: {len(merged_df)}개")
    
    # 중복 제거 (혹시 있을 수 있는)
    print(f"\n🔍 중복 검사...")
    before_dedup = len(merged_df)
    
    # 상호명 컬럼 찾기
    name_column = None
    possible_columns = ['상호명', '업체명', '가맹점명', '점포명', 'name', '상호']
    for col in possible_columns:
        if col in merged_df.columns:
            name_column = col
            break
    
    if name_column:
        merged_df = merged_df.drop_duplicates(subset=[name_column], keep='first')
        after_dedup = len(merged_df)
        
        if before_dedup != after_dedup:
            print(f"⚠️  중복 제거: {before_dedup - after_dedup}개")
        else:
            print(f"✅ 중복 없음")
    else:
        print(f"⚠️  상호명 컬럼을 찾을 수 없어 중복 검사 생략")
    
    # 결과 통계
    print(f"\n📊 최종 병합 결과:")
    result_counts = merged_df['현대카드_가맹여부_재검토'].value_counts()
    
    total_count = len(merged_df)
    for result, count in result_counts.items():
        percentage = (count / total_count) * 100
        if result == 'O':
            print(f"   ✅ 현대카드 가맹점: {count:,}개 ({percentage:.1f}%)")
        elif result == 'X':
            print(f"   ❌ 비가맹점: {count:,}개 ({percentage:.1f}%)")
        else:
            print(f"   ⚠️  {result}: {count:,}개 ({percentage:.1f}%)")
    
    # Excel 파일로 저장 (두 개 시트)
    output_file = '비가맹점_현대카드_재검토_최종결과.xlsx'
    
    # 가맹점과 비가맹점 분리
    members = merged_df[merged_df['현대카드_가맹여부_재검토'] == 'O'].copy()
    non_members = merged_df[merged_df['현대카드_가맹여부_재검토'] == 'X'].copy()
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 전체 결과
        merged_df.to_excel(writer, sheet_name='전체결과', index=False)
        print(f"\n💾 '전체결과' 시트: {len(merged_df)}개")
        
        # 가맹점만
        if len(members) > 0:
            members.to_excel(writer, sheet_name='새로발견된가맹점', index=False)
            print(f"💾 '새로발견된가맹점' 시트: {len(members)}개")
        
        # 비가맹점만
        if len(non_members) > 0:
            non_members.to_excel(writer, sheet_name='확인된비가맹점', index=False)
            print(f"💾 '확인된비가맹점' 시트: {len(non_members)}개")
    
    print(f"\n💾 Excel 파일 저장 완료!")
    print(f"📁 파일명: {output_file}")
    
    # 원본 데이터와 비교
    try:
        original_df = pd.read_excel('비가맹점1_정제(실행해).xlsx', sheet_name='Sheet1')
        original_count = len(original_df)
        processed_count = len(merged_df)
        coverage = (processed_count / original_count) * 100
        
        print(f"\n🔍 원본 데이터와 비교:")
        print(f"   📋 원본 비가맹점: {original_count:,}개")
        print(f"   ✅ 재검토 완료: {processed_count:,}개")
        print(f"   📈 처리율: {coverage:.1f}%")
        
        if coverage < 100:
            remaining = original_count - processed_count
            print(f"   ⚠️  미처리: {remaining:,}개")
            
        # 가맹점 발견율
        if 'O' in result_counts:
            discovery_rate = result_counts['O'] / original_count * 100
            print(f"   🎯 전체 대비 가맹점 발견율: {discovery_rate:.1f}%")
            
    except Exception as e:
        print(f"   ⚠️  원본 파일 비교 불가: {e}")
    
    print(f"\n🎉 모든 병합 작업이 완료되었습니다!")
    print(f"📊 총 {len(merged_df):,}개 업체 재검토 완료")
    
    if 'O' in result_counts:
        print(f"🎊 놀라운 발견: 기존 비가맹점 중 {result_counts['O']:,}개가 실제로는 현대카드 가맹점이었습니다!")
    
    return output_file

if __name__ == "__main__":
    try:
        result_file = merge_non_member_results()
        if result_file:
            print(f"\n🎊 최종 결과 파일: {result_file}")
            print(f"📋 Excel에서 시트별로 결과를 확인할 수 있습니다!")
        
    except Exception as e:
        print(f"\n❌ 병합 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()