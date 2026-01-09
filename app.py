import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# ---------- 基本設定 ----------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(
    page_title="Smart Fridge Chef 🧊👨‍🍳",
    layout="centered",
)

# 深色 Vibe
st.markdown(
    """
    <style>
    body { background-color: #0e1117; color: #fafafa; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🧊 Smart Fridge Chef")
st.caption("輸入冰箱剩餘食材，AI 幫你想晚餐")

# ---------- 使用者輸入 ----------
ingredients = st.text_input(
    "請輸入冰箱裡的食材（用逗號分隔）",
    placeholder="例如：雞蛋, 番茄, 洋蔥, 起司"
)

# ---------- 主要功能 ----------
if st.button("🍳 產生食譜"):
    if not ingredients.strip():
        st.warning("請先輸入食材")
        st.stop()

    with st.spinner("AI 主廚思考中..."):

        # 1️⃣ 請 AI 產生結構化食譜（含缺少食材）
        prompt = f"""
        你是一位料理助理，請根據使用者現有食材產生三道料理。

        使用者擁有的食材：
        {ingredients}

        請嚴格依照以下格式輸出（三道）：

        【料理 1】
        菜名：
        簡介：
        缺少食材：

        【料理 2】
        菜名：
        簡介：
        缺少食材：

        【料理 3】
        菜名：
        簡介：
        缺少食材：
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.choices[0].message.content
        recipes = text.split("【料理")

        st.subheader("🍽 AI 推薦料理")

        # 2️⃣ 逐道顯示料理 + 各自生成圖片
        for r in recipes[1:]:
            block = "【料理" + r
            lines = block.splitlines()

            title = next((l.replace("菜名：", "") for l in lines if "菜名：" in l), "")
            desc = next((l.replace("簡介：", "") for l in lines if "簡介：" in l), "")
            missing = next((l.replace("缺少食材：", "") for l in lines if "缺少食材：" in l), "無")

            st.markdown(f"### 🍳 {title}")
            st.write(desc)
            st.info(f"🛒 缺少食材：{missing}")

            # 3️⃣ 為每道菜生成圖片
            img_prompt = f"""
            A delicious home cooked dish called {title},
            food photography, realistic, high quality, warm lighting
            """

            img = client.images.generate(
                model="gpt-image-1",
                prompt=img_prompt,
                size="1024x1024"
            )

            st.image(img.data[0].url, caption=title)
