import json
import os
import re
import shutil
from datetime import datetime
from glob import glob


def copy_folder(source_path, new_name, destination_path=None, replace=False):
    if destination_path is None:
        destination_path = os.path.dirname(source_path)

    new_path = os.path.join(destination_path, new_name)

    try:
        if replace and os.path.exists(new_path):
            shutil.rmtree(new_path)
            print(f"Removed existing folder: '{new_path}'")

        shutil.copytree(source_path, new_path)
        print(f"Successfully copied '{source_path}' to '{new_path}'")
    except FileNotFoundError:
        print(f"Error: Source folder '{source_path}' not found")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def is_kaggle_path_regex(file_path):
    return bool(re.search(r"kaggle", file_path, re.IGNORECASE))


def update_notebook_sections(
    notebook_path,
    general_announcement,
    installation_steps,
    installation_steps_kaggle,
    new_announcement,
):
    try:
        with open(notebook_path, "r", encoding="utf-8") as f:
            notebook_content = json.load(f)

        updated = False
        i = 0
        while i < len(notebook_content["cells"]):
            cell = notebook_content["cells"][i]

            if cell["cell_type"] == "markdown":
                source_str = "".join(cell["source"]).strip()

                if source_str == "# General":
                    if (
                        i + 1 < len(notebook_content["cells"])
                        and notebook_content["cells"][i + 1]["cell_type"] == "markdown"
                    ):
                        notebook_content["cells"][i + 1]["source"] = [
                            f"{line}\n" for line in general_announcement.splitlines()
                        ]
                        updated = True
                        i += 1
                elif source_str == "# News":
                    if (
                        i + 1 < len(notebook_content["cells"])
                        and notebook_content["cells"][i + 1]["cell_type"] == "markdown"
                    ):
                        notebook_content["cells"][i + 1]["source"] = [
                            f"{line}\n" for line in new_announcement.splitlines()
                        ]
                        updated = True
                        i += 1
                elif source_str == "# Installation":
                    if (
                        i + 1 < len(notebook_content["cells"])
                        and notebook_content["cells"][i + 1]["cell_type"] == "code"
                    ):
                        if is_kaggle_path_regex(notebook_path):
                            notebook_content["cells"][i + 1]["source"] = [
                                f"{line}\n"
                                for line in installation_steps_kaggle.splitlines()
                            ]
                        else:
                            notebook_content["cells"][i + 1]["source"] = [
                                f"{line}\n" for line in installation_steps.splitlines()
                            ]
                        updated = True
                        i += 1

            i += 1

        # Ensure GPU metadata is set
        if "metadata" not in notebook_content:
            notebook_content["metadata"] = {}
        if "accelerator" not in notebook_content["metadata"]:
            notebook_content["metadata"]["accelerator"] = "GPU"
            updated = True
        if "colab" not in notebook_content["metadata"]:
            notebook_content["metadata"]["colab"] = {"provenance": []}
            updated = True
        if "kernelspec" not in notebook_content["metadata"]:
            notebook_content["metadata"]["kernelspec"] = {
                "display_name": "Python 3",
                "name": "python3",
            }
            updated = True

        if updated:
            with open(notebook_path, "w", encoding="utf-8") as f:
                json.dump(notebook_content, f, indent=1)
            print(f"Updated: {notebook_path}")
        else:
            print(f"No sections found to update in: {notebook_path}")

    except FileNotFoundError:
        print(f"Error: Notebook not found at {notebook_path}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in notebook at {notebook_path}")
    except Exception as e:
        print(f"An unexpected error occurred while processing {notebook_path}: {e}")


def main():
    general_announcement_content = """To run this, press "*Runtime*" and press "*Run all*" on a **free** Tesla T4 Google Colab instance!
<div class="align-center">
  <a href="https://github.com/unslothai/unsloth"><img src="https://github.com/unslothai/unsloth/raw/main/images/unsloth%20new%20logo.png" width="115"></a>
  <a href="https://discord.gg/unsloth"><img src="https://github.com/unslothai/unsloth/raw/main/images/Discord button.png" width="145"></a>
  <a href="https://docs.unsloth.ai/"><img src="https://github.com/unslothai/unsloth/blob/main/images/documentation%20green%20button.png?raw=true" width="125"></a></a> Join Discord if you need help + ⭐ <i>Star us on <a href="https://github.com/unslothai/unsloth">Github</a> </i> ⭐
</div>

To install Unsloth on your own computer, follow the installation instructions on our Github page [here](https://github.com/unslothai/unsloth?tab=readme-ov-file#-installation-instructions).

**[NEW] As of Novemeber 2024, Unsloth now supports vision finetuning!**

You will learn how to do [data prep](#Data), how to [train](#Train), how to [run the model](#Inference), & [how to save it](#Save)"""

    installation_content = """%%capture
!pip install unsloth
# Also get the latest nightly Unsloth!
!pip uninstall unsloth -y && pip install --upgrade --no-cache-dir --no-deps git+https://github.com/unslothai/unsloth.git
"""

    installation_kaggle_content = """%%capture
# Install kaggle
!pip install unsloth
# Also get the latest nightly Unsloth!
!pip uninstall unsloth -y && pip install --upgrade --no-cache-dir --no-deps git+https://github.com/unslothai/unsloth.git
"""

    new_announcement_content = """* We support Llama 3.2 Vision 11B, 90B; Pixtral; Qwen2VL 2B, 7B, 72B; and any Llava variant like Llava NeXT!
* We support 16bit LoRA via `load_in_4bit=False` or 4bit QLoRA. Both are accelerated and use much less memory!
"""

    notebook_directory = "notebooks"
    notebook_pattern = "*.ipynb"

    notebook_files = glob(os.path.join(notebook_directory, "*", notebook_pattern))

    if not notebook_files:
        print(
            f"No notebooks found in the directory: {notebook_directory} with pattern: {notebook_pattern}"
        )
        return

    for notebook_file in notebook_files:
        update_notebook_sections(
            notebook_file,
            general_announcement_content,
            installation_content,
            installation_kaggle_content,
            new_announcement_content,
        )


def update_readme(readme_path, notebooks_dir):
    base_url_colab = (
        "https://colab.research.google.com/github/unslothai/notebooks/blob/main/"
    )
    base_url_kaggle = "https://www.kaggle.com/notebooks/welcome?src=https://github.com/unslothai/notebooks/blob/main/"

    paths = glob(os.path.join(notebooks_dir, "*", "*.ipynb"))

    sections = {}  # Dynamically create sections based on subfolders

    table_header = "| Notebook | Link |\n| --- | --- |\n"

    for path in paths:
        notebook_name = os.path.basename(path)
        section_name = os.path.basename(os.path.dirname(path))

        # Create section if it doesn't exist
        if section_name not in sections:
            sections[section_name] = {
                "header": f"## {section_name} Notebooks\n",
                "rows": "",
            }

        if section_name == "Kaggle":
            notebook_link = base_url_kaggle + path + "&accelerator=nvidiaTeslaT4"
            sections[section_name]["rows"] += (
                f"| {notebook_name} | [Open in Kaggle]({notebook_link}) |\n"
            )
        else:
            notebook_link = base_url_colab + path
            sections[section_name]["rows"] += (
                f"| {notebook_name} | [Open in Colab]({notebook_link}) |\n"
            )

    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()

        # Sort sections alphabetically
        sorted_sections = dict(sorted(sections.items()))

        # Find the start and end of the "Notebooks Links" section
        start_marker = "# Notebooks Links"
        start_index = readme_content.find(start_marker)
        if start_index == -1:
            raise ValueError("Start marker '# Notebooks Links' not found in README.")
        start_index += len(start_marker)

        end_marker = "<!-- End of Notebook Links -->"
        end_index = readme_content.find(end_marker)
        if end_index == -1:
            raise ValueError(
                "End marker '<!-- End of Notebook Links -->' not found in README."
            )

        # Extract the content before and after the "Notebooks Links" section
        content_before = readme_content[:start_index]
        content_after = readme_content[end_index:]

        # Construct the updated "Notebooks Links" section
        updated_notebooks_links = ""
        for section_name, section_data in sorted_sections.items():
            updated_notebooks_links += (
                section_data["header"] + table_header + section_data["rows"]
            )

        # Add the "Last updated" timestamp
        timestamp = f"<!-- Last updated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->\n"

        # Combine all the parts
        updated_readme_content = (
            content_before + "\n" + updated_notebooks_links + timestamp + content_after
        )

        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(updated_readme_content)

        print(f"Successfully updated {readme_path}")

    except FileNotFoundError:
        print(f"Error: {readme_path} not found.")
    except Exception as e:
        print(f"An error occurred while updating {readme_path}: {e}")


if __name__ == "__main__":
    copy_folder("original_template", "notebooks", replace=True)
    main()

    notebook_directory = "notebooks"
    readme_path = "README.md"
    update_readme(readme_path, notebook_directory)
