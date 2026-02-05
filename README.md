# DataFabric Databricks CI/CD

## Pipeline Overview
This repository implements a CI/CD pipeline for Databricks asset bundles using Azure DevOps. The pipeline automates:
- Environment setup (Python, Databricks CLI)
- Secret retrieval from Azure Key Vault
- Bundle validation and deployment to Databricks workspaces (dev, test, prod)
- Post-deployment smoke testing

## How to Add New Jobs/Notebooks
1. **Add your notebook** to the appropriate folder under `notebooks/code/datafabric/`.
2. **Define a job** in `databricks.yml` under the `resources.jobs` section, referencing the notebook path.
3. **Commit and push** your changes. The pipeline will include the new notebook/job in the next deployment.

## How to Run/Deploy Locally
1. Install Python 3.x and the Databricks CLI:
   ```sh
   python -m pip install --upgrade pip
   pip install databricks-cli
   ```
2. Authenticate with Databricks:
   ```sh
   databricks configure --token
   ```
3. Validate and deploy the bundle:
   ```sh
   databricks bundle validate -t dev
   databricks bundle deploy -t dev
   ```
   Replace `dev` with `test` or `prod` as needed.

## How to Update Secrets/Variables
- **Azure Key Vault**: Update secrets directly in the Azure Key Vault referenced by your environment's variable group.
- **Pipeline Variables**: Update variables (e.g., `SMOKE_TEST_JOB_ID`) in the Azure DevOps variable group for each environment.
- **Environment Variables**: If running locally, set required environment variables in your shell or use a `.env` file (if supported).

---

For more details, see the inline comments in the pipeline YAML files and the Databricks bundle documentation: https://docs.databricks.com/dev-tools/bundles/index.html
