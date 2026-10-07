"""Execute the portfolio notebook using this Python environment."""
import os
import sys
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpec
from .data_processing import PROJECT_ROOT


def execute_notebook() -> None:
    path = PROJECT_ROOT / "notebooks" / "employee_training_causal_analysis.ipynb"
    runtime = PROJECT_ROOT / ".jupyter-runtime"
    runtime.mkdir(exist_ok=True)
    os.environ["JUPYTER_RUNTIME_DIR"] = str(runtime)
    notebook = nbformat.read(path, as_version=4)
    manager = KernelManager(kernel_name="python3")
    # Use the current interpreter without a global kernelspec installation.
    manager._kernel_spec = KernelSpec(argv=[sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
                                      display_name="Project Python", language="python")
    client = NotebookClient(notebook, timeout=300, km=manager,
                            resources={"metadata": {"path": str(PROJECT_ROOT / "notebooks")}})
    client.execute()
    nbformat.validate(notebook)
    nbformat.write(notebook, path)
    code_cells = [c for c in notebook.cells if c.cell_type == "code"]
    if any(o.output_type == "error" for c in code_cells for o in c.outputs):
        raise RuntimeError("Notebook contains error outputs.")
    print(f"Executed {len(code_cells)} code cells with no errors: {path.name}")


if __name__ == "__main__":
    execute_notebook()
