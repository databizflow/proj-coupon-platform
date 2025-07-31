import pandas as pd

def merge_all_including_manual():
    print("🔄 모든 결과 병합 시작 (수동 작업 포함)!")
    print("=" * 60)
    
    try:
        # 1. 기존 분할 처리 결과 읽기
        print("📁 기존 분할 처리 결과 읽기...")
        existing_df = pd.read_csv('현대카드_가맹점_조회결과_최종완료.csv', encoding='utf-8-sig')
        print(f"   ✅ 분할 처리 결과: {len(existing_df)}개")
        
        # 2. 수동 작업 결과 읽기 (여러 인코딩 시도)
        print("\n📁 수동 작업 결과 읽기...")
        manual_df = None
        encodings = ['utf-8-sig', 'cp949', 'euc-kr', 'utf-8']
        
        for encoding in encodings:
            try:
                # 탭으로 구분된 파일일 수 있으므로 separator 시도
                manual_df = pd.read_csv('미처리_상호명_목록_진행중.csv', encoding=encoding, sep='\t')
                print(f"   ✅ 인코딩 성공: {encoding} (탭 구분)")
                break
            except:
                try:
                    manual_df = pd.read_csv('미처리_상호명_목록_진행중.csv', encoding=encoding)
                    print(f"   ✅ 인코딩 성공: {encoding}")
                    break
                except:
                    continue
        
        if manual_df is None:
            print("   ❌ 수동 작업 파일을 읽을 수 없습니다.")
            return None
        
        # 처리된 데이터만 필터링
        manual_processed = manual_df[manual_df['현대카드_가맹여부'].notna() & (manual_df['현대카드_가맹여부'] != '')]
        print(f"   ✅ 수동 작업 결과: {len(manual_processed)}개")
        
        # 3. 두 결과 합치기
        print("\n🔄 결과 병합 중...")
        
        # 데이터 합치기
        all_results = pd.concat([existing_df, manual_processed], ignore_index=True)
        print(f"   ✅ 병합 완료: {len(all_results)}개")
        
        # 4. 중복 제거 (사업자등록번호 + 상호명 기준)
        print("\n🔍 중복 검사 및 제거...")
        before_dedup = len(all_results)
        all_results = all_results.drop_duplicates(subset=['사업자등록번호', '상호명'], keep='first')
        after_dedup = len(all_results)
        
        if before_dedup != after_dedup:
            print(f"   ⚠️  중복 제거: {before_dedup - after_dedup}개")
        else:
            print(f"   ✅ 중복 없음")
        
        # 5. 결과 통계
        print(f"\n📊 최종 통합 결과:")
        result_counts = all_results['현대카드_가맹여부'].value_counts()
        
        total_processed = len(all_results)
        for result, count in result_counts.items():
            percentage = (count / total_processed) * 100
            if result == 'O':
                print(f"   ✅ 현대카드 가맹점: {count:,}개 ({percentage:.1f}%)")
            elif result == 'X':
                print(f"   ❌ 비가맹점: {count:,}개 ({percentage:.1f}%)")
            else:
                print(f"   ⚠️  {result}: {count:,}개 ({percentage:.1f}%)")
        
        # 6. 비가맹점만 추출
        non_members = all_results[all_results['현대카드_가맹여부'] == 'X'].copy()
        
        # 7. Excel 파일로 저장 (3개 시트)
        output_file = '현대카드_가맹점_최종분석결과.xlsx'
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 첫 번째 시트: 전체 결과
            all_results.to_excel(writer, sheet_name='전체결과', index=False)
            print(f"\n💾 '전체결과' 시트: {len(all_results)}개")
            
            # 두 번째 시트: 비가맹점만
            non_members.to_excel(writer, sheet_name='비가맹점', index=False)
            print(f"💾 '비가맹점' 시트: {len(non_members)}개")
            
            # 세 번째 시트: 가맹점만
            members = all_results[all_results['현대카드_가맹여부'] == 'O'].copy()
            members.to_excel(writer, sheet_name='가맹점', index=False)
            print(f"💾 '가맹점' 시트: {len(members)}개")
        
        print(f"\n💾 Excel 파일 저장 완료!")
        print(f"📁 파일명: {output_file}")
        
        # 8. 상세 분석
        print(f"\n📊 상세 분석:")
        print(f"   - 총 처리 건수: {len(all_results):,}개")
        print(f"   - 현대카드 가맹점: {len(members):,}개 ({len(members)/len(all_results)*100:.1f}%)")
        print(f"   - 비가맹점: {len(non_members):,}개 ({len(non_members)/len(all_results)*100:.1f}%)")
        
        # 원본 데이터와 비교
        try:
            original_df = pd.read_csv('suji_filtered.csv', encoding='utf-8-sig')
            original_count = len(original_df)
            coverage = (len(all_results) / original_count) * 100
            
            print(f"\n🔍 원본 데이터와 비교:")
            print(f"   📋 원본 데이터: {original_count:,}개")
            print(f"   ✅ 처리 완료: {len(all_results):,}개")
            print(f"   📈 처리율: {coverage:.1f}%")
            
            if coverage < 100:
                remaining = original_count - len(all_results)
                print(f"   ⚠️  미처리: {remaining:,}개")
        except:
            print("   ⚠️  원본 파일 비교 불가")
        
        print(f"\n🎉 모든 병합 작업이 완료되었습니다!")
        
        return output_file
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result_file = merge_all_including_manual()
    if result_file:
        print(f"\n🎊 최종 결과 파일: {result_file}")
        print(f"📋 Excel에서 세 개 시트를 확인할 수 있습니다:")
        print(f"   - '전체결과': 모든 조회 결과")
        print(f"   - '비가맹점': 현대카드 사용 불가 업체")
        print(f"   - '가맹점': 현대카드 사용 가능 업체")