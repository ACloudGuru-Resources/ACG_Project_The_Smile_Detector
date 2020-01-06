import cv2
from io import BytesIO
from PIL import Image,ImageDraw
import requests
import os

API_KEY = '<INSERT API KEY HERE>'  # Replace with a valid Subscription Key here.
ENDPOINT = 'https://westeurope.api.cognitive.microsoft.com/face/v1.0/detect'

args = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'smile'
}

def GetSmileScoreAndFaceIdInFrame(pil_img):
    # Convert the opencv frame to bytes
    stream = BytesIO()
    pil_img.save(stream, format='JPEG') # convert PIL Image to Bytes
    bin_img = stream.getvalue()

    # Post the frame to the Face API
    headers = {'Content-Type': 'application/octet-stream', 'Ocp-Apim-Subscription-Key': API_KEY}
    response = requests.post(data=bin_img, url=ENDPOINT, headers=headers, params=args)
    jsondata = response.json()

    faceId = ""
    smile = 0
    if jsondata and jsondata[0]:
        smile = jsondata[0]["faceAttributes"]["smile"]
        faceId = jsondata[0]["faceId"]
    return smile, faceId









def VerifyFriend(faceId):
    endpointVerify = "https://westeurope.api.cognitive.microsoft.com/face/v1.0/verify"
    headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': API_KEY}
    
    name = ""
    isFriend = False

    for friendname, faceIdFriend in friendList:
        body = dict(faceId1 = faceId, faceId2 = faceIdFriend)
        response = requests.post(url=endpointVerify, headers=headers, json=body)
        jsondata = response.json()

        if jsondata['isIdentical'] == True:
            name = friendname
            isFriend = True
            break
    
    return isFriend, name

cap = cv2.VideoCapture(2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
cap.set(cv2.CAP_PROP_FPS, 10)

# Index the friends directory send the image to the face api and retrieve a face
friendList = []
path = "friends/"
for f in os.listdir(path):
    friendname = os.path.splitext(f)[0]
    pil_image = Image.open(os.path.join(path,f))
    smile, faceId = GetSmileScoreAndFaceIdInFrame(pil_image)
    friendList.append((friendname,faceId))

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Detect the smile score for every frame
    pil_img = Image.fromarray(frame)
    smile, faceId = GetSmileScoreAndFaceIdInFrame(pil_img)

    # Convert the frame to black and white
    if smile < 0.7:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    else:
        isFriend, friendName = VerifyFriend(faceId)
        message = "Hello "+friendName
        if isFriend == False:
            message = "Thanks for the smile, but no colour for you!"
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.putText(frame,message, (30,500), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255)) 
            
    # Show the frame
    cv2.imshow('frame',frame)

    # Exit when pressing the q key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
