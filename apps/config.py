import os
if os.environ.get('RENDER', None) != 'true':
    from dotenv import load_dotenv      # render.com이 아닌 로컬 환경에서만 .env를 로드(안해도 됨)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    dotenv_path = os.path.join(BASE_DIR, '..', '.env')
    load_dotenv(dotenv_path)
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    #API_KEY = os.getenv('API_KEY')
    IRIS_LABELS = ['setosa', 'versicolor', 'virginica']
    INSTANCE_DIR = os.path.join(BASE_DIR, '..', 'instance')
    if not os.path.exists(INSTANCE_DIR):
        os.makedirs(INSTANCE_DIR)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(INSTANCE_DIR, 'mydb.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Flask-Login
    # REMEMBER_COOKIE_DURATION = 3600  # 1시간
    # Flask-CSRFProtect
    CSRF_ENABLED = True
    CSRF_SESSION_KEY = os.getenv('CSRF_SESSION_KEY', SECRET_KEY) # 없으면,SECRET_KEY사용
    # API Key 관련 설정 (필요시 추가)
    #API_KEY_LENGTH = 32 # API 키 길이   #API_KEY_EXPIRATION_DAYS = 365 # API 키 만료일
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')    
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')    
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
