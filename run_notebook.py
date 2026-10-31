"""
Script untuk mengeksekusi notebook.ipynb menggunakan nbclient.
Dijalankan dari direktori proyek.
"""
import os
import sys
import nbformat
import nbclient

os.chdir(os.path.dirname(os.path.abspath(__file__)))
print("Working dir:", os.getcwd())

# Baca notebook
with open("notebook.ipynb", "r", encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

print(f"Notebook loaded: {len(nb.cells)} cells")

# Eksekusi
client = nbclient.NotebookClient(
    nb,
    timeout=600,
    kernel_name="python3",
    resources={"metadata": {"path": os.getcwd()}},
)

print("Executing notebook... (may take 1-3 minutes)")
try:
    client.execute()
    print("Execution COMPLETE - no errors!")
except nbclient.exceptions.CellExecutionError as e:
    print(f"Cell execution error: {e}")
    print("Saving partial results anyway...")
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    print("Saving partial results anyway...")

# Simpan
with open("notebook.ipynb", "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print("Notebook saved with outputs.")
