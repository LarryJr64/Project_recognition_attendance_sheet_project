
from datetime import datetime
import cv2
import numpy as np
import os
import PIL.Image
import dlib
from imutils import face_utils
import argparse
from pathlib import Path
import ntpath
import pandas as pd

#subprocess pour run des command line 
parser = argparse.ArgumentParser(description='Easy Facial Recognition App')
parser.add_argument('-i', '--input', type=str, required=True, help='directory of input known faces')


def start_recognition():
    global pose_predictor_68_point, pose_predictor_5_point, face_encoder, face_detector, df_present
    print('[INFO] Starting System...')
    print('[INFO] Importing pretrained model..')
    df_present={"names":set(),"presence":[]}
    pose_predictor_68_point = dlib.shape_predictor("C:/Users/louis/Desktop/Programmation_Wirtz/modèles/pretrained_model/shape_predictor_68_face_landmarks.dat")
    pose_predictor_5_point = dlib.shape_predictor("C:/Users/louis/Desktop/Programmation_Wirtz/modèles/pretrained_model/shape_predictor_5_face_landmarks.dat")
    face_encoder = dlib.face_recognition_model_v1("C:/Users/louis/Desktop/Programmation_Wirtz/modèles/pretrained_model/dlib_face_recognition_resnet_model_v1.dat")
    face_detector = dlib.get_frontal_face_detector()
    print('[INFO] Importing pretrained model..')

def transform(image, face_locations):
    coord_faces = []
    for face in face_locations:
        rect = face.top(), face.right(), face.bottom(), face.left()
        coord_face = max(rect[0], 0), min(rect[1], image.shape[1]), min(rect[2], image.shape[0]), max(rect[3], 0)
        coord_faces.append(coord_face)
    return coord_faces


def encode_face(image):
    face_locations = face_detector(image, 1)
    face_encodings_list = []
    landmarks_list = []
    for face_location in face_locations:
        # DETECT FACES
        shape = pose_predictor_68_point(image, face_location)
        face_encodings_list.append(np.array(face_encoder.compute_face_descriptor(image, shape, num_jitters=1)))
        # GET LANDMARKS
        shape = face_utils.shape_to_np(shape)
        landmarks_list.append(shape)
    face_locations = transform(image, face_locations)
    return face_encodings_list, face_locations, landmarks_list

    
def easy_face_reco(frame, known_face_encodings, known_face_names):
    global result
    global df_present
    rgb_small_frame = frame[:, :, ::-1]
    # ENCODING FACE
    face_encodings_list, face_locations_list, landmarks_list = encode_face(rgb_small_frame)
    face_names = []
    for face_encoding in face_encodings_list:
        if len(face_encoding) == 0:
            return np.empty((0))
        # CHECK DISTANCE BETWEEN KNOWN FACES AND FACES DETECTED
        vectors = np.linalg.norm(known_face_encodings - face_encoding, axis=1)
        tolerance = 0.6
        result = []

        for vector in vectors:
            if vector <= tolerance:
                result.append(True)
            else:
                result.append(False)
        if True in result:
            first_match_index = result.index(True)
            name = known_face_names[first_match_index]
            df_present['names'].add(name)
            if len(df_present['presence']) < len(df_present['names']):
                df_present["presence"].append(datetime.now().strftime("%Hh%M"))
            else:
                pass
        else:
            name = "Unknown"
        face_names.append(name)

    for (top, right, bottom, left), name in zip(face_locations_list, face_names):
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.rectangle(frame, (left, bottom - 30), (right, bottom), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, name, (left + 2, bottom - 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)


    for shape in landmarks_list:
        for (x, y) in shape:
            cv2.circle(frame, (x, y), 1, (255, 0, 255), -1)

def execution_recognition():         
#if __name__ == '__main__':
    start_recognition()
    args = parser.parse_args()

    print('[INFO] Importing faces...')
    face_to_encode_path = Path(args.input)
    files = [file_ for file_ in face_to_encode_path.rglob('*.jpg')]

    for file_ in face_to_encode_path.rglob('*.png'):
        files.append(file_)
    if len(files)==0:
        raise ValueError('No faces detect in the directory: {}'.format(face_to_encode_path))
    known_face_names = [os.path.splitext(ntpath.basename(file_))[0] for file_ in files]

    known_face_encodings = []
    for file_ in files:
        image = PIL.Image.open(file_)
        image = np.array(image)
        face_encoded = encode_face(image)[0][0]
        known_face_encodings.append(face_encoded)        

    print('[INFO] Faces well imported')
    print('[INFO] Starting Webcam...')
    video_capture = cv2.VideoCapture(0)
    print('[INFO] Webcam well started')
    print('[INFO] Detecting...')
    names_cleaned=[]
    while True:
        ret, frame = video_capture.read()
        frame = cv2.GaussianBlur(frame, (7, 7), 0)
        easy_face_reco(frame, known_face_encodings, known_face_names)          
        cv2.imshow('Easy Facial Recognition App', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            df_present["names"]=list(df_present["names"])
            pd.DataFrame(df_present).to_csv("C:/Users/louis/Documents/GitHub/Projet_Wirtz/outputs/output.csv")
            break
    print('[INFO] Stopping System')
    
    video_capture.release()
    cv2.destroyAllWindows()
    print(df_present)
    

