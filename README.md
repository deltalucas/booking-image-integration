# Booking.com Image Gathering and Integration into TraffickCam

This directory contains the code to gather data from every hotel in the United States from Booking.com. The data includes hotel name, gps coordinates, hotel address (including city, state, etc.), rating, and all the links to the hotel's images. The directory also contains code to download all the images from the links gathered onto the server. The ultimate goal of this project is to integrate all the images of booking.com hotels into the existing TraffickCam hotel image corpus.

- ✅ **Jupyter Notebook Server (GPU3)**
- ✅ **Local Code Editors (VS Code, PyCharm, etc.)**
- ✅ **Google Colab**

Whether you are working on **data preprocessing, model training, or evaluation**, this template provides a structured workflow to streamline your ML experiments.  

---

## 📂 Project Structure  
Here's a quick breakdown of the repository contents:

| **File / Directory** | **Purpose** |
|----------------------|-------------|
| `main.ipynb` | 📓 The main Jupyter Notebook for running experiments and prototyping ML code. |
| `README.md` | 📄 Documentation for understanding and using this template. |
| `.gitignore` | 🚫 Ensures that large files, logs, and unnecessary cache files are not committed to Git. |
| `requirements.txt` | 📦 Lists all required dependencies (for `pip install -r requirements.txt`). |
| `scripts/` | 🛠 Contains reusable Python scripts for preprocessing, training, and evaluation. |
| `results/` | 📊 Stores logs, metrics, and experiment outputs. |
| `models/` | 🏗 Stores trained models and checkpoints. |
| `data/` | 📁 Placeholder for datasets (**already in `.gitignore`**, so any datasets added here won’t be committed to Git). |


---

## 🚀 Getting Started  

### 🔹 **1. Clone the Repository**
```bash
git clone https://github.com/your-org/ml-project-template.git
cd ml-project-template
```

### 🛠 Setting Up the Dataset (GPU Server)
To avoid hardcoding dataset paths, create a **symbolic link** inside `data/` pointing to your dataset location:

```bash
ln -s /absolute/path/to/dataset /path/to/ml-project-template/data/dataset_name
```

| **Where You're Running the Notebook** | **Dataset Setup** |
|--------------------------------------|------------------|
| **GPU Server (Jupyter Notebook Server)** | Use a **symlink** (`ln -s`) to point to the real dataset. |
| **Local Machine (VS Code, Jupyter, etc.)** | Create a **small sample dataset** inside `data/`. |
| **Google Colab (Cloud)** | Upload a sample dataset to **Google Drive** inside `data/`. |
