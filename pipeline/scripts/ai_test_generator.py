"""
AI-powered test generation for Databricks notebooks.
Uses Azure OpenAI to analyze notebook code patterns and generate pytest/unittest cases.
"""

import os
import json
import glob
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Azure OpenAI imports
from openai import AzureOpenAI


class NotebookTestGenerator:
    """Generates tests for Databricks notebooks using Azure OpenAI."""

    def __init__(self, azure_endpoint: str, api_key: str, api_version: str = "2024-02-15-preview"):
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")

    def parse_notebook(self, notebook_path: str) -> Dict[str, Any]:
        """Parse a Jupyter notebook and extract code cells."""
        with open(notebook_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Handle both JSON and VSCode XML-style notebooks
        if content.strip().startswith('{'):
            notebook = json.loads(content)
            cells = []
            for cell in notebook.get('cells', []):
                if cell.get('cell_type') == 'code':
                    source = ''.join(cell.get('source', []))
                    cells.append({
                        'type': 'code',
                        'source': source
                    })
            return {'cells': cells, 'path': notebook_path}
        else:
            # VSCode XML-style format
            import re
            cells = []
            pattern = r'<VSCode\.Cell[^>]*language="python"[^>]*>(.*?)</VSCode\.Cell>'
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                cells.append({
                    'type': 'code',
                    'source': match.strip()
                })
            return {'cells': cells, 'path': notebook_path}

    def extract_functions(self, notebook_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract function definitions from notebook cells."""
        import re
        functions = []
        
        for cell in notebook_data.get('cells', []):
            source = cell.get('source', '')
            # Find function definitions
            func_pattern = r'def\s+(\w+)\s*\([^)]*\).*?(?=\ndef\s|\nclass\s|\Z)'
            matches = re.findall(func_pattern, source, re.DOTALL)
            
            # Also extract full function with body
            full_func_pattern = r'(def\s+\w+\s*\([^)]*\):.*?)(?=\ndef\s|\nclass\s|\Z)'
            full_matches = re.findall(full_func_pattern, source, re.DOTALL)
            
            for i, name in enumerate(matches):
                functions.append({
                    'name': name,
                    'code': full_matches[i] if i < len(full_matches) else '',
                    'notebook': notebook_data.get('path', 'unknown')
                })
        
        return functions

    def analyze_data_patterns(self, notebook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze notebook for Spark DataFrame patterns and table operations."""
        patterns = {
            'spark_operations': [],
            'table_references': [],
            'schema_definitions': [],
            'data_transformations': []
        }
        
        import re
        for cell in notebook_data.get('cells', []):
            source = cell.get('source', '')
            
            # Find Spark DataFrame operations
            if 'spark.read' in source or 'spark.sql' in source:
                patterns['spark_operations'].append(source[:200])
            
            # Find table references
            table_pattern = r"(?:FROM|INTO|TABLE)\s+['\"]?(\w+\.?\w+)['\"]?"
            tables = re.findall(table_pattern, source, re.IGNORECASE)
            patterns['table_references'].extend(tables)
            
            # Find schema definitions
            if 'StructType' in source or 'StructField' in source:
                patterns['schema_definitions'].append(source[:300])
            
            # Find transformations
            if any(t in source for t in ['.filter(', '.select(', '.groupBy(', '.agg(', '.join(']):
                patterns['data_transformations'].append(source[:200])
        
        # Remove duplicates
        patterns['table_references'] = list(set(patterns['table_references']))
        
        return patterns

    def generate_tests(self, notebook_path: str, output_dir: str) -> str:
        """Generate test cases for a notebook using Azure OpenAI."""
        
        # Parse notebook
        notebook_data = self.parse_notebook(notebook_path)
        functions = self.extract_functions(notebook_data)
        patterns = self.analyze_data_patterns(notebook_data)
        
        # Build context for AI
        notebook_name = Path(notebook_path).stem
        
        prompt = f"""You are an expert Python test engineer specializing in Databricks and PySpark testing.

Analyze the following notebook code and generate comprehensive pytest test cases.

NOTEBOOK: {notebook_name}
PATH: {notebook_path}

FUNCTIONS FOUND:
{json.dumps([{'name': f['name'], 'code': f['code'][:500]} for f in functions[:10]], indent=2)}

DATA PATTERNS DETECTED:
- Spark Operations: {len(patterns['spark_operations'])} found
- Table References: {patterns['table_references'][:10]}
- Schema Definitions: {len(patterns['schema_definitions'])} found
- Data Transformations: {len(patterns['data_transformations'])} found

SAMPLE CODE FROM NOTEBOOK:
{chr(10).join([c['source'][:400] for c in notebook_data['cells'][:5]])}

Generate a complete pytest test file that includes:

1. **Fixtures**:
   - Mock SparkSession fixture
   - Sample DataFrame fixtures based on detected schemas
   - Mock dbutils fixture for Databricks widgets
   - Configuration fixtures

2. **Unit Tests**:
   - Test each function found in the notebook
   - Include positive and negative test cases
   - Test edge cases (empty DataFrames, null values, etc.)

3. **Data Quality Tests**:
   - Schema validation tests
   - Null check assertions
   - Data type validation
   - Business rule validations based on the code logic

4. **Integration Test Stubs**:
   - Table existence checks
   - Data freshness tests

Use these best practices:
- Use pytest parametrize for multiple test cases
- Include docstrings explaining each test
- Use meaningful assertion messages
- Mock external dependencies (dbutils, spark.sql)

Return ONLY the Python code for the test file, no explanations.
"""

        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[
                {"role": "system", "content": "You are an expert Python test engineer. Generate only valid Python pytest code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        test_code = response.choices[0].message.content
        
        # Clean up code block markers if present
        if test_code.startswith('```python'):
            test_code = test_code[9:]
        if test_code.startswith('```'):
            test_code = test_code[3:]
        if test_code.endswith('```'):
            test_code = test_code[:-3]
        
        # Write test file
        test_filename = f"test_{notebook_name}.py"
        output_path = os.path.join(output_dir, test_filename)
        
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(test_code.strip())
        
        print(f"Generated: {output_path}")
        return output_path

    def generate_data_quality_assertions(self, table_name: str, schema_info: Dict = None) -> str:
        """Generate data quality assertion functions for a table."""
        
        prompt = f"""Generate PySpark data quality assertion functions for table: {table_name}

Schema info (if available): {json.dumps(schema_info) if schema_info else 'Not provided'}

Create functions for:
1. check_not_null(df, columns) - Verify no nulls in specified columns
2. check_unique(df, columns) - Verify uniqueness of column combinations
3. check_referential_integrity(df, ref_df, keys) - FK validation
4. check_value_ranges(df, column, min_val, max_val) - Range validation
5. check_data_freshness(df, date_column, max_age_hours) - Freshness check

Return only Python code with these functions.
"""

        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[
                {"role": "system", "content": "Generate only valid PySpark Python code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        
        return response.choices[0].message.content


def discover_notebooks(base_path: str, pattern: str = "**/*.ipynb") -> List[str]:
    """Discover all notebooks in the given path."""
    notebooks = glob.glob(os.path.join(base_path, pattern), recursive=True)
    # Exclude test notebooks
    return [nb for nb in notebooks if 'test' not in nb.lower() and 'unittest' not in nb.lower()]


def main():
    parser = argparse.ArgumentParser(description='Generate AI-powered tests for Databricks notebooks')
    parser.add_argument('--notebooks-path', required=True, help='Path to notebooks directory')
    parser.add_argument('--output-dir', required=True, help='Output directory for generated tests')
    parser.add_argument('--pattern', default='**/*.ipynb', help='Glob pattern for notebook discovery')
    parser.add_argument('--azure-endpoint', help='Azure OpenAI endpoint (or set AZURE_OPENAI_ENDPOINT env var)')
    parser.add_argument('--single-notebook', help='Generate tests for a single notebook only')
    
    args = parser.parse_args()
    
    # Get Azure OpenAI configuration
    azure_endpoint = args.azure_endpoint or os.getenv('AZURE_OPENAI_ENDPOINT')
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    
    if not azure_endpoint or not api_key:
        print("ERROR: Azure OpenAI endpoint and API key required.")
        print("Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY environment variables.")
        exit(1)
    
    # Initialize generator
    generator = NotebookTestGenerator(azure_endpoint, api_key)
    
    # Find notebooks
    if args.single_notebook:
        notebooks = [args.single_notebook]
    else:
        notebooks = discover_notebooks(args.notebooks_path, args.pattern)
    
    print(f"Found {len(notebooks)} notebooks to process")
    
    # Generate tests
    generated_tests = []
    for notebook in notebooks:
        try:
            print(f"\nProcessing: {notebook}")
            test_path = generator.generate_tests(notebook, args.output_dir)
            generated_tests.append(test_path)
        except Exception as e:
            print(f"ERROR processing {notebook}: {e}")
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Generated {len(generated_tests)} test files")
    print(f"Output directory: {args.output_dir}")
    
    # Write manifest
    manifest_path = os.path.join(args.output_dir, 'generated_tests_manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump({
            'generated_at': str(Path(__file__).stat().st_mtime),
            'notebooks_processed': len(notebooks),
            'tests_generated': generated_tests
        }, f, indent=2)


if __name__ == '__main__':
    main()
