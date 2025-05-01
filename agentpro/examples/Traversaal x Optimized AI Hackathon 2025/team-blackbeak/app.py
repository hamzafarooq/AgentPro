import streamlit as st
from agentpro import (
    php_tool, audit_tool, security_tool, extract_files_tool,
    integration_tool, test_tool, doc_tool, file_reader_tool, zip_reader_tool
)
from agentpro.agent import AgentPro
import os
import json
import shutil
from datetime import datetime

# === Constants ===
HISTORY_DIR = "history"

# === Agents Initialization ===
tools_map = {
    "migrate": php_tool,
    "audit": audit_tool,
    "integration": integration_tool,
    "security": security_tool,
    "test": test_tool,
    "doc": doc_tool,
    "extract_files": extract_files_tool
}
agents = {name: AgentPro(tools=[tool]) for name, tool in tools_map.items()}
agent_reader = file_reader_tool
agent_zip_reader = zip_reader_tool

# === Streamlit UI ===
st.set_page_config(page_title="Multi-Agent Migration App", layout="wide")
st.title("🤖 Multi-Agent PHP to Next.js Migration")
st.markdown("Migrate, analyze, secure and automatically deploy PHP projects to Next.js.")

# === Helper Functions ===
def save_history(data, filename=None):
    os.makedirs(HISTORY_DIR, exist_ok=True)
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_name = filename.replace(" ", "_") if filename else "migration"
    file_key = f"{file_name} {run_id}.json"
    with open(f"{HISTORY_DIR}/{file_key}", "w", encoding="utf-8") as f:
        json.dump({"timestamp": run_id, "filename": filename, **data}, f, indent=2)
    return file_key

def load_history(file_name):
    with open(f"{HISTORY_DIR}/{file_name}", encoding="utf-8") as f:
        return json.load(f)

def display_section(title, content, display_type="code", language=None):
    with st.expander(title, expanded=True):
        if display_type == "code":
            st.code(content, language=language)
        elif display_type == "markdown":
            st.markdown(content, unsafe_allow_html=True)
        elif display_type == "text":
            st.text(content)

def list_directory_files(root_dir):
    file_list = []
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            rel_dir = os.path.relpath(dirpath, root_dir)
            rel_file = os.path.join(rel_dir, file) if rel_dir != "." else file
            file_list.append(rel_file)
    return file_list

def export_project(base_path, export_name):
    if not os.path.exists(base_path):
        raise FileNotFoundError("Export path not found")
    zip_path = f"{export_name}.zip"
    shutil.make_archive(export_name, "zip", base_path)
    return zip_path

# === Sidebar History ===
st.sidebar.subheader("📜 Migration History")
if os.path.exists(HISTORY_DIR):
    history_files = sorted(os.listdir(HISTORY_DIR), reverse=True)
    for file in history_files:
        label = file.replace(".json", "")
        if st.sidebar.button(label, key=file):
            st.session_state["selected_history"] = file
            st.session_state["show_history"] = True

# === Migration Tab ===
tabs = st.tabs(["🚀 Migration"])

with tabs[0]:
    st.subheader("🔁 Intelligent Migration")
    zip_file = st.file_uploader("📂 Load a PHP project (.zip or .php)", type=["php", "zip"])
    php_code = ""

    if zip_file:
        if zip_file.name.endswith(".zip"):
            php_code = agent_zip_reader.run(zip_file)
        else:
            content = zip_file.read().decode("utf-8")
            php_code = agent_reader.run(content)

    php_code = st.text_area("📝 PHP code to analyze or migrate", value=php_code, height=300)

    if st.button("🚀 Start Migration") and php_code:
        st.session_state.pop("selected_history", None)
        st.session_state["show_history"] = False

        with st.spinner("Running multi-agent pipeline..."):
            progress = st.progress(0)
            step_status = st.empty()
            step_count = 7

            def update_status(done):
                status = ["✅" if i < done else "⏳" for i in range(step_count)]
                labels = ["Audit", "Security", "Migration", "Test", "Extract", "Integrate", "Docs"]
                lines = [f"- {status[i]} Step {i+1}: {labels[i]}" for i in range(step_count)]
                step_status.markdown("**Migration Progress**\n" + "\n".join(lines))

            current_step = 0
            update_status(current_step)

            audit = agents["audit"](php_code); current_step += 1; progress.progress(current_step/step_count); update_status(current_step)
            security = agents["security"](php_code); current_step += 1; progress.progress(current_step/step_count); update_status(current_step)
            migration = agents["migrate"](php_code); current_step += 1; progress.progress(current_step/step_count); update_status(current_step)
            tests = agents["test"](migration); current_step += 1; progress.progress(current_step/step_count); update_status(current_step)
            extract_file = agents["extract_files"](migration); current_step += 1; progress.progress(current_step/step_count); update_status(current_step)
            integration_result = agents["integration"](extract_file); current_step += 1; progress.progress(current_step/step_count); update_status(current_step)

            integration_log = integration_result["log"]
            base_path = integration_result["path"]

            docs = agents["doc"](migration); current_step += 1; progress.progress(current_step/step_count); update_status(current_step)

            file_key = save_history({
                "php": php_code,
                "migration": migration,
                "audit": audit,
                "security": security,
                "tests": tests,
                "docs": docs,
                "extract_file": extract_file,
                "integration": integration_log,
                "base_path": base_path
            }, filename=zip_file.name if zip_file else None)

            st.success("✅ Migration pipeline completed")
            st.session_state["selected_history"] = file_key
            st.session_state["show_history"] = True

            st.markdown("---")
            st.subheader("📦 Export Migrated Project")

            include_docs = st.checkbox("Include documentation", value=True)
            include_logs = st.checkbox("Include integration logs", value=True)

            if base_path and os.path.exists(base_path):
                if st.button("💾 Generate ZIP"):
                    # Use the folder name as the zip file name
                    export_name = f"nextjs-export-{os.path.basename(base_path)}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                    zip_path = export_project(base_path, export_name)

                    file_tree = list_directory_files(base_path)
                    st.markdown("#### 📁 Files to be included:")
                    for file in file_tree:
                        st.text(f"- {file}")

                    with open(zip_path, "rb") as f:
                        st.download_button("⬇️ Download ZIP", f, file_name=os.path.basename(zip_path))
                    st.success("✅ Export ready for download!")
            else:
                st.error("❌ Error: Migrated project path not found. Integration step may have failed.")

# === Display Saved History + Export ===
if st.session_state.get("show_history") and "selected_history" in st.session_state:
    data = load_history(st.session_state["selected_history"])

    tabs_output = st.tabs(["🧹 Migrated Code", "📊 Audit", "🔐 Security", "✅ Tests", "📑 Docs", "🗂️ Extracted File", "⚙️ Integration Log"])

    with tabs_output[0]:
        display_section("Migrated Code", data["migration"], language="markdown")
    with tabs_output[1]:
        display_section("Audit", data["audit"], language="markdown")
    with tabs_output[2]:
        display_section("Security", data["security"], language="markdown")
    with tabs_output[3]:
        display_section("Tests", data["tests"], language="markdown")
    with tabs_output[4]:
        display_section("Documentation", data["docs"], display_type="markdown")
    with tabs_output[5]:
        display_section("Extracted File", data["extract_file"], display_type="markdown")
    with tabs_output[6]:
        display_section("Integration Log", data["integration"], display_type="markdown")

    # === Export Section at the End ===
    st.markdown("---")
    st.subheader("📦 Export Migrated Project")

    include_docs = st.checkbox("Include documentation", value=True, key="history_docs")
    include_logs = st.checkbox("Include integration logs", value=True, key="history_logs")

    if data.get("base_path") and os.path.exists(data["base_path"]):
        if st.button("💾 Generate ZIP (History)"):
            # Use the folder name as the zip file name
            export_name = f"nextjs-history-export-{os.path.basename(data['base_path'])}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            zip_path = export_project(data["base_path"], export_name)

            file_tree = list_directory_files(data["base_path"])
            st.markdown("#### 📁 Files to be included:")
            for file in file_tree:
                st.text(f"- {file}")

            with open(zip_path, "rb") as f:
                st.download_button("⬇️ Download ZIP", f, file_name=os.path.basename(zip_path))
            st.success("✅ ZIP from history ready for download!")
    else:
        st.error("❌ Error: No valid exported path found in history.")
