# Deploying TMA Magic to Streamlit Community Cloud

This folder is configured for instant deployment to Streamlit Community Cloud.

## 🚀 Deployment Steps

### 1. Create a New Repository
1. Go to [GitHub](https://github.com/new).
2. Create a **new public repository** (e.g., `tma-magic-app`).
3. Leave it empty (no README/gitignore).

### 2. Push Code
Open your terminal in this folder (`TMA Project`) and run:
```bash
git init
git add .
git commit -m "Initial commit for Cloud Deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/tma-magic-app.git
git push -u origin main
```

### 3. Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/).
2. Click **"New App"**.
3. Select your new repository (`tma-magic-app`).
4. **Main file path:** `app.py`
5. Click **"Deploy!"**.

### 4. Configure Secrets (Important!)
Your API Key must be set in the cloud dashboard, NOT in code.
1. On your app dashboard, click **Manage App** (bottom right) -> **Settings** (dots) -> **Secrets**.
2. Paste this TOML configuration:
```toml
[general]
openai_api_key = "sk-..."
```
3. Save.

## 🔐 Authentication (New!)
The app now includes a built-in Sign Up / Sign In system.

### **Default Admin Credentials**
- **Username:** `admin`
- **Password:** `abc`

> **Note:** On Streamlit Community Cloud (free tier), new user registrations are **ephemeral**. If the app goes to sleep or restarts, the user list may reset to the default `auth_config.yaml`. For permanent user storage, a database connection would be required.

## ⚠️ Known Limits
- **Storage:** Files uploaded or generated are **temporary**. They will disappear if the app restarts.
- **Memory:** 1GB Limit. Large PDFs (>50MB) may crash the worker.
- **Timeout:** Processing jobs longer than 10-15 minutes may be terminated.

## 🛠 Project Structure
- `app.py`: Frontend UI
- `backend_processor.py`: Background worker (subprocess)
- `packages.txt`: System installs (poppler for PDFs)
- `requirements.txt`: Python libraries
