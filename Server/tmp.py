
from scipy.misc import imresize, imsave
import pyrebase
import cv2
firebaseConfig = {
  'apiKey': "AIzaSyDemEX4zM6WQAYVYewOk-0y6EOTrt4Jeq4",
  'authDomain': "pbl5-c253c.firebaseapp.com",
  'databaseURL': "https://pbl5-c253c-default-rtdb.firebaseio.com",
  'projectId': "pbl5-c253c",
  'storageBucket': "pbl5-c253c.appspot.com",
  'messagingSenderId': "769387973080",
  'appId': "1:769387973080:web:14271fb1bc1478688c8aad",
  'measurementId': "G-DXRW3ZD08C"
}
firebase = pyrebase.initialize_app(firebaseConfig)
database = firebase.database()
storage = firebase.storage()
auth = firebase.auth()
email = "baoquocitf@gmail.com"
password = "123258zxc"
user = auth.sign_in_with_email_and_password(email, password)
student = database.child("Student/101").get()
a =student.val()
print(a['name'])


