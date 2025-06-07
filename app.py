import streamlit as st
from openai import OpenAI
import requests
import random

st.set_page_config(page_title="AIMM Pro - Premium AI Merch Generator", layout="wide")
st.title("🤖 AIMM Pro - Premium AI Merch Generator")

# ─── Sidebar: API Keys & Webhook ───────────────────────────────────────────────
openai_key     = st.sidebar.text_input("🔑 OpenAI API Key", type="password")
zapier_webhook = st.sidebar.text_input("🌐 Zapier Webhook URL", type="password")

# ─── Prompt Guidance Controls ──────────────────────────────────────────────────
st.sidebar.markdown("### 🎯 Prompt Guidance")
niche_options = [
    "Funny parenting quotes", "Cottagecore animals", "Dark academia skeletons",
    "Retro-futuristic tech jokes", "Weird cryptid merch", "Anxious therapist memes",
    "Lesbian space cowboys", "Evil plant moms", "Birdwatcher fan art",
    "Wholesome goth aesthetics", "Chaotic gamer humor"
]
selected_niche = st.sidebar.selectbox("Choose a niche:", niche_options)

if "seed" not in st.session_state:
    st.session_state.seed = ""
if st.sidebar.button("🎲 Roll Creative Seed"):
    adjectives = ["unhinged", "wholesome", "vintage", "chaotic", "haunted", "sassy", "stoic"]
    niches     = ["gardeners", "gamers", "cat moms", "anime fans", "paranormal lovers", "teachers"]
    items      = ["frogs", "skeletons", "robots", "ghosts", "mushrooms", "aliens"]
    st.session_state.seed = f"{random.choice(adjectives)} {random.choice(niches)} with {random.choice(items)}"
st.sidebar.write(f"🧪 Current Seed: **{st.session_state.seed or selected_niche}**")

# ─── Session State ────────────────────────────────────────────────────────────
for var in ["idea", "image_url", "product_type"]:
    if var not in st.session_state:
        st.session_state[var] = ""

# Use seed if available, else selected niche
prompt_context = st.session_state.seed or selected_niche

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
                            f"Use the context seed '{prompt_context}'. "
                            "Give me one fresh, ultra-specific print-on-demand product idea that Etsy has never seen before. "
                            "Format as:\n"
                            "- **Product Type:**\n"
                            "- **Title:**\n"
                            "- **Description:**"
                        )
                    }
                ]
            )
            full_idea = response.choices[0].message.content.strip()
            st.session_state.idea = full_idea

            lt = full_idea.lower()
            if "mug" in lt:
                st.session_state.product_type = "mug"
            elif "shirt" in lt or "t-shirt" in lt:
                st.session_state.product_type = "t-shirt"
            elif "poster" in lt:
                st.session_state.product_type = "poster"
            else:
                st.session_state.product_type = "product"

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
                f"Merch design for a {st.session_state.product_type} based on this idea: {st.session_state.idea}. "
                "Centered composition, bold vector illustration, minimal clutter, high contrast, white or transparent background, "
                "made for professional merch printing."
            )
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

# ─── Display the Image ─────────────────────────────────────────────────────────
if st.session_state.image_url:
    st.image(st.session_state.image_url, caption="DALL·E 3 Merch Image", use_column_width=True)

# ─── Price Logic & Button 3: Automate Merch Drop via Zapier ───────────────────
if st.session_state.idea and st.session_state.image_url and st.button("🚀 Automate Merch Drop via Zapier"):
    if not zapier_webhook:
        st.warning("⚠️ Please enter your Zapier Webhook URL.")
    else:
        # Auto price based on product type
        prod = st.session_state.product_type.lower()
        if "mug" in prod:
            price = "17.99"
        elif "shirt" in prod:
            price = "29.99"
        elif "poster" in prod:
            price = "21.99"
        else:
            price = "19.99"

        try:
            payload = {
                "title":       st.session_state.idea.splitlines()[0][:100],
                "description": st.session_state.idea,
                "image_url":   st.session_state.image_url,
                "price":       price,
                "category":    st.session_state.product_type.capitalize()
            }
            resp = requests.post(zapier_webhook, json=payload, timeout=10)
            if resp.status_code == 200:
                st.success(f"📤 Sent to Zapier! Price set at ${price}")
            else:
                st.error(f"❌ Zapier failed: {resp.status_code} {resp.text}")
        except Exception as e:
            st.error(f"❌ Error sending to Zapier: {e}")
