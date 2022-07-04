from PyDoc import pydoc, pydoc_runner

# Single file processing
pydoc(r"demo/single_file/example.py", r"demo/single_file/example.html")

# Directory processing
pydoc_runner(
    root_src=r"demo/directory",
    root_doc=r"demo/doc"
)
