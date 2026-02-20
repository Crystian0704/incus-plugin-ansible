
import os
import ast
import yaml
import glob
import re

def extract_doc_yaml(content):
    match = re.search(r'DOCUMENTATION\s*=\s*r?(\'\'\'|""")(.*?)(\1)', content, re.DOTALL)
    if match:
        return match.group(2)
    return None

def extract_examples(content):
    match = re.search(r'EXAMPLES\s*=\s*r?(\'\'\'|""")(.*?)(\1)', content, re.DOTALL)
    if match:
        return match.group(2)
    return None

def extract_argument_spec(content):
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'AnsibleModule':
                for keyword in node.keywords:
                    if keyword.arg == 'argument_spec':
                        if isinstance(keyword.value, ast.Call) and isinstance(keyword.value.func, ast.Name) and keyword.value.func.id == 'dict':
                            # Handle dict(...) constructor
                            args = {}
                            for k in keyword.value.keywords:
                                # Extract parameter definition if it's a dict(...) call
                                param_def = {}
                                if isinstance(k.value, ast.Call) and isinstance(k.value.func, ast.Name) and k.value.func.id == 'dict':
                                    for pk in k.value.keywords:
                                        # We are interested in 'required' which is usually a boolean literal
                                        if pk.arg == 'required':
                                            if isinstance(pk.value, ast.Constant): # Python 3.8+
                                                param_def['required'] = pk.value.value
                                            elif isinstance(pk.value, ast.NameConstant): # Python < 3.8
                                                param_def['required'] = pk.value.value
                                args[k.arg] = param_def
                            return args
                        elif isinstance(keyword.value, ast.Dict):
                            # Handle {...} literal
                            return ast.literal_eval(keyword.value)
                        return {}
    except Exception as e:
        print(f"Error extracting argument_spec: {e}")
    return {}

def audit_module(filepath):
    print(f"Auditing {filepath}...")
    with open(filepath, 'r') as f:
        content = f.read()

    doc_yaml = extract_doc_yaml(content)
    if not doc_yaml:
        print(f"  [ERROR] No DOCUMENTATION found.")
        return False

    try:
        doc = yaml.safe_load(doc_yaml)
    except yaml.YAMLError as e:
        print(f"  [ERROR] YAML parse error: {e}")
        return False

    arg_spec = extract_argument_spec(content)
    if not arg_spec:
        print(f"  [WARNING] Could not extract argument_spec (or it is empty).")

    doc_options = doc.get('options', {})
    
    errors = []

    for param in arg_spec:
        if param not in doc_options:
            errors.append(f"Parameter '{param}' in argument_spec but MISSING in DOCUMENTATION.")
    
    for param in doc_options:
        if param not in arg_spec:
             errors.append(f"Parameter '{param}' in DOCUMENTATION but MISSING in argument_spec.")

    if 'name' in arg_spec and 'instance_name' in arg_spec:
         pass # Both might be valid, but check if they are mutually exclusive or aliases
    
    if 'name' in doc_options and 'instance_name' in doc_options:
         pass

    examples = extract_examples(content)
    if not examples:
        errors.append("No EXAMPLES found.")
    else:
        for param in arg_spec:
            if arg_spec[param].get('required', False) and param not in examples:
                 pass

    if errors:
        for err in errors:
            print(f"  [FAIL] {err}")
        return False
    else:
        print(f"  [OK]")
        return True

def main():
    modules_dir = 'plugins/modules'
    for filepath in glob.glob(os.path.join(modules_dir, '*.py')):
        if '__init__' in filepath:
            continue
        audit_module(filepath)

if __name__ == "__main__":
    main()
