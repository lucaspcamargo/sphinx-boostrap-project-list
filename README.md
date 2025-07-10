# Sphinx Bootstrap Project List

A tool for generating a Bootstrap-themed list of projects by consuming JSON data and rendering it through a customizable template.

## About

This project takes a JSON data source describing multiple projects and generates an OK-looking, Bootstrap-styled HTML list. This is what powers the project lists of my site. Talk about meta stuff.

## Features

- **JSON Data Source**: Specify the path or URL to your JSON file containing project information.
- **Images**: Meant to be used with images. Falls back to a global placeholder if not provided.
- **Internal or External Links**: Add external links or resources to each project entry.
- **Text Fallback**: Fallback to a list of links on non-HTML output.

Configuration is typically managed via a JSON file and template files. See the project documentation for setup and customization details.

## Usage

To use the Sphinx Bootstrap Project List, add the following directive to your reStructuredText file:

```rst
.. bspl::
    :json: projects.json
```

More options to come, patches welcome always.

### Example JSON File

Below is an example `projects.json` file. The JSON is a dictionary where each key is a project ID, and the value is the project data:

```json
{
  "alpha": {
    "nice_title": "Project Alpha",
    "descr": "A sample project for demonstration.",
    "index_path": "https://github.com/example/project-alpha",
    "last_mod": "2025-08-03T03:41:52Z",
    "last_mod_fmt": "August 03, 2025",
  },
  "beta": {
    "nice_title": "Beta Tool",
    "descr": "Another example project.",
    "index_path": "projects/beta.md",   
    "image_path": "projects/beta_logo.png",
    "last_mod": "2025-07-15T14:22:10Z",
    "last_mod_fmt": "July 15, 2025",
  }
}
```

Paths are relative to the json file location, unless absolute. Can be a reference to another document, or a full url as well.

## Configuration

To configure the Sphinx Bootstrap Project List extension in your `conf.py`, add the following settings (with a default image):

```python
bspl_default_image = '_static/default_project_image.png_'
```

- `bspl_default_image`: URL or path to a default image for projects without a specified image.

More options to come in the future, patches always welcome.

## License

This project is licensed under the GPL v3 License. See the [LICENSE](LICENSE) file for details.