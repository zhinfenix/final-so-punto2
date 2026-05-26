from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
import boto3
from botocore.exceptions import ClientError

app = FastAPI(title="API S3 EC2")
BUCKET_NAME = "final-so-imagenes-zhinfenix-3806"
s3_client = boto3.client('s3', region_name='us-east-2')

@app.post("/upload/")
async def upload_image(usuario: str = Form(...), file: UploadFile = File(...)):
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Solo PNG o JPG/JPEG.")
    
    file_key = f"{usuario}/{file.filename}"
    try:
        s3_client.upload_fileobj(file.file, BUCKET_NAME, file_key)
        return {"message": "Imagen subida", "path": file_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/image/")
async def get_image(usuario: str, image_name: str):
    file_key = f"{usuario}/{image_name}"
    try:
        response = s3_client.head_object(Bucket=BUCKET_NAME, Key=file_key)
        last_modified = response['LastModified']
        presigned_url = s3_client.generate_presigned_url(
            'get_object', Params={'Bucket': BUCKET_NAME, 'Key': file_key}, ExpiresIn=3600
        )
        return {"message": "Encontrada", "url": presigned_url, "fecha": last_modified}
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            raise HTTPException(status_code=404, detail="El usuario o la imagen no existen.")
        raise HTTPException(status_code=500, detail=str(e))

