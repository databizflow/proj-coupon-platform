import pandas as pd
import os

def merge_final_results():
    print("🔄 최종 통합 병합 시작!")
    print("=" * 60)
    
    try:
        # 1. 오늘한완성본 폴더의 파일 읽기
        completed_file = '------오늘한완성본/통합_가맹점_데이터.xlsx'
        print(f"📁 완성본 파일 읽기: {completed_file}")
        
        if not os.path.exists(completed_file):
            print(f"❌ 오류: '{completed_file}' 파일을 찾을 수 없습니다.")
            return False
        
        # Excel 파일의 시트 확인
        excel_file = pd.ExcelFile(completed_file)
        print(f"📋 완성본 시트 목록: {excel_file.sheet_names}")
        
        # 모든 시트 읽기
        completed_data = {}
        total_completed = 0
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(completed_file, sheet_name=sheet_name)
            completed_data[sheet_name] = df
            total_completed += len(df)
            print(f"   📊 {sheet_name}: {len(df)}개")
        
        print(f"📊 완성본 총 데이터: {total_completed:,}개")
        
        # 2. 비가맹점 재검토 결과 읽기
        non_member_file = '비가맹점_현대카드_재검토_최종결과.xlsx'
        print(f"\n📁 비가맹점 재검토 파일 읽기: {non_member_file}")
        
        if not os.path.exists(non_member_file):
            print(f"❌ 오류: '{non_member_file}' 파일을 찾을 수 없습니다.")
            return False
        
        # 비가맹점 재검토 결과 읽기
        non_member_excel = pd.ExcelFile(non_member_file)
        print(f"📋 비가맹점 시트 목록: {non_member_excel.sheet_names}")
        
        non_member_data = {}
        total_non_member = 0
        
        for sheet_name in non_member_excel.sheet_names:
            df = pd.read_excel(non_member_file, sheet_name=sheet_name)
            non_member_data[sheet_name] = df
            total_non_member += len(df)
            print(f"   📊 {sheet_name}: {len(df)}개")
        
        print(f"📊 비가맹점 재검토 총 데이터: {total_non_member:,}개")
        
        # 3. 새로 발견된 가맹점만 추출
        if '새로발견된가맹점' in non_member_data:
            new_members = non_member_data['새로발견된가맹점']
            print(f"\n🎯 새로 발견된 가맹점: {len(new_members)}개")
        else:
            print(f"\n⚠️  '새로발견된가맹점' 시트를 찾을 수 없습니다.")
            return False
        
        # 4. 통합 데이터 생성
        print(f"\n🔄 데이터 통합 중...")
        
        # 최종 통합 파일 생성
        output_file = '현대카드_가맹점_최종분석결과_최종통합.xlsx'
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 기존 완성본 시트들 복사
            for sheet_name, df in completed_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"💾 기존 시트 복사: {sheet_name} ({len(df)}개)")
            
            # 새로 발견된 가맹점 추가
            new_members.to_excel(writer, sheet_name='새로발견된가맹점_비가맹점재검토', index=False)
            print(f"💾 새 시트 추가: 새로발견된가맹점_비가맹점재검토 ({len(new_members)}개)")
            
            # 비가맹점 재검토 전체 결과도 추가
            if '전체결과' in non_member_data:
                non_member_data['전체결과'].to_excel(writer, sheet_name='비가맹점재검토_전체결과', index=False)
                print(f"💾 새 시트 추가: 비가맹점재검토_전체결과 ({len(non_member_data['전체결과'])}개)")
        
        print(f"\n💾 최종 통합 파일 저장 완료!")
        print(f"📁 파일명: {output_file}")
        
        # 5. 통합 결과 요약
        print(f"\n📊 최종 통합 결과:")
        print(f"   📋 기존 완성본 데이터: {total_completed:,}개")
        print(f"   ✅ 새로 발견된 가맹점: {len(new_members):,}개")
        print(f"   📈 총 통합 데이터: {total_completed + len(new_members):,}개")
        
        # 가맹점 증가율
        if total_completed > 0:
            increase_rate = (len(new_members) / total_completed) * 100
            print(f"   🎯 가맹점 증가율: +{increase_rate:.1f}%")
        
        print(f"\n🎉 모든 통합 작업이 완료되었습니다!")
        
        return output_file
        
    except Exception as e:
        print(f"❌ 통합 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    try:
        result_file = merge_final_results()
        if result_file:
            print(f"\n🎊 최종 통합 파일: {result_file}")
            print(f"📋 Excel에서 모든 시트를 확인할 수 있습니다!")
            print(f"🎯 특히 '새로발견된가맹점_비가맹점재검토' 시트를 확인해보세요!")
        
    except Exception as e:
        print(f"\n❌ 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()