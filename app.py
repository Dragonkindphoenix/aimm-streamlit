import streamlit as st
from openai import OpenAI
import requests

st.set_page_config(page_title="AIMM - AI Income Machine", layout="wide")
st.title("🤖 AIMM - Enhanced AI Merch Generator")

# ─── Sidebar: API Keys & Webhook ───────────────────────────────────────────────
openai_key     = st.sidebar.text_input("🔑 OpenAI API Key", type="password")
zapier_webhook = st.sidebar.text_input("🌐 Zapier Webhook URL", type="password")

# ─── Session State ────────────────────────────────────────────────────────────
if "idea"         not in st.session_state: st.session_state.idea         = ""
if "image_url"    not in st.session_state: st.session_state.image_url    = ""
if "product_type" not in st.session_state: st.session_state.product_type = ""

# ─── Button 1: Generate High-Conversion Product Idea ──────────────────────────
if st.button("💡 Generate High-Conversion Product Idea"):
    try:
        client = OpenAI(api_key=openai_key)
        with st.spinner("Generating a data-backed, viral-worthy merch idea..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are AIMM’s Product Innovation Engine — an AI strategist who reverse-engineers "
                            "best-selling Etsy and Printify products using up-to-date trends, SEO demand, and viral niches. "
                            "You use insights from Google Trends, Etsy's top sellers, Amazon reviews, and Pinterest saves to craft "
                            "data-backed, original merch ideas that convert. All outputs must be:\n"
                            "- Fresh, never repeated\n"
                            "- Visually clear for DALL·E illustration\n"
                            "- Targeted to buyers with intent (e.g. dog moms, dark humor fans, fantasy gamers, therapists)\n"
                            "- Include: product type (mug, shirt, poster), short Etsy-style title, and a 1-2 sentence description.\n"
                            "Always optimize for shareability, emotional impact, and humor or identity-based appeal."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            "Give me one high-converting print-on-demand merch idea. Use market signals and real trends. "
                            "Format it like:\n"
                            "- **Product Type:**\n"
                            "- **Title:**\n"
                            "- **Description:**"
                        )
                    }
                ]
            )
            full_idea = response.choices[0].message.content.strip()
            st.session_state.idea = full_idea

            # Auto-detect product type
            lt = full_idea.lower()
            if "mug" in lt:      st.session_state.product_type = "mug"
            elif "shirt" in lt or "t-shirt" in lt: st.session_state.product_type = "t-shirt"
            elif "poster" in lt: st.session_state.product_type = "poster"
            else:                st.session_state.product_type = "product"

        st.success("✅ Product idea generated!")
    except Exception as e:
        st.error(f"❌ Error generating idea: {e}")

# ─── Display the Idea ─────────────────────────────────────────────────────────
if st.session_state.idea:
    st.subheader("💡 Product Idea")
    st.markdown(st.session_state.idea)

# ─── Button 2: Create Merch-Ready DALL·E Image ─────────────────────────────────
if st.session_state.idea and st.button("🎨 Create Merch-Ready DALL·E Image"):
    try:
        client = OpenAI(api_key=openai_key)
        with st.spinner("Rendering a high-quality, ad-ready image..."):
            prompt = (
                f"High-conversion {st.session_state.product_type} design based on the following idea: {st.session_state.idea}. "
                "Style: bold, clean, and centered. Include elements relevant to the idea. "
                "Suitable for Etsy listing, designed for merch, with a transparent background. "
                "Vector-style, 1024×1024, strong focal point and minimal clutter."
            )
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            st.session_state.image_url = response.data[0].url
        st.success("✅ DALL·E image created!")
    except Exception as e:
        st.error(f"❌ Error generating image: {e}")

# ─── Display the Image ─────────────────────────────────────────────────────────
if st.session_state.image_url:
    st.image(st.session_state.image_url, caption="DALL·E 3 Merch Image", use_column_width=True)

# ─── Button 3: Automate Merch Drop via Zapier ──────────────────────────────────
if st.session_state.idea and st.session_state.image_url and st.button("🚀 Automate Merch Drop via Zapier"):
    if not zapier_webhook:
        st.warning("⚠️ Please enter your Zapier Webhook URL.")
    else:
        try:
            payload = {
                "title":       st.session_state.idea.splitlines()[0][:100],
                "description": st.session_state.idea,
                "image_url":   st.session_state.image_url,
                "price":       "29.99",
                "category":    st.session_state.product_type.capitalize()
            }
            resp = requests.post(zapier_webhook, json=payload, timeout=10)
            if resp.status_code == 200:
                st.success("📤 Sent to Zapier!")
            else:
                st.error(f"❌ Zapier failed: {resp.status_code} {resp.text}")
        except Exception as e:
            st.error(f"❌ Error sending to Zapier: {e}")
