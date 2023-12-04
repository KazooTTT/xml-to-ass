import os
import subprocess
import zipfile
from typing import List
import tempfile
from datetime import datetime

from fastapi import FastAPI, UploadFile, File
from starlette.responses import FileResponse

app = FastAPI()


@app.get("/")
async def index():
    return {"data": "hello world",
            "status": 200,
            "msg": "success"}


@app.post("/convert")
async def convertToFileList(files: List[UploadFile] = File(...)):
    converted_files = await convertXmlToAss(files)

    return {"data": converted_files,
            "status": 200,
            "msg": "success"}


@app.post("/convert/zip")
async def convertToZip(files: List[UploadFile] = File(...)):
    converted_files = await convertXmlToAss(files)
    # convert the files into zip
    zip_filename = f"converted_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        for file in converted_files:
            zipf.write(file)
    return FileResponse(zip_filename, media_type="application/zip", filename=zip_filename)


async def convertXmlToAss(files: List[UploadFile] = File(...)):
    converted_files = []
    # loop the files and convert them
    for file in files:
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml", prefix=file.filename) as tmp:
            tmp.write(await file.read())
            tmp_file_name = tmp.name

            # Get the base name from the file
            basename = os.path.basename(file.filename).split('.')[0]
            output_name = f"{basename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ass"

            # run the DanmakuFactory command
            subprocess.run(["./convert/DanmakuFactory", "-o", output_name, "-i", tmp_file_name], check=True)
            converted_files.append(output_name)
    return converted_files
