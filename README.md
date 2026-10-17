# SYNORA (refactored Flask project)

## Run locally
1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure values. Export the variables in your shell (or install python-dotenv and load `.env`).
4. Run: `python run.py`
5. Open `http://127.0.0.1:5000`.

## Storage
By default, the Store uses in-memory data, so records are lost on restart. Set `USE_DYNAMODB=1` and create DynamoDB tables named `SkillPortal-students`, `SkillPortal-opportunities`, and `SkillPortal-applications`, each with partition key `id` (String), to use DynamoDB. Configure AWS credentials using a supported AWS credentials provider.

Document upload/download/delete uses a private S3 bucket configured with `S3_BUCKET`, `AWS_REGION`, and appropriate IAM permissions.

## Structure
- `app/routes/`: HTTP endpoints grouped by feature
- `app/services/`: reusable business/storage operations
- `app/models/store.py`: in-memory/DynamoDB data access
- `app/templates/`: Jinja HTML templates
- `app/static/css/style.css`: UI stylesheet
- `app/config.py`: environment-backed configuration

Before production, replace the development secret, validate uploaded file contents (not just extensions), add CSRF protection and rate limiting, and configure persistent storage.
