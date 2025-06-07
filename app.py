import streamlit as st
from openai import OpenAI
import requests

st.set_page_config(page_title="AIMM - AI Income Machine", layout="wide")
st.title("🤖 AIMM - Enhanced AI Merch Generator")

# Input API keys
openai_key = st.sidebar.text_input("🔑 OpenAI API Key", type="password")
zapier_webhook = st.sidebar.text_input("🌐 Zapier Webhook URL", type="password")

# Initialize state
if "idea" not in st.session_state:
    st.session_state.idea = ""
if "image_url" not in st.session_state:
    st.session_state.image_url = ""
if "product_type" not in st.session_state:
    st.session_state.product_type = ""

# Button 1: Generate Business Idea
if st.button("💡 Generate High-Conversion Product Idea"):
    try:
        client = OpenAI(api_key=openai_key)
        with st.spinner("Generating a winning product idea..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a best-selling Etsy strategist and AI product designer. Your job is to create profitable, evergreen print-on-demand merch ideas (shirts, mugs, posters, etc.) using AI-generated branding."},
                    {"role": "user", "content": "Give me a product idea that matches these rules:\n- It must be funny, clever, or emotionally resonant\n- It should target a niche that buys (e.g. pet lovers, teachers, gamers, parents, horror fans)\n- It must be easy to illustrate with DALL·E 3\n- Include a suggested product type (t-shirt, mug, etc.), a short Etsy-style title, and a product description"}
                ]
            )
            full_idea = response.choices[0].message.content
            st.session_state.idea = full_idea
            if "mug" in full_idea.lower():
                st.session_state.product_type = "mug"
            elif "shirt" in full_idea.lower() or "t-shirt" in full_idea.lower():
                st.session_state.product_type = "t-shirt"
            elif "poster" in full_idea.lower():
                st.session_state.product_type = "poster"
            else:
                st.session_state.product_type = "product"
        st.success("✅ Product idea generated!")
    except Exception as e:
        st.error(f"❌ Error generating idea: {e}")

# Display idea
if st.session_state.idea:
    st.subheader("💡 Product Idea")
    st.write(st.session_state.idea)

# Button 2: Generate DALL·E Branding Image
if st.session_state.idea and st.button("🎨 Create Merch-Ready DALL·E Image"):
    try:
        client = OpenAI(api_key=openai_key)
        with st.spinner("Creating high-quality merch image..."):
            prompt = f"A {st.session_state.product_type} design featuring: {st.session_state.idea}. Bold, vibrant, clean design with centered composition, transparent background, merch-ready, vector-style, suitable for Etsy listing."
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="hd",
                n=1
            )
            st.session_state.image_url = response.data[0].url
        st.success("✅ DALL·E image created!")
    except Exception as e:
        st.error(f"❌ Error generating image: {e}")

# Display image
if st.session_state.image_url:
    st.image(st.session_state.image_url, caption="DALL·E 3 Merch Image")

# Button 3: Send to Zapier
if st.session_state.idea and st.session_state.image_url and st.button("🚀 Automate Merch Drop via Zapier"):
    if zapier_webhook:
        try:
            payload = {
                "title": st.session_state.idea[:100],
                "description": st.session_state.idea,
                "image_url": st.session_state.image_url,
                "price": "29.99",
                "category": st.session_state.product_type.capitalize()
            }
            response = requests.post(zapier_webhook, json=payload)
            if response.status_code == 200:
                st.success("📤 Sent to Zapier!")
            else:
                st.error(f"❌ Zapier failed with status code: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Error sending to Zapier: {e}")
    else:
        st.warning("⚠️ Please enter your Zapier Webhook URL.")