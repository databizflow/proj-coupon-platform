import pandas as pd

def merge_cu_columns():
    print("🔄 CU편의점 C열과 D열 합치기 시작!")
    print("=" * 50)
    
    try:
        # Excel 파일 읽기
        file_path = '현대카드_가맹점_최종분석결과_편의점분리완료.xlsx'
        
        # CU편의점 시트 읽기
        df_cu = pd.read_excel(file_path, sheet_name='CU편의점')
        print(f"📊 CU편의점 데이터: {len(df_cu)}개")
        
        # 컬럼 확인
        print(f"📋 현재 컬럼: {list(df_cu.columns)}")
        
        # C열과 D열이 브랜드명, 지점명인지 확인
        if len(df_cu.columns) >= 4:
            c_column = df_cu.columns[2]  # C열 (0-based index 2)
            d_column = df_cu.columns[3]  # D열 (0-based index 3)
            
            print(f"📍 C열: {c_column}")
            print(f"📍 D열: {d_column}")
            
            # C열과 D열 합치기
            def combine_columns(row):
                c_val = str(row[c_column]) if pd.notna(row[c_column]) else ''
                d_val = str(row[d_column]) if pd.notna(row[d_column]) else ''
                
                # 둘 다 비어있으면 빈 문자열
                if not c_val and not d_val:
                    return ''
                # C열만 있으면 C열만
                elif c_val and not d_val:
                    return c_val
                # D열만 있으면 D열만  
                elif not c_val and d_val:
                    return d_val
                # 둘 다 있으면 합치기
                else:
                    # 공백으로 구분해서 합치기
                    if c_val.endswith(')') and not d_val.startswith('('):
                        return f"{c_val}{d_val}"  # 괄호 뒤에는 바로 붙이기
                    else:
                        return f"{c_val} {d_val}" if c_val and d_val else (c_val or d_val)
            
            # 새로운 합친 컬럼 생성
            df_cu['합친_상호명'] = df_cu.apply(combine_columns, axis=1)
            
            # 합친 결과를 C열 위치에 넣고, D열 제거
            df_cu[c_column] = df_cu['합친_상호명']
            df_cu = df_cu.drop([d_column, '합친_상호명'], axis=1)
            
            print(f"✅ C열과 D열 합치기 완료!")
            
            # 결과 샘플 출력
            print(f"\n📋 합치기 결과 샘플 (처음 10개):")
            print("=" * 60)
            for i, (idx, row) in enumerate(df_cu.head(10).iterrows()):
                print(f"{i+1:2d}. {row[c_column]}")
            
        else:
            print("❌ 컬럼이 충분하지 않습니다.")
            return None
        
        # 기존 Excel 파일의 모든 시트를 유지하면서 CU편의점 시트만 업데이트
        output_file = '현대카드_가맹점_최종분석결과_편의점열합치기완료.xlsx'
        
        # 기존 파일의 모든 시트 읽기
        excel_data = {}
        try:
            excel_file = pd.ExcelFile(file_path)
            for sheet_name in excel_file.sheet_names:
                if sheet_name == 'CU편의점':
                    excel_data[sheet_name] = df_cu  # 수정된 데이터 사용
                else:
                    excel_data[sheet_name] = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f"📋 시트 로드: {sheet_name}")
        except Exception as e:
            print(f"⚠️  기존 파일 읽기 오류: {e}")
            excel_data = {'CU편의점': df_cu}
        
        # Excel 파일로 저장
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for sheet_name, data in excel_data.items():
                data.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"💾 시트 저장: {sheet_name} ({len(data)}개)")
        
        print(f"\n💾 Excel 파일 저장 완료!")
        print(f"📁 파일명: {output_file}")
        
        print(f"\n🎉 CU편의점 열 합치기 완료!")
        print(f"📊 C열과 D열이 하나의 열로 합쳐졌습니다!")
        
        return output_file
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result_file = merge_cu_columns()
    if result_file:
        print(f"\n🎊 작업 완료!")
        print(f"📁 결과 파일: {result_file}")
        print(f"📋 CU편의점 시트에서 C열과 D열이 합쳐졌습니다!")