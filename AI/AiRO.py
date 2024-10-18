#########################################################
#  $$$$$ this code is for face recognition $$$$$


# Ai and router here

# TODO: 
# -1  create router for the ai and router | Done!
# -2  Tast All endpoint | --
#- 3
#########################################################


import base64
import os
import cv2
from fastapi import APIRouter, FastAPI, Request, WebSocket, BackgroundTasks, UploadFile, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import numpy as np
import face_recognition
import asyncio
import time
import mysql.connector
import pygame

pygame.mixer.init()
alarm_sound = pygame.mixer.Sound('mixkit-classic-alarm-995.wav')

# Establish a database connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # Update with your actual password
    database="face_recognition_db",
    port=3306,
)
mycursor = mydb.cursor()

# دالة لتخزين الصور في قاعدة البيانات
# Function to store images in the database
def store_images_in_db(path):
    start_time = time.time()  # for testng and improve performance
    for filename in os.listdir(path):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(path, filename)

            # Read the image file as binary data
            with open(image_path, "rb") as file:
                binary_data = file.read()

            # Extract the ref_no and name from the filename
            name, ref_no = filename.split(".")[0], filename.split(".")[1]

            # Insert the image into the database
            # sql = "INSERT INTO faces (name, ref_no, data) VALUES (?, ?, ?)"
            sql = "INSERT INTO faces (name, ref_no, data) VALUES (%s, %s, %s)"  #if ues mysql for database
            val = (name, ref_no, binary_data)
            try:
                mycursor.execute(sql, val)
                mydb.commit()
                print(f"Inserted {filename} into the database.")
            # except sqlite3.Error as err:
            except mysql.connector.Error as err:
                print(f"Error: {err}")
    end_time = time.time()  # for testng and improve performance
    print(f"Time taken to store images: {end_time - start_time:.2f} seconds")



stream_active = False
cap = None


# دالة لاسترجاع ومعالجة الصور للتعرف على الوجوه
def retrieve_and_process_images():
    start_time = time.time()  # for testng and improve performance
    mycursor.execute("SELECT name, ref_no, data FROM faces")
    results = mycursor.fetchall()

    images = []
    classNames = []
    ref_nos = []

    # Process each row from the database
    for row in results:
        ref_no = row[1]
        name = row[0]
        image_data = row[2]

        # Convert the binary data to a NumPy array
        np_image = np.frombuffer(image_data, dtype=np.uint8)
        # Decode the NumPy array into an image
        img = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        if img is not None:
            images.append(img)
            classNames.append(name)
            ref_nos.append(ref_no)
    end_time = time.time()  # for testng and improve performance
    print(
        f"Time taken to retrieve and process images: {end_time - start_time:.2f} seconds"
    )
    return images, classNames, ref_nos


# استرجاع الصور والترميز
# Retrieve images and encodings
images, classNames, ref_nos = retrieve_and_process_images()


# دالة للعثور على ترميزات الصور
def findEncodeings(images):
    start_time = time.time()  # for testng and improve performance
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)
        if len(encode) > 0:
            encodeList.append(encode[0])
    end_time = time.time()  # for testng and improve performance
    print(f"Time taken to find encodings: {end_time - start_time:.2f} seconds")
    return encodeList


encodeListKnown = findEncodeings(images)
print("Encoding Complete.")

# إنشاء موجه FastAPI
router = APIRouter()


# نقطة نهاية WebSocket لبث الفيديو
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global stream_active, cap
    await websocket.accept()  # chack

    # Real-time face recognition
    if cap is None:
        cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        await websocket.send_text("Error: Could not open camera.")
        await websocket.close()
        return

    # متغيرات لتتبع الحالة
    recognized_toggle = True  # لتتبع recognized_faces
    unrecognized_toggle = True  # لتتبع unrecognized_faces
    connection_closed = False  # لتتبع اغلاق الاتصال

    try:
        while True:
            if not stream_active:

                await asyncio.sleep(0.1)
                continue

            if connection_closed:
                break
            start_time = time.time()  #

            success, img = cap.read()
            if not success:
                await websocket.send_text("Error: Failed to capture image.")
                break

            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            faceCurentFrame = face_recognition.face_locations(imgS, model="cnn")
            encodeCurentFrame = face_recognition.face_encodings(imgS, faceCurentFrame)

            for encodeface, faceLoc in zip(encodeCurentFrame, faceCurentFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeface)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeface)

                if len(faceDis) > 0:
                    matchIndex = np.argmin(faceDis)
                    if matches[matchIndex]:
                        name = classNames[matchIndex].upper()
                        face_id = ref_nos[matchIndex]
                        y1, x2, y2, x1 = faceLoc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.rectangle(
                            img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED
                        )
                        cv2.putText(
                            img,
                            name,
                            (x1 + 6, y2 - 6),
                            cv2.FONT_HERSHEY_COMPLEX,
                            1,
                            (255, 255, 255),
                            2,
                        )
                        # تعيين category لـ recognized_faces
                        category = "ENTERING" if recognized_toggle else "LEAVING"
                        recognized_toggle = not recognized_toggle  # تبديل الحالة

                        snapshot = cv2.imencode(".jpg", img)[1].tobytes()

                        # sql = "INSERT INTO recognized_faces (face_id, snapshot, category) VALUES (?, ?, ?)"
                        sql = "INSERT INTO recognized_faces (face_id, snapshot, category) VALUES (%s, %s, %s)"

                        val = (face_id, snapshot, category)
                        try:
                            mycursor.execute(sql, val)
                            mydb.commit()
                            print(
                                f"Inserted recognized face for {name} into recognized_faces with category '{category}'."
                            )
                            await asyncio.sleep(1)  #
                        # except sqlite3.Error as err:
                        except mysql.connector.Error as err:
                            print(f"Error: {err}")

                    else:
                        # التقاط لقطة للوجه غير المعروف
                        y1, x2, y2, x1 = faceLoc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.rectangle(
                            img, (x1, y2 - 35), (x2, y2), (0, 0, 255), cv2.FILLED
                        )
                        cv2.putText(
                            img,
                            "Unknown",
                            (x1 + 6, y2 - 6),
                            cv2.FONT_HERSHEY_COMPLEX,
                            1,
                            (255, 255, 255),
                            2,
                        )

                        # # تشغيل صوت الإنذار
                        alarm_sound.play()  # تشغيل صوت الإنذار

                        # تعيين category لـ unrecognized_faces
                        category = "ENTERING" if unrecognized_toggle else "LEAVING"
                        unrecognized_toggle = not unrecognized_toggle

                        snapshot = cv2.imencode(".jpg", img)[1].tobytes()

                        # sql = "INSERT INTO unrecognized_faces (snapshot, category) VALUES (?, ?)"
                        sql = "INSERT INTO unrecognized_faces (snapshot, category) VALUES (%s, %s)"
                        val = (snapshot, category)  # إضافة category
                        try:
                            mycursor.execute(sql, val)
                            mydb.commit()
                            print("Inserted unrecognized face into unrecognized_faces.")
                            await asyncio.sleep(1)
                            # global stream_active, cap  # الوصول إلى المتغيرات العامة
                            stream_active = False  # إيقاف البث
                            if cap is not None:
                                cap.release()
                                cap = None
                        # except sqlite3.Error as err:
                        except mysql.connector.Error as err:
                            print(f"Error: {err}")

            # cv2.imshow("Face Recognition", img)
            # if cv2.waitKey(1) & 0xFF == ord("q"):
            #     break

            # Explanation:
            # - cv2.imshow() and cv2.waitKey() are commented out because video display is handled
            #   through the web interface, sending the video to the browser via WebSocket as Base64.
            # - There is no need for local window display or stopping the stream using the keyboard,
            #   since the stream is controlled by "Start" and "Stop" buttons in the web interface.

            _, jpeg_frame = cv2.imencode(".jpg", img)
            frame_base64 = base64.b64encode(jpeg_frame).decode("utf-8")

            try:
                await websocket.send_text(frame_base64)
            except RuntimeError as e:
                print(f"RuntimeError during send: {e}")
                connection_closed = True
                break

            end_time = time.time()
            print(
                f"Time taken for one frame processing: {end_time - start_time:.2f} seconds"
            )

            await asyncio.sleep(1.1)

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if cap is not None:
            cap.release()
            cap = None
        if not connection_closed:
            await websocket.close()
        else:
            print("WebSocket was already closed, skipping close operation.")


# نقطة نهاية HTTP لبدء البث
@router.post("/start_stream")
async def start_stream(background_tasks: BackgroundTasks):
    global stream_active
    stream_active = True
    return {"status": "Started the stream"}


# نقطة نهاية HTTP لإيقاف البث يدويًا
@router.post("/stop_stream")
async def stop_stream():
    global stream_active, cap
    stream_active = False
    if cap is not None:
        cap.release()
        cap = None
    return {"status": "Stopped the stream"}

templates = Jinja2Templates(directory="template")


@router.get("/", response_class=HTMLResponse)
async def get_html(request: Request):
    return templates.TemplateResponse("root.html", {"request": request})

# دالة لإضافة وجه جديد إلى قاعدة البيانات
def add_face_to_db(name: str, ref_no: str, image_data: bytes):
    # sql = "INSERT INTO faces (name, ref_no, data) VALUES (?, ?, ?)"
    sql = "INSERT INTO faces (name, ref_no, data) VALUES (%s, %s, %s)"
    val = (name, ref_no, image_data)
    try:
        mycursor.execute(sql, val)
        mydb.commit()
        print(f"Inserted {name} with ref_no {ref_no} into the database.")
    # except sqlite3.Error as err:
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        raise


# دالة لتحديث قائمة الترميزات المعروفة بعد إضافة وجه جديد
def update_known_encodings():
    global encodeListKnown, classNames, ref_nos
    images, classNames, ref_nos = retrieve_and_process_images()
    encodeListKnown = findEncodeings(images)
    print("Updated Encoding List.")


# نقطة نهاية HTTP لإضافة وجه جديد
@router.post("/add_face")
async def add_face(
    name: str = Form(...), ref_no: str = Form(...), image: UploadFile = Form(...)
):
    try:
        # قراءة بيانات الصورة المرفقة
        image_bytes = await image.read()

        # التحقق من نوع الملف
        # if image.content_type not in ["image/jpeg", "image/png"]:
        #     return {"error": "Invalid image type. Only JPEG and PNG are supported."}

        # إضافة الوجه إلى قاعدة البيانات
        add_face_to_db(name, ref_no, image_bytes)

        # تحديث قائمة الترميزات المعروفة
        update_known_encodings()

        return {"status": "Face added successfully."}
    except Exception as e:
        print(f"Error adding face: {e}")
        return {"error": "An error occurred while adding the face."}


@router.on_event("shutdown")
def shutdown_event():
    mycursor.close()
    mydb.close()

