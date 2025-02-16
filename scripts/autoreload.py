import importlib
import sys
import os
import time

try:
    from IPython import get_ipython
    ipython = get_ipython()
except ImportError:
    ipython = None  # Not running in an interactive IPython environment

last_reload_times = {}

def reload_scripts(*args, **kwargs):  # No script_dir as a parameter
    """
    Dynamically reloads all Python modules in the `scripts/` directory,
    but only if they were modified since the last reload.

    This function ensures that changes to scripts are picked up in interactive environments like Jupyter, 
    Colab, and VS Code Jupyter extension, without affecting standalone Python execution.

    Usage:
        from scripts import autoreload
        autoreload.reload_scripts()
    """
    script_dir = "scripts"  # Ensure script_dir is always correctly set
    script_path = os.path.abspath(script_dir)

    # Ensure `scripts/` is in sys.path
    if script_path not in sys.path:
        sys.path.append(script_path)

    # print(f"📂 Reloading scripts from: {script_path}")

    reloaded_modules = []
    global last_reload_times

    for filename in os.listdir(script_path):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"scripts.{filename[:-3]}"  # Convert filename to module name
            module_path = os.path.join(script_path, filename)
            last_modified = os.path.getmtime(module_path)

            # Check if the file has been modified since the last reload
            if module_name in last_reload_times and last_reload_times[module_name] >= last_modified:
                continue  # Skip if no changes

            try:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])  # Reload module
                    reloaded_modules.append(module_name)
                    last_reload_times[module_name] = time.time()  # Update last reload time
            except Exception as e:
                print(f"❌ Failed to reload {module_name}: {e}")

    # if reloaded_modules:
    #     print(f"✅ Reloaded {len(reloaded_modules)} modules:", ", ".join(reloaded_modules))
    # else:
    #     print("⏳ No scripts changed, skipping reload.")

# Enable autoreload **only if running inside an IPython environment**
if ipython:
    ipython.events.register("pre_run_cell", reload_scripts)  # No argument needed
    print("🔄 Auto-reloading enabled for scripts/. Only modified scripts will be reloaded.")
else:
    print("⚠ Not running in an interactive IPython environment. Autoreload is disabled.")
