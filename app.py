import streamlit as st
import requests
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Git2Markdown Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LOCALIZATION ---
LANGUAGES = {
    "English": {
        "title": "🚀 Git2Markdown Pro",
        "subtitle": "Transform any GitHub profile into a clean, systematic Portfolio README!",
        "sidebar_header": "⚙️ Configuration & Settings",
        "username_label": "Enter GitHub Username or Profile URL",
        "token_label": "GitHub Token (Optional - fixes rate limits)",
        "fetch_btn": "Generate Markdown Portfolio",
        "success_msg": "Portfolio successfully generated!",
        "editor_header": "✏️ Live Markdown Editor & Viewer",
        "download_btn": "Download README.md",
        "error_user": "Please enter a valid GitHub username or URL!",
        "error_not_found": "❌ GitHub user or repositories not found! Check if the username is correct.",
        "error_fetch": "Error fetching data. GitHub rate limit exceeded. Try adding an optional token in sidebar.",
        "timeout_err": "⏳ Request timed out! GitHub took too long to respond. Try again in a moment.",
        "conn_err": "🌐 Network connection error! Please check your internet.",
        "stats_repos": "Public Repositories",
        "stats_stars": "Total Stars Earned",
    },
    "Hindi (हिंदी)": {
        "title": "🚀 Git2Markdown प्रो",
        "subtitle": "किसी भी GitHub प्रोफाइल को एक शानदार पोर्टफोलियो README में बदलें!",
        "sidebar_header": "⚙️ सेटिंग्स और कॉन्फ़िगरेशन",
        "username_label": "GitHub यूजरनेम या प्रोफाइल लिंक दर्ज करें",
        "token_label": "GitHub टोकन (वैकल्पिक - रेट लिमिट ठीक करने के लिए)",
        "fetch_btn": "मार्डाउन पोर्टफोलियो बनाएं",
        "success_msg": "पोर्टफोलियो सफलतापूर्वक जनरेट हो गया!",
        "editor_header": "✏️ लाइव मार्डाउन एडिटर और व्यूअर",
        "download_btn": "README.md डाउनलोड करें",
        "error_user": "कृपया एक वैध GitHub यूजरनेम या यूआरएल दर्ज करें!",
        "error_not_found": "❌ GitHub यूजर या रिपॉजिटरी नहीं मिली!",
        "error_fetch": "डेटा लाने में त्रुटि। GitHub की रेट लिमिट समाप्त हो गई है।",
        "timeout_err": "⏳ रिक्वेस्ट टाइमआउट हो गई! कृपया थोड़ा इंतज़ार करके दोबारा कोशिश करें।",
        "conn_err": "🌐 नेटवर्क कनेक्शन त्रुटि!",
        "stats_repos": "पब्लिक रिपॉजिटरी",
        "stats_stars": "कुल स्टार्स",
    },
    "Spanish (Español)": {
        "title": "🚀 Git2Markdown Pro",
        "subtitle": "¡Transforma cualquier perfil de GitHub en un README limpio!",
        "sidebar_header": "⚙️ Configuración",
        "username_label": "Ingresa el usuario o URL de GitHub",
        "token_label": "Token de GitHub (Opcional)",
        "fetch_btn": "Generar Portafolio",
        "success_msg": "¡Portafolio generado con éxito!",
        "editor_header": "✏️ Editor y Vista Previa",
        "download_btn": "Descargar README.md",
        "error_user": "¡Ingresa un usuario o URL válido!",
        "error_not_found": "❌ ¡Usuario no encontrado!",
        "error_fetch": "Límite de API de GitHub excedido.",
        "timeout_err": "⏳ ¡Tiempo de espera agotado!",
        "conn_err": "🌐 ¡Error de red!",
        "stats_repos": "Repositorios Públicos",
        "stats_stars": "Estrellas Totales",
    },
    "Latin (Latina)": {
        "title": "🚀 Git2Markdown Pro",
        "subtitle": "Profilum GitHub in README converte!",
        "sidebar_header": "⚙️ Optiones",
        "username_label": "Nomen usoris vel URL inscribe",
        "token_label": "GitHub Token (Libere)",
        "fetch_btn": "Portfolio Generare",
        "success_msg": "Feliciter generatum!",
        "editor_header": "✏️ Editor Markdown",
        "download_btn": "Depromere README.md",
        "error_user": "Quaeso validum nomen usoris inscribe!",
        "error_not_found": "❌ Non inventus!",
        "error_fetch": "Error petendo.",
        "timeout_err": "⏳ Tempus exivit!",
        "conn_err": "🌐 Retis error!",
        "stats_repos": "Repositoria Publica",
        "stats_stars": "Summa Stellarum",
    }
}

# --- SIDEBAR SETTINGS ---
st.sidebar.markdown("### 🌐 Language")
selected_lang = st.sidebar.selectbox("Select Language", list(LANGUAGES.keys()))
t = LANGUAGES[selected_lang]

st.sidebar.markdown(f"--- \n### {t['sidebar_header']}")
raw_input_val = st.sidebar.text_input(t["username_label"], placeholder="e.g. alok-kumar8765 or profile URL")
github_token = st.sidebar.text_input(t["token_label"], type="password", placeholder="ghp_xxxxxxxxxxxx (Optional)")

include_stats = st.sidebar.checkbox("Include GitHub Stats Badge", value=True)

# --- HELPER FUNCTION TO EXTRACT USERNAME FROM URL ---
def extract_username(user_input):
    user_input = user_input.strip()
    # If user pasted a full URL like https://github.com/alok-kumar8765/something
    match = re.search(r"github\.com/([^/]+)", user_input)
    if match:
        return match.group(1)
    # Otherwise treat it as a direct username
    return user_input.split("/")[-1]

# --- MAIN UI ---
st.title(t["title"])
st.markdown(t["subtitle"])
st.markdown("---")

if st.button(t["fetch_btn"], type="primary"):
    if not raw_input_val.strip():
        st.error(t["error_user"])
    else:
        clean_username = extract_username(raw_input_val)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Setup headers (add token only if user provided it)
        headers = {"Accept": "vnd.github.v3+json"}
        if github_token.strip():
            headers["Authorization"] = f"token {github_token.strip()}"
        
        try:
            # Step 1: User Verification
            status_text.text(f"🔍 Step 1/3: Verifying user '{clean_username}'...")
            progress_bar.progress(20)
            
            user_url = f"https://api.github.com/users/{clean_username}"
            user_response = requests.get(user_url, headers=headers, timeout=10)
            
            if user_response.status_code == 404:
                progress_bar.empty()
                status_text.empty()
                st.error(t["error_not_found"])
            elif user_response.status_code == 403 or user_response.status_code == 429:
                progress_bar.empty()
                status_text.empty()
                st.error(t["error_fetch"])
            elif user_response.status_code != 200:
                progress_bar.empty()
                status_text.empty()
                st.error(t["error_fetch"])
            else:
                user_data = user_response.json()
                
                # Step 2: Fetch Repositories
                status_text.text("📁 Step 2/3: Fetching public repositories...")
                progress_bar.progress(60)
                
                repos_url = f"https://api.github.com/users/{clean_username}/repos?per_page=100&sort=updated"
                repos_response = requests.get(repos_url, headers=headers, timeout=15)
                
                if repos_response.status_code != 200:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(t["error_fetch"])
                else:
                    repos = repos_response.json()
                    
                    # Step 3: Markdown Generation
                    status_text.text("✍️ Step 3/3: Generating structured Markdown portfolio...")
                    progress_bar.progress(90)
                    
                    total_repos = len(repos)
                    total_stars = sum([repo.get("stargazers_count", 0) for repo in repos])
                    name = user_data.get("name") or clean_username
                    bio = user_data.get("bio") or "A passionate developer building cool things."
                    
                    # Build Markdown Content
                    md_content = f"# Hi there 👋, I'm {name}!\n\n"
                    md_content += f"> {bio}\n\n"
                    md_content += f"### 📊 GitHub Overview\n"
                    md_content += f"- 📁 **{t['stats_repos']}:** {total_repos}\n"
                    md_content += f"- ⭐ **{t['stats_stars']}:** {total_stars}\n\n"
                    
                    if include_stats:
                        md_content += f"![GitHub Stats](https://github-readme-stats.vercel.app/api?username={clean_username}&show_icons=true&theme=radical)\n\n"
                    
                    md_content += f"## 🚀 Repositories\n\n"
                    md_content += "| Repository | Description | Language | Stars |\n"
                    md_content += "| :--- | :--- | :---: | :---: |\n"
                    
                    for repo in repos:
                        repo_name = repo.get("name")
                        html_url = repo.get("html_url")
                        desc = repo.get("description") or "No description provided."
                        desc = desc.replace("|", "-")
                        language = repo.get("language") or "Various"
                        stars = repo.get("stargazers_count", 0)
                        
                        md_content += f"| **[{repo_name}]({html_url})** | {desc} | `{language}` | ⭐ {stars} |\n"
                    
                    st.session_state["generated_markdown"] = md_content
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Done!")
                    st.success(t["success_msg"])
                    
        except requests.exceptions.Timeout:
            progress_bar.empty()
            status_text.empty()
            st.error(t["timeout_err"])
        except requests.exceptions.ConnectionError:
            progress_bar.empty()
            status_text.empty()
            st.error(t["conn_err"])
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"An unexpected error occurred: {e}")

# --- LIVE EDITOR & SAVE SECTION ---
if "generated_markdown" in st.session_state:
    st.markdown("---")
    st.markdown(f"### {t['editor_header']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📝 Edit Markdown")
        edited_markdown = st.text_area(
            "Modify your markdown text below:",
            value=st.session_state["generated_markdown"],
            height=400,
            label_visibility="collapsed"
        )
        st.session_state["generated_markdown"] = edited_markdown

    with col2:
        st.markdown("#### 👀 Live Preview")
        st.markdown(
            f"<div style='border: 1px solid #334155; padding: 15px; border-radius: 8px; height: 400px; overflow-y: scroll; background-color: #0f172a;'>{edited_markdown}</div>",
            unsafe_allow_html=True
        )
        
    # download button
    st.download_button(
        label=f"📥 {t['download_btn']}",
        data=edited_markdown,
        file_name="README.md",
        mime="text/markdown",
        type="primary"
    )