import pandas as pd
import os

def merge_all_to_single_sheet():
    print("🔄 모든 데이터를 한 시트로 통합 시작!")
    print("=" * 60)
    
    try:
        # 1. 기존 완성본 데이터 읽기
        completed_file = '------오늘한완성본/통합_가맹점_데이터.xlsx'
        print(f"📁 기존 완성본 읽기: {completed_file}")
        
        if os.path.exists(completed_file):
            completed_df = pd.read_excel(completed_file, sheet_name='오휴2시')
            print(f"   ✅ 기존 가맹점: {len(completed_df)}개")
        else:
            print(f"   ⚠️  기존 완성본 파일 없음")
            completed_df = pd.DataFrame()
        
        # 2. 새로 발견된 가맹점 읽기
        new_members_file = '비가맹점_현대카드_재검토_최종결과.xlsx'
        print(f"📁 새로 발견된 가맹점 읽기: {new_members_file}")
        
        if os.path.exists(new_members_file):
            new_members_df = pd.read_excel(new_members_file, sheet_name='새로발견된가맹점')
            print(f"   ✅ 새로 발견된 가맹점: {len(new_members_df)}개")
        else:
            print(f"   ❌ 새로 발견된 가맹점 파일 없음")
            return False
        
        # 3. 편의점 재검토 결과 읽기
        convenience_file = '편의점_현대카드_재검토_완료.xlsx'
        print(f"📁 편의점 재검토 결과 읽기: {convenience_file}")
        
        convenience_members = pd.DataFrame()
        if os.path.exists(convenience_file):
            try:
                # 편의점 파일의 시트들 확인
                excel_file = pd.ExcelFile(convenience_file)
                print(f"   📋 편의점 시트: {excel_file.sheet_names}")
                
                # 편의점에서 가맹점(O)인 것들만 추출
                for sheet_name in excel_file.sheet_names:
                    if 'CU' in sheet_name or 'GS25' in sheet_name or '편의점' in sheet_name:
                        df = pd.read_excel(convenience_file, sheet_name=sheet_name)
                        if '현대카드_가맹여부_재검토' in df.columns:
                            members = df[df['현대카드_가맹여부_재검토'] == 'O']
                            convenience_members = pd.concat([convenience_members, members], ignore_index=True)
                
                print(f"   ✅ 편의점 가맹점: {len(convenience_members)}개")
            except Exception as e:
                print(f"   ⚠️  편의점 파일 읽기 오류: {e}")
        else:
            print(f"   ⚠️  편의점 파일 없음")
        
        # 4. 모든 데이터 통합
        print(f"\n🔄 모든 데이터 통합 중...")
        
        all_data = []
        total_count = 0
        
        # 기존 완성본 추가
        if not completed_df.empty:
            # 구분 컬럼 추가
            completed_df['데이터_출처'] = '기존_가맹점'
            all_data.append(completed_df)
            total_count += len(completed_df)
            print(f"   ✅ 기존 가맹점 추가: {len(completed_df)}개")
        
        # 새로 발견된 가맹점 추가
        if not new_members_df.empty:
            new_members_df['데이터_출처'] = '비가맹점재검토_발견'
            all_data.append(new_members_df)
            total_count += len(new_members_df)
            print(f"   ✅ 비가맹점 재검토 발견 추가: {len(new_members_df)}개")
        
        # 편의점 가맹점 추가
        if not convenience_members.empty:
            convenience_members['데이터_출처'] = '편의점재검토_발견'
            all_data.append(convenience_members)
            total_count += len(convenience_members)
            print(f"   ✅ 편의점 재검토 발견 추가: {len(convenience_members)}개")
        
        if not all_data:
            print("❌ 통합할 데이터가 없습니다.")
            return False
        
        # 데이터 병합
        final_df = pd.concat(all_data, ignore_index=True, sort=False)
        print(f"   ✅ 초기 병합 완료: {len(final_df)}개")
        
        # 5. 중복 제거 (상호명 기준)
        print(f"\n🔍 중복 검사 및 제거...")
        
        # 상호명 컬럼 찾기
        name_columns = ['상호명', '업체명', '가맹점명', '점포명', 'name']
        name_column = None
        
        for col in name_columns:
            if col in final_df.columns:
                name_column = col
                break
        
        if name_column:
            before_dedup = len(final_df)
            final_df = final_df.drop_duplicates(subset=[name_column], keep='first')
            after_dedup = len(final_df)
            
            if before_dedup != after_dedup:
                print(f"   ⚠️  중복 제거: {before_dedup - after_dedup}개")
            else:
                print(f"   ✅ 중복 없음")
        else:
            print(f"   ⚠️  상호명 컬럼을 찾을 수 없어 중복 검사 생략")
        
        # 6. 최종 파일 저장
        output_file = '현대카드_가맹점_통합_완전판.xlsx'
        
        # 단일 시트로 저장
        final_df.to_excel(output_file, sheet_name='전체_현대카드_가맹점', index=False)
        
        print(f"\n💾 한 시트 통합 파일 저장 완료!")
        print(f"📁 파일명: {output_file}")
        print(f"📊 시트명: 전체_현대카드_가맹점")
        
        # 7. 최종 통계
        print(f"\n📊 최종 통합 통계:")
        print(f"   📋 총 현대카드 가맹점: {len(final_df):,}개")
        
        # 출처별 통계
        if '데이터_출처' in final_df.columns:
            source_counts = final_df['데이터_출처'].value_counts()
            print(f"   📈 출처별 분포:")
            for source, count in source_counts.items():
                percentage = (count / len(final_df)) * 100
                print(f"     - {source}: {count:,}개 ({percentage:.1f}%)")
        
        # 지역별 분포 (만약 주소 컬럼이 있다면)
        address_columns = ['소재지지번주소', '주소', 'address', '소재지']
        address_column = None
        
        for col in address_columns:
            if col in final_df.columns:
                address_column = col
                break
        
        if address_column:
            print(f"\n🗺️  지역별 분포 (상위 10개):")
            # 용인시 수지구 내 동별 분포
            final_df['동'] = final_df[address_column].str.extract(r'용인시 수지구 (\w+동)')
            dong_counts = final_df['동'].value_counts().head(10)
            
            for i, (dong, count) in enumerate(dong_counts.items(), 1):
                if pd.notna(dong):
                    percentage = (count / len(final_df)) * 100
                    print(f"     {i:2d}. {dong}: {count:,}개 ({percentage:.1f}%)")
        
        print(f"\n🎉 모든 현대카드 가맹점이 하나의 시트로 통합되었습니다!")
        print(f"📊 총 {len(final_df):,}개의 현대카드 가맹점 데이터")
        
        return output_file
        
    except Exception as e:
        print(f"❌ 통합 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    try:
        result_file = merge_all_to_single_sheet()
        if result_file:
            print(f"\n🎊 최종 통합 완료!")
            print(f"📁 파일: {result_file}")
            print(f"📋 모든 현대카드 가맹점이 하나의 시트에 정리되었습니다!")
        
    except Exception as e:
        print(f"\n❌ 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()