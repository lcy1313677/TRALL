import streamlit as st
import os
import pandas as pd
import re
from markitdown import MarkItDown

# 設定網頁標題與圖示
st.set_page_config(page_title="萬用檔案轉 Markdown / CSV 工具", page_icon="📄", layout="centered")

st.title("📄 MarkItDown 網頁版轉換器")
st.markdown("將您的 **PDF, Word, Excel, PPT, 圖片** 等檔案上傳，轉換成 Markdown 或提取出結構化的 CSV 表格。")
st.divider()

# 初始化 MarkItDown
@st.cache_resource
def load_markitdown():
    return MarkItDown()

md = load_markitdown()

# 讓使用者選擇輸出格式
output_format = st.radio(
    "請選擇輸出格式：", 
    [".md (完整 Markdown 格式)", ".csv (提取並轉換為逗號分隔值)"],
    horizontal=True
)

# 檔案上傳區塊
uploaded_files = st.file_uploader(
    "請拖曳或選擇檔案 (支援多個檔案)", 
    accept_multiple_files=True,
    help="支援格式：.pdf, .docx, .pptx, .xlsx, .csv, .html, .jpg, .png 等"
)

def extract_markdown_tables_to_csv(md_text):
    """將 Markdown 中的表格提取並轉換成 CSV 格式的字串"""
    lines = md_text.split('\n')
    csv_lines = []
    in_table = False
    
    for line in lines:
        line = line.strip()
        # 偵測 Markdown 表格行 (以 | 開頭和結尾)
        if line.startswith('|') and line.endswith('|'):
            # 略過 Markdown 表格的分隔線 (例如 |---|---| )
            if re.match(r'^\|[\s\-:]+\|$', line):
                continue
            
            # 移除頭尾的 '|' 並依 '|' 分割
            row_data = [cell.strip() for cell in line.strip('|').split('|')]
            
            # 將每個儲存格加上雙引號，避免內部原有的逗號破壞 CSV 格式
            csv_row = ','.join([f'"{cell}"' for cell in row_data])
            csv_lines.append(csv_row)
            in_table = True
        else:
            # 如果離開表格區塊，加入空行隔開不同的表格
            if in_table:
                csv_lines.append("") 
                in_table = False
                
    return '\n'.join(csv_lines)

if uploaded_files:
    if st.button("🚀 開始全部轉換", type="primary"):
        for uploaded_file in uploaded_files:
            st.write(f"**處理中:** `{uploaded_file.name}` ...")
            
            # 將上傳的檔案暫存到伺服器本地
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())
            
            try:
                with st.spinner('轉換中... 請稍候 ⏳'):
                    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                    
                    # 情況 A：使用者選擇 CSV，且原始檔案是 Excel
                    if output_format.startswith(".csv") and file_ext in ['.xlsx', '.xls']:
                        df = pd.read_excel(temp_path)
                        final_content = df.to_csv(index=False)
                        file_suffix = ".csv"
                        mime_type = "text/csv"
                        
                    # 情況 B：轉換為 Markdown，或從其他非結構化文件中提取 CSV
                    else:
                        result = md.convert(temp_path)
                        content = result.text_content if hasattr(result, 'text_content') else str(result)
                        
                        if output_format.startswith(".csv"):
                            final_content = extract_markdown_tables_to_csv(content)
                            file_suffix = ".csv"
                            mime_type = "text/csv"
                            
                            # 如果文件中完全找不到表格
                            if not final_content.strip():
                                st.warning(f"⚠️ 在 `{uploaded_file.name}` 中找不到任何表格結構可以轉換成 CSV。")
                                continue
                        else:
                            final_content = content
                            file_suffix = ".md"
                            mime_type = "text/markdown"
                    
                    st.success("✅ 轉換成功！")
                    
                    # 提供下載按鈕
                    download_name = f"{os.path.splitext(uploaded_file.name)[0]}{file_suffix}"
                    st.download_button(
                        label=f"⬇️ 下載檔案 ({download_name})",
                        data=final_content.encode('utf-8-sig'), # 使用 utf-8-sig 讓 Excel 開啟 CSV 時不會亂碼
                        file_name=download_name,
                        mime=mime_type,
                        key=f"dl_{uploaded_file.name}"
                    )
                    
                    # 顯示轉換後的預覽
                    with st.expander("👀 點此預覽內容"):
                        if file_suffix == ".md":
                            st.markdown(final_content)
                        else:
                            st.text(final_content)
                            
            except Exception as e:
                st.error(f"❌ 轉換失敗: {str(e)}")
                
            finally:
                # 清理暫存檔案
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        st.balloons()