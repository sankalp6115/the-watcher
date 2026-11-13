from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import requests

text1 = "€>5> PP Shradha = @ lecture_eight.py @ py O ® lecture_eight.py > ¢ Student P 1 class Student: is 2 3 #default constructors ] 9 4 _init_(s 5 S 6 & 7 #parameterized constructors 8 def __init_(self, name, marks): — 9 self.name = name 10 self.marks = marks 11 print(""adding new student in Database.."") 12 13 (2) 14 $1 = Student(""karan"", 97) 15 print(si.name, sl.marks) #karan 16 g02 17 s2 = Student(""arjun"", 88) print(s2.name, s2.marks) {g) Oo Ln 5, Col 13 (58 selected) Spaces:4 UTF-8 LF ($P"
text2 = "we ® Sd Your story 3_nine_07 akshunya_mishr... _lalit.katheriya web_development_legend (a 1 deprezz « I'll Do It (Slowed) FOR 2025 & N cA 5 SMS Sender School Online Quiz Management System —+o LE. oe, 0196 Nee m y SS Dice Education Face Simulator System Recognition Email Sender Hospital Management O x Security Automatic Software Driver 2 Playing With Ticket Video Editor Tic-Tac-Toe Cards Reservation ®. python ow) V9 AV Liked by x0117_35a and others web_development_legend # Follow for more @ @# @web_development_legend... more A Q G) fe) Professional Email Client Calculator"

res1 = requests.post(
    "http://localhost:8000/embed-text",
    json={"text": text1}
)

res2 = requests.post(
    "http://localhost:8000/embed-text",
    json={"text": text2}
)

embed1 = np.array(res1.json()["embedding"]).reshape(1,-1)
embed2 = np.array(res2.json()["embedding"]).reshape(1,-1)


similarity = cosine_similarity(embed1,embed2)

print(similarity[0][0])
