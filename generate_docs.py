import os
import glob
import re
import yaml
def extract_block(content, block_name):
    pattern = r"{}\s*=\s*r?'''(.*?)'''".format(block_name)
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1)
    
    pattern = r'{}\s*=\s*r?"""(.*?)"""'.format(block_name)
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1)
        
    return None
def main():
    docs_dir = 'docs'
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
    dirs_to_scan = [
        ('plugins/modules', 'Module'),
        ('plugins/lookup', 'Lookup Plugin'),
        ('plugins/inventory', 'Inventory Plugin')
    ]
    
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)

    for source_dir, plugin_type in dirs_to_scan:
        for filepath in glob.glob(os.path.join(source_dir, '*.py')):
            filename = os.path.basename(filepath)
            module_name = os.path.splitext(filename)[0]
            if module_name == '__init__':
                continue
            
            with open(filepath, 'r') as f:
                content = f.read()
            
            doc_yaml_str = extract_block(content, 'DOCUMENTATION')
            examples_str = extract_block(content, 'EXAMPLES')
            return_str = extract_block(content, 'RETURN')
            
            if not doc_yaml_str:
                print(f"Skipping {module_name}: No DOCUMENTATION found.")
                continue
            
            try:
                doc = yaml.safe_load(doc_yaml_str)
            except yaml.YAMLError as e:
                print(f"Error parsing YAML for {module_name}: {e}")
                continue
            
            md_content = f"# {module_name} ({plugin_type})\n\n"
            md_content += f"{doc.get('short_description', 'No description')}\n\n"
            
            description = doc.get('description', [])
            if isinstance(description, list):
                md_content += "\n".join([str(x) for x in description]) + "\n\n"
            else:
                md_content += str(description) + "\n\n"
            
            md_content += "## Parameters\n\n"
            options = doc.get('options', {})
            if options:
                md_content += "| Parameter | Required | Default | Choices | Description |\n"
                md_content += "|---|---|---|---|---|\n"
                for opt_name, opt_data in options.items():
                    required = opt_data.get('required', False)
                    default = opt_data.get('default', '')
                    choices = opt_data.get('choices', '')
                    desc = opt_data.get('description', [])
                    if isinstance(desc, list):
                        desc = " ".join([str(x) for x in desc])
                    desc = desc.replace("\n", " ")
                    md_content += f"| `{opt_name}` | {required} | {default} | {choices} | {desc} |\n"
            else:
                md_content += "No parameters.\n"
            
            md_content += "\n## Examples\n\n"
            if examples_str:
                md_content += "```yaml\n"
                md_content += examples_str.strip() + "\n"
                md_content += "```\n\n"
            else:
                md_content += "No examples found.\n\n"
            
            md_content += "## Return Values\n\n"
            if return_str:
                 md_content += "```yaml\n"
                 md_content += return_str.strip() + "\n"
                 md_content += "```\n"
            
            if 'Lookup' in plugin_type:
                 output_filename = f"{module_name}_lookup.md"
            else:
                 output_filename = f"{module_name}.md"
            
            output_path = os.path.join(docs_dir, output_filename)
            with open(output_path, 'w') as f:
                f.write(md_content)
            print(f"Generated {output_path}")
if __name__ == "__main__":
    main()
