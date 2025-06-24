import streamlit as st
from openai import OpenAI
import requests
import random

# ─── App Config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="AIMM Pro - Automated AI Merch Generator", layout="wide")
st.title("🤖 AIMM Pro – Automated AI Merch Generator with Etsy-Driven Niche Validation")

# ─── Sidebar: API Keys & Webhooks ──────────────────────────────────────────────
openai_key       = st.sidebar.text_input("🔑 OpenAI API Key", type="password")
etsy_api_key     = st.sidebar.text_input("🗝️ Etsy API Key", type="password")
zapier_webhook   = st.sidebar.text_input("🌐 Zapier Webhook URL", type="password")
printify_api_key = st.sidebar.text_input("🔐 Printify API Key", type="password")
printify_shop_id = st.sidebar.text_input("🏷️ Printify Shop ID")

# ─── Sidebar: Candidate Niches via Etsy API ───────────────────────────────────
st.sidebar.markdown("### 🔍 Step 1: Auto-Validate Niche via Etsy API")
candidates = st.sidebar.text_area(
    "Enter candidate niches (one per line):",
    value="Cottagecore Animal Mugs\nDark Academia Poster Prints\nChaotic Gamer T-Shirts"
).splitlines()

def get_etsy_trends(term: str):
    url = "https://openapi.etsy.com/v3/application/listings/active"
    headers = {"x-api-key": etsy_api_key}
    params  = {
        "limit": 50,
        "keyword": term,
        "sort_on": "score",
        "sort_order": "down"
    }
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json().get("results", [])

if st.sidebar.button("🔍 Auto-Select Hot Niche (Etsy)"):
    if not etsy_api_key:
        st.error("Please enter your Etsy API Key.")
    else:
        try:
            hits = {}
            for term in candidates:
                term = term.strip()
                if not term:
                    continue
                results = get_etsy_trends(term)
                hits[term] = len(results)
            # pick the niche with the most active listings
            hot = max(hits, key=hits.get)
            st.success(f"🔥 Hot Etsy niche: **{hot}** ({hits[hot]} listings)")
            st.session_state.hot_niche = hot
        except Exception as e:
            st.error(f"Etsy API error: {e}")

# Show validated niche in sidebar
if "hot_niche" in st.session_state:
    st.sidebar.markdown(f"#### ✅ Validated Niche:\n**{st.session_state.hot_niche}**")

# ─── Session State Defaults ────────────────────────────────────────────────────
for var in ("idea", "image_url", "product_type"):
    if var not in st.session_state:
        st.session_state[var] = ""

prompt_context = st.session_state.get("hot_niche", "")

# ─── Button: Generate High-Converting Idea ─────────────────────────────────────
if st.button("💡 Generate High-Conversion Product Idea"):
    if not openai_key:
        st.error("Please enter your OpenAI API Key.")
    elif not prompt_context:
        st.warning("Please auto-select a validated niche first.")
    else:
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
                                "best-selling Etsy and Printify products using real Etsy marketplace data, SEO demand, "
                                "and viral niches. All outputs must be:\n"
                                "- Fresh, never repeated\n"
                                "- Visually clear for DALL·E illustration\n"
                                "- Targeted to buyers with intent\n"
                                "- Include: product type (mug, shirt, poster), short Etsy-style title, and a 1-2 sentence description.\n"
                                "Always optimize for shareability, emotional impact, and humor or identity-based appeal."
                            )
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Using Etsy niche '{prompt_context}', give me one fresh, ultra-specific print-on-demand product idea "
                                "that sells on Etsy. Format as:\n"
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
            st.error(f"Error generating idea: {e}")

# ─── Display the Idea ─────────────────────────────────────────────────────────
if st.session_state.idea:
    st.subheader("💡 Product Idea")
    st.markdown(st.session_state.idea)

# ─── Button: Generate Merch-Ready DALL·E Image ─────────────────────────────────
if st.session_state.idea and st.button("🎨 Create Merch-Ready Image"):
    try:
        client = OpenAI(api_key=openai_key)
        with st.spinner("Rendering a high-quality image..."):
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
        st.success("✅ Image created!")
    except Exception as e:
        st.error(f"Error generating image: {e}")

# ─── Display the Image ─────────────────────────────────────────────────────────
if st.session_state.image_url:
    st.image(
        st.session_state.image_url,
        caption="DALL·E 3 Merch Image",
        use_container_width=True
    )

# ─── Button: Automate Merch Drop via Zapier & Printify/Etsy ────────────────────
if (
    st.session_state.idea and
    st.session_state.image_url and
    st.button("🚀 Automate Merch Drop")
):
    if not zapier_webhook:
        st.warning("Please enter your Zapier Webhook URL.")
    else:
        # Price logic
        prod = st.session_state.product_type.lower()
        if "mug" in prod:
            price = "17.99"
        elif "shirt" in prod:
            price = "29.99"
        elif "poster" in prod:
            price = "21.99"
        else:
            price = "19.99"

        payload = {
            "title":       st.session_state.idea.splitlines()[0][:100],
            "description": st.session_state.idea,
            "image_url":   st.session_state.image_url,
            "price":       price,
            "category":    st.session_state.product_type.capitalize()
        }

        # Send to Zapier
        try:
            resp = requests.post(zapier_webhook, json=payload, timeout=10)
            if resp.status_code == 200:
                st.success(f"📤 Sent to Zapier! Price set at ${price}")
            else:
                st.error(f"Zapier failed: {resp.status_code} {resp.text}")
        except Exception as e:
            st.error(f"Error sending to Zapier: {e}")

        # Surface Etsy URL via Printify API (optional)
        if printify_api_key and printify_shop_id:
            headers = {"Authorization": f"Bearer {printify_api_key}"}
            r = requests.get(
                f"https://api.printify.com/v1/shops/{printify_shop_id}/products.json?limit=10",
                headers=headers,
                timeout=10
            )
            if r.ok:
                for p in r.json().get("data", []):
                    if p.get("title", "").startswith(payload["title"]):
                        for store in p.get("external_stores", []):
                            if store.get("integration_type") == "etsy":
                                etsy_id  = store["id"]
                                etsy_url = f"https://www.etsy.com/listing/{etsy_id}"
                                st.success(f"🛒 Live on Etsy: [View Listing]({etsy_url})")
                                break
                        break
            else:
                st.error("Could not retrieve Printify products.")
