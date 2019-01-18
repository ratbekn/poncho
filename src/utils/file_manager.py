def save_content_to_file(content, file_name):  # pragma: no cover
    with open(file_name, "w") as f:
        f.writelines(content)
