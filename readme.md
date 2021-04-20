## Table of contents
* [General info](#general-info)
* [Usage](#usage)

## General info
This Tool is to export your AWS Organizations structure, SCPs to Json file and import structure, SCPs to another AWS Organization. During import and export a a log file is written so that the processes can be traced

![Example](static/orgtoolicon.jpeg)

## Tool info:
|Version |Author  | 
--- | --- |
|1.0 | David Krohn </br> [Linkedin](https://www.linkedin.com/in/daknhh/) - [Blog](https://globaldatanet.com/blog/author/david-krohn)|


## Usage

### Structure:
#### Export: `orgtool.py -u export -f <file.json> -p AWSPROFILE `

#### Import: `orgtool.py -u import -f <file.json> -p AWSPROFILE `
### SCPs:
#### Export: `orgtool.py -u export-scps -f <file.json> -p AWSPROFILE`

#### Import: `orgtool.py -u import-scps -f <file.json> -p AWSPROFILE`

#### Attach-SCPs: `orgtool.py -u attach-scps -f <file.json> -p AWSPROFILE`
#### Validate-SCPs: `orgtool.py -u validate-scps -f <file.json> -p AWSPROFILE` 
ℹ️ Uses Access Analyzer policy validation to validates your SCPs against IAM [policy grammar](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_grammar.html) and [best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html). 

### Visualization:
#### Visualize Organization with graphviz: `orgtool.py -u visualize-organization-graphviz -f <file.json> -p AWSPROFILE`

ℹ️ Visualize Organization currently use [Graphviz](https://www.graphviz.org/download/) please install before using the function.

![Example Output](static/visualize-organization-example-graphviz.png)

#### Visualize Organization with diagrams.net: `orgtool.py -u visualize-organization-diagrams -f <file.json> -p AWSPROFILE`

ℹ️  The tool will generate a organziations.csv file.
Follow the guide to [import from CSV to draw.io diagrams](https://drawio-app.com/import-from-csv-to-drawio/)

![Example Output](static/visualize-organization-example-diagrams.png)
### How to use the tool with virtual env:

1. Creating virtual env: 
`python3 -m venv orgtool`

2. Activate virtual env:
`source orgtool/bin/activate`