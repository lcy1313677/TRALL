import streamlit as st
import os
from markitdown import MarkItDown

# 設定網頁標題與圖示
st.set_page_config(page_title="萬用檔案轉 Markdown 轉換器", page_icon="📄", layout="centered")

st.title("📄 MarkItDown 網頁版轉換器")
st.markdown("將您的 **PDF, Word, Excel, PPT, 圖片** 等檔案上傳，一鍵轉換成乾淨的 Markdown 格式！")
st.divider()

# 初始化 MarkItDown
@st.cache_resource
def load_markitdown():
    return MarkItDown()

md = load_markitdown()

# 檔案上傳區塊 (支援多檔上傳)
uploaded_files = st.file_uploader(
    "請拖曳或選擇檔案 (支援多個檔案)", 
    accept_multiple_files=True,
    help="支援格式：.pdf, .docx, .pptx, .xlsx, .csv, .html, .jpg, .png 等"
)

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
                    # 執行轉換
                    result = md.convert(temp_path)
                    content = result.text_content if hasattr(result, 'text_content') else str(result)
                    
                    st.success("✅ 轉換成功！")
                    
                    # 提供下載按鈕
                    st.download_button(
                        label=f"⬇️ 下載 Markdown 檔案 ({uploaded_file.name}.md)",
                        data=content,
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}.md",
                        mime="text/markdown",
                        key=uploaded_file.name # 確保每個按鈕有唯一的 key
                    )
                    
                    # 顯示轉換後的預覽 (可選)
                    with st.expander("👀 點此預覽 Markdown 內容"):
                        st.markdown(content)
                        
            except Exception as e:
                st.error(f"❌ 轉換失敗: {str(e)}")
                
            finally:
                # 清理暫存檔案
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        st.balloons() # 轉換完成撒花動畫