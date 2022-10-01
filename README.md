# Paper-Cloud
A new paradigm for bibliography

## Abstract
연구자들에게 있어서 논문 서지 관리는 매우 중요하다. 시중에는 pdf 등에서 논문의 정보(metadata)를 자동으로 추출하여 나열해주는 프로그램이 많이 있다.
하지만 이런 프로그램들은 알파벳 등의 순서의 리스트로 논문의 정보들을 보여주고, 대부분의 경우 이 보여지는 순서는 연구자가 찾고싶은 내용의 순서와는 동떨어져있다.
이런 문제를 해결하기 위해, 이 글에서는 Paper Cloud 라는 새로운 방식의 논문 서지 관리 프로그램을 제안한다.
Paper Cloud 는 pdf 형태의 각 논문을 추출해서 bag-of-words 의 형태로 나타낸다. 이어서 논문 사이의 cosine similarity 를 계산하고,
t-SNE 라는 임베딩 기법을 통해 이를 연구자에게 직관적인 2차원 구름(cloud)의 형태로 보여주는 것이 기본적인 아이디어이다.
위와 같은 아이디어를 실제로 사용해 생산성을 높일 수 있도록 이번 프로젝트에서는 Python 과 JDK 를 이용해 GUI 와 여러 필수 기능까지 구현하는 것을 목표로 한다.

## Product Features
![multiselect](https://user-images.githubusercontent.com/5498512/193402693-b6000b3a-c932-425d-b76f-2e0399beb852.png)
![rubberband](https://user-images.githubusercontent.com/5498512/193402695-abb0a736-5ec9-45d1-8494-4fa5618244d5.png)
![mainwindow](https://user-images.githubusercontent.com/5498512/193402696-bce0acd5-b4a6-488f-a433-38b70f584181.png)

## Dependencies

<pre>
tika-server-1.19.jar
cermine-1.13.jar
</pre>
<pre>
arxiv2bib==1.0.8
bibtexparser==1.1.0
certifi==2019.11.28
chardet==3.0.4
click==7.1.1
cycler==0.10.0
future==0.18.2
idna==2.9
isbnlib==3.10.0
joblib==0.14.1
kiwisolver==1.1.0
libbmc==0.2.1
matplotlib==3.1.3
mkl-fft==1.0.15
mkl-random==1.1.0
mkl-service==2.3.0
nltk==3.4.5
numpy==1.18.1
pandas==1.0.3
pycryptodome==3.9.7
pyparsing==2.4.6
PyPDF2==1.26.0
PyQt5==5.13.0
PyQt5-sip==12.7.1
pyqt5-tools==5.13.0.1.5
PySocks==1.7.1
python-dateutil==2.8.1
python-dotenv==0.12.0
pytz==2019.3
requests==2.23.0
scikit-learn==0.22.2.post1
scipy==1.4.1
six==1.14.0
tika==1.24
tornado==6.0.4
urllib3==1.25.8
wincertstore==0.2
</pre>
