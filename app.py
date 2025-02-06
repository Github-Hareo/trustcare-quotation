import os
import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
import io

from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas



# 日本語フォントを登録
# フォントの相対パスを指定
font_path = "fonts/NotoSansJP-Regular.ttf"
if not os.path.exists(font_path):
    raise FileNotFoundError(f"Font file not found: {font_path}")

pdfmetrics.registerFont(TTFont("NotoSansJP", font_path))


# 商品データ
products = {
    "識別記号": ["A", "B", "C", "D", "E", "F", "G"],
    "名称": [
        "AIカメラ(AICAMX)",
        "Trust Care 見守り端末",
        "環境センサーユニット",
        "専用サーバー",
        "メッシュルータ・設定",
        "基本ケーブル・配線・検査",
        "専用VPS Tailscale",
    ],
    "単価 (¥)": [22565, 43800, 18200, 135000, 95000, 80000, 880],
    "数量上限": [100, 100, 100, 1, 1, 1, 100],
}

# ディスカウントルール
discounts = {10: 1.0, 49: 0.97, 100: 0.95}

# Streamlit UI
st.title("TrustCare 見積計算アプリ")

# 数量選択
quantities = {}
for i, row in enumerate(products["名称"]):
    max_val = products["数量上限"][i]
    default_val = 1 if max_val == 1 else 0
    quantities[row] = st.number_input(row, min_value=0, max_value=max_val, value=default_val)

# 計算処理
df = pd.DataFrame(products)
df["数量"] = df["名称"].map(quantities)
df["小計"] = df["単価 (¥)"] * df["数量"]

# 割引適用
def apply_discount(qty, price):
    for limit, rate in discounts.items():
        if qty <= limit:
            return price * rate
    return price

df["割引後価格"] = df.apply(lambda x: apply_discount(x["数量"], x["小計"]), axis=1)

# 合計金額
total_price = df["割引後価格"].sum()

# 結果表示
st.subheader("見積計算結果")
st.dataframe(df[["名称", "単価 (¥)", "数量", "小計", "割引後価格"]])
st.write(f"### **合計金額: ¥{total_price:,.0f}**")

# PDF作成
def generate_pdf(data):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setFont("NotoSansJP", 12)
    
    pdf.drawString(50, 800, "TrustCare 見積書")
    pdf.drawString(50, 780, f"合計金額: ¥{total_price:,.0f}")

    y = 750
    for index, row in data.iterrows():
        pdf.drawString(50, y, f"{row['名称']} - 数量: {row['数量']} - 合計: ¥{row['割引後価格']:,.0f}")
        y -= 20

    pdf.save()
    buffer.seek(0)
    return buffer

# PDFダウンロードボタン
if st.button("PDFとして保存"):
    pdf_buffer = generate_pdf(df)
    st.download_button("📄 PDFダウンロード", pdf_buffer, file_name="見積書.pdf", mime="application/pdf")

