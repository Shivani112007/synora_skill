import uuid

from botocore.exceptions import ClientError
from flask import abort, flash, redirect, request, url_for
from werkzeug.utils import secure_filename

from app import (
    ALLOWED_EXTENSIONS,
    S3_BUCKET,
    app,
    db,
    me,
    page,
)
from app.services.document_service import get_s3, get_user_documents


@app.route("/documents", methods=["GET", "POST"])
def documents():
    u = me()
    if not u:
        return redirect(url_for("login"))

    docs = get_user_documents(u)

    if request.method == "POST":
        file = request.files.get("document")
        label = request.form.get("label", "").strip()
        category = request.form.get("category", "Other")

        if not file or not file.filename:
            flash("Please choose a file.")
            return redirect(url_for("documents"))

        filename = secure_filename(file.filename)
        if not filename or "." not in filename:
            flash("Invalid filename.")
            return redirect(url_for("documents"))

        extension = filename.rsplit(".", 1)[1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            flash("File type not allowed.")
            return redirect(url_for("documents"))

        if category not in {
            "Resume",
            "Certificate",
            "Academic Record",
            "Project",
            "Other",
        }:
            flash("Invalid document category.")
            return redirect(url_for("documents"))

        # The browser's content type is not trusted; inspect the file signature
        # or use a dedicated validation library before production deployment.
        doc_id = uuid.uuid4().hex
        key = f"student-documents/{uuid.uuid4().hex}/{filename}"

        try:
            s3 = get_s3()
            s3.upload_fileobj(
                file,
                S3_BUCKET,
                key,
                ExtraArgs={
                    "ContentType": file.mimetype or "application/octet-stream",
                    "Metadata": {"owner": uuid.uuid5(uuid.NAMESPACE_URL, u["id"]).hex},
                },
            )
        except (ClientError, RuntimeError):
            app.logger.exception("Document upload failed")
            flash("Upload failed. Check the S3 configuration and permissions.")
            return redirect(url_for("documents"))

        docs.append(
            {
                "id": doc_id,
                "label": label or filename,
                "filename": filename,
                "category": category,
                "s3_key": key,
            }
        )
        db.put("students", u)
        flash("Document uploaded successfully.")
        return redirect(url_for("documents"))

    return page("documents.html", title="My Documents", u=u, documents=docs)


@app.route("/documents/<doc_id>/download")
def document_download(doc_id):
    u = me()
    if not u:
        return redirect(url_for("login"))

    doc = next(
        (d for d in get_user_documents(u) if d["id"] == doc_id),
        None,
    )
    if not doc:
        abort(404)

    try:
        url = get_s3().generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": doc["s3_key"]},
            ExpiresIn=300,
        )
        return redirect(url)

    except (ClientError, RuntimeError):
        app.logger.exception("Document download link failed")
        abort(503)


@app.route("/documents/<doc_id>/delete", methods=["POST"])
def document_delete(doc_id):
    u = me()
    if not u:
        return redirect(url_for("login"))

    docs = get_user_documents(u)
    doc = next((d for d in docs if d["id"] == doc_id), None)
    if not doc:
        abort(404)

    try:
        get_s3().delete_object(
            Bucket=S3_BUCKET,
            Key=doc["s3_key"],
        )
    except (ClientError, RuntimeError):
        app.logger.exception("Document deletion failed")
        flash("Could not delete the document from storage.")
        return redirect(url_for("documents"))

    u["documents"] = [d for d in docs if d["id"] != doc_id]
    db.put("students", u)
    flash("Document deleted successfully.")
    return redirect(url_for("documents"))


# import uuid

# from flask import abort, flash, redirect, request, url_for
# from werkzeug.utils import secure_filename

# from app import (
#     ALLOWED_EXTENSIONS,
#     S3_BUCKET,
#     app,
#     db,
#     me,
#     page,
# )
# from app.services.document_service import get_s3, get_user_documents


# @app.route("/documents", methods=["GET", "POST"])
# def documents(ClientError):
#     u = me()
#     if not u:
#         return redirect(url_for("login"))

#     docs = get_user_documents(u)

#     if request.method == "POST":
#         file = request.files.get("document")
#         label = request.form.get("label", "").strip()
#         category = request.form.get("category", "Other")

#         if not file or not file.filename:
#             flash("Please choose a file.")
#             return redirect(url_for("documents"))

#         filename = secure_filename(file.filename)
#         if not filename or "." not in filename:
#             flash("Invalid filename.")
#             return redirect(url_for("documents"))

#         extension = filename.rsplit(".", 1)[1].lower()
#         if extension not in ALLOWED_EXTENSIONS:
#             flash("File type not allowed.")
#             return redirect(url_for("documents"))

#         if category not in {
#             "Resume",
#             "Certificate",
#             "Academic Record",
#             "Project",
#             "Other",
#         }:
#             flash("Invalid document category.")
#             return redirect(url_for("documents"))

#         # The browser's content type is not trusted; inspect the file signature
#         # or use a dedicated validation library before production deployment.
#         doc_id = uuid.uuid4().hex
#         key = f"student-documents/{uuid.uuid4().hex}/{filename}"

#         try:
#             s3 = get_s3()
#             s3.upload_fileobj(
#                 file,
#                 S3_BUCKET,
#                 key,
#                 ExtraArgs={
#                     "ContentType": file.mimetype or "application/octet-stream",
#                     "Metadata": {"owner": uuid.uuid5(uuid.NAMESPACE_URL, u["id"]).hex},
#                 },
#             )
#         except (ClientError, RuntimeError):
#             app.logger.exception("Document upload failed")
#             flash("Upload failed. Check the S3 configuration and permissions.")
#             return redirect(url_for("documents"))

#         docs.append(
#             {
#                 "id": doc_id,
#                 "label": label or filename,
#                 "filename": filename,
#                 "category": category,
#                 "s3_key": key,
#             }
#         )
#         db.put("students", u)
#         flash("Document uploaded successfully.")
#         return redirect(url_for("documents"))

#     return page("documents.html", title="My Documents", u=u, documents=docs)


# @app.route("/documents/<doc_id>/download")
# def document_download(doc_id):
#     u = me()
#     if not u:
#         return redirect(url_for("login"))

#     doc = next((d for d in get_user_documents(u) if d["id"] == doc_id), None)
#     if not doc:
#         abort(404)

#     class ClientError:
#         ...

#     try:
#         url = get_s3().generate_presigned_url(
#             "get_object",
#             Params={"Bucket": S3_BUCKET, "Key": doc["s3_key"]},
#             ExpiresIn=300,
#         )
#         return redirect(url)

#     except (ClientError, RuntimeError):
#         app.logger.exception("Document download link failed")
#         abort(503)

#     return redirect(url)


# @app.route("/documents/<doc_id>/delete", methods=["POST"])
# def document_delete(doc_id):
#     u = me()
#     if not u:
#         return redirect(url_for("login"))

#     docs = get_user_documents(u)
#     doc = next((d for d in docs if d["id"] == doc_id), None)
#     if not doc:
#         abort(404)

#     class ClientError:
#         ...

#     try:
#         get_s3().delete_object(Bucket=S3_BUCKET, Key=doc["s3_key"])
#     except (ClientError, RuntimeError):
#         app.logger.exception("Document deletion failed")
#         flash("Could not delete the document from storage.")
#         return redirect(url_for("documents"))

#     u["documents"] = [d for d in docs if d["id"] != doc_id]
#     db.put("students", u)
#     flash("Document deleted successfully.")
#     return redirect(url_for("documents"))
