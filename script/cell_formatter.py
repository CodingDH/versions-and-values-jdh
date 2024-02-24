import json
import nbformat
import os
import re
from typing import List, Union

def anonymize_notebook(notebook_filename: str):
    """
    Anonymize a notebook by replacing author names with "Author1" and "Author2"

    Parameters
    ----------
    notebook_filename : str
        The filename of the notebook to anonymize
    
    """
    # Load the notebook
    with open(notebook_filename, "r") as file:
        notebook = nbformat.read(file, as_version=4)

    # Regular expressions for matching
    patterns = {
        r"\.\s*LeBlanc and Wieringa": ". The Authors",
        r"\.\s*Wieringa and LeBlanc": ". The Authors",
        "LeBlanc and Wieringa": "the authors",
        "Wieringa and LeBlanc": "the authors",
        "LeBlanc": "Author1",
        "Wieringa": "Author2"
    }

    # Iterate through each cell
    for cell in notebook.cells:
        if cell.cell_type == "markdown" or cell.cell_type == "code":
            for pattern, replacement in patterns.items():
                cell.source = re.sub(pattern, replacement, cell.source)

    # Save the anonymized notebook
    with open(notebook_filename, 'w') as file:
        nbformat.write(notebook, file)

# Function to load source descriptions from a JSON file
def load_source_descriptions(filename: str) -> List:
    """
    Load source descriptions from a JSON file

    Parameters
    ----------
    filename : str
        The filename of the JSON file to load
    
    Returns
    -------
    list
        A list of source descriptions, with types and tags
    """
    with open(filename, 'r') as file:
        return json.load(file)

# Function to check if a tag matches any of the source description keys
def tag_matches_sources(tag: str, cells: List) -> dict or None:
    """
    Check if a tag matches any of the source description keys

    Parameters
    ----------
    tag : str
        The tag to check
    cells : list
        A list of source descriptions, with types and tags
    
    Returns
    -------
    dict
        The source description that matches the tag, or None if no match
    """
    for cell in cells:
        # Create a regular expression pattern from the source tag
        # Replace '*' with '.*' to match any character(s)
        pattern = '^' + re.escape(cell["tag"]).replace("\\*", ".*") + '$'
        if re.match(pattern, tag):
            return cell
    return None

# Function to add metadata to cells with specific tags
def add_metadata_to_notebook(notebook_filename: str, sources: List):
    """
    Add metadata to cells with specific tags

    Parameters
    ----------
    notebook_filename : str
        The filename of the notebook to add metadata to
    sources : list
        A list of source descriptions, with types and tags
    """
    # Load the notebook
    with open(notebook_filename, 'r') as file:
        notebook = nbformat.read(file, as_version=4)

    # Iterate through each cell
    for cell in notebook.cells:
        if 'metadata' in cell and 'tags' in cell['metadata']:
            for tag in cell['metadata']['tags']:
                # Check if the tag matches any in our sources
                matching_source = tag_matches_sources(tag, sources)
                if matching_source:
                    # Add or update the 'jdh' metadata
                    cell['metadata']['jdh'] = {
                        "object": {
                            "source": matching_source["source"]
                        }
                    }
                    if "type" in matching_source:
                        cell['metadata']['jdh']['object']['type'] = matching_source["type"]
                        cell['metadata']['jdh']["module"] = "object"

    # Save the updated notebook
    with open(notebook_filename, 'w') as file:
        nbformat.write(notebook, file)


# Function to find all cells with tags containing the word "figure"
def find_figure_cells(notebook_filename: str, output_filename: str, rerun_code: bool = False) -> List[dict] or None:
    """
    Find all cells with tags containing the word "figure"

    Parameters
    ----------
    notebook_filename : str
        The filename of the notebook to find figure cells in
    output_filename : str
        The filename of the JSON file to save the figure cells to
    rerun_code : bool
        Whether to rerun the code to find figure cells, or load from the JSON file
    
    Returns
    -------
    list
        A list of figure cells, with cell index, tag, and source
    """
    if os.path.exists(output_filename) or rerun_code:
        figure_cells = load_source_descriptions(output_filename)
    else:
        # Load the notebook
        with open(notebook_filename, 'r') as file:
            notebook = nbformat.read(file, as_version=4)

        figure_cells = []
        
        # Iterate through each cell
        for cell_index, cell in enumerate(notebook.cells):
            if 'metadata' in cell and 'tags' in cell['metadata']:
                for tag in cell['metadata']['tags']:
                    if ('figure' in tag) or ('table' in tag) or ('cover' in tag):
                        # Add cell index and tag to the list
                        figure_cells.append({"cell_index": cell_index, "tag": tag, "source": []})

        # Save the figure cells list to a JSON file
        with open(output_filename, 'w') as outfile:
            json.dump(figure_cells, outfile, indent=4)
    return figure_cells

if __name__ == '__main__':


    """Example usage
    "metadata": {
        "jdh": {
            "object": {
                "source": [
                    "This graph illustrates the frequency of 'Tool' in quotes from whatisdigitalhumanities.com and Day of DH."
                ]
            }
        },
        "tags": [
        "figure-whatisdh-tools-*",
        "narrative",
        "hermeneutics"
        ]
    }
    """
    #Example usage for adding metadata to article-text.ipynb
    # Generate lists of cells that need sources based on tags
    rerun_code = False
    figure_cells = find_figure_cells('../article-text.ipynb', 'data/jsons/figure_cells.json', rerun_code)
    # Once manually added sources, add metadata to cells
    add_metadata_to_notebook('../article-text.ipynb', figure_cells)
    # add_metadata_to_notebook('../article-text-partial-anonymous.ipynb', figure_cells)
    
    #Example usage for anonymizing article-text.ipynb
    ## Generate lists of cells that need sources based on tags
    figure_cells = find_figure_cells('../article-text-fully-anonymized.ipynb', 'data/jsons/figure_cells_anonymized.json', rerun_code)
    # Once manually added sources, add metadata to cells
    add_metadata_to_notebook('../article-text-fully-anonymized.ipynb', figure_cells)
    ## Anonymize the notebook
    anonymize_notebook('../article-text-fully-anonymized.ipynb')