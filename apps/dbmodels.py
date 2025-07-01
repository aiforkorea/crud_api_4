#apps/dbmodels.py
import enum
import uuid
from apps import db  # apps에서 db를 import
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash 
#hash import
from datetime import datetime
from apps.config import Config
class User(db.Model, UserMixin): 
# db.Model, UserMixin 상속하는 User 클래스 생성
    __tablename__= "users"  # 삭제시, 테이블 이름은 Model 이름 소문자 
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String, index=True)
    email=db.Column(db.String, unique=True, index= True)
    password_hash=db.Column(db.String)
    is_admin=db.Column(db.Boolean,default=False)
    created_at=db.Column(db.DateTime, default= datetime.now)
    updated_at=db.Column(db.DateTime, default= datetime.now, onupdate=datetime.now)
    api_keys = db.relationship('APIKey', backref='user', lazy=True, cascade='all, delete-orphan')
    usage_logs = db.relationship('UsageLog', backref='user', lazy=True, cascade='all, delete-orphan')
    iris_results = db.relationship('IRIS', backref='user', lazy=True, cascade='all, delete-orphan')
    # The 'password' property and its setter
    @property
    def password(self):
        # Prevent direct reading of the password. Attempting to read `user.password` will raise an AttributeError.
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
        # Hashes the plain-text password and stores it in password_hash. This allows you to do `user.password = "mysecretpassword"`.
        self.password_hash = generate_password_hash(password)
    # Method to check password (you likely already have this or check_password)
    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)
    # 비밀번호 체크
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    # Flask-Login required methods
    @property
    def is_authenticated(self):
        return True
    @property
    def is_active(self):
        return True
    @property
    def is_anonymous(self):
        return False
    def __repr__(self):
        return f'<User {self.username}>'
    # 이메일 중복 체크
    def is_duplicate_email(self):
        return User.query.filter_by(email=self.email).first() is not None
    # flask-login에서 사용자 ID를 문자열로 반환하기 위한 함수
    # 이 함수는 Flask-Login이 사용자 객체를 로드할 때 사용됨
    def get_id(self):
        return str(self.id)
    # 현재 로그인하고 있는 사용자 정보 취득 함수 설정은 apps/__init__.py에서 정의함
class APIKey(db.Model):
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    key_string = db.Column(db.String(Config.API_KEY_LENGTH), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default= datetime.now)
    last_used = db.Column(db.DateTime)
    usage_count = db.Column(db.Integer, default=0)
    # 특정 API Key에 대한 일일/월간 사용량 제한을 위한 필드 추가 가능 (예: daily_limit, monthly_limit)
    usage_logs = db.relationship('UsageLog', backref='api_key', lazy=True, cascade="all, delete-orphan")
    def generate_key(self):
        self.key_string = str(uuid.uuid4()).replace('-', '')[:Config.API_KEY_LENGTH]
    def __repr__(self):
        return f'<APIKey {self.key_string}>'

class UsageType(enum.Enum):
    LOGIN = 'login'
    API_KEY = 'api_key'

class UsageLog(db.Model):
    __tablename__ = 'usage_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'), index=True)
    usage_type = db.Column(db.Enum(UsageType), nullable=False) # 로그인 기반 또는 API Key 기반
    login_confirm = db.Column(db.String(10), nullable=True) # 로그인 사용자의 AI 추론에 대한 결과 confirm저장 유무(확인)
    endpoint = db.Column(db.String(120), nullable=False) # 사용된 서비스 엔드포인트
    timestamp = db.Column(db.DateTime, default= datetime.now, index=True)
    # 요청 IP, 요청 바디 요약, 응답 상태 코드 등 상세 로그를 위한 필드 추가
    remote_addr = db.Column(db.String(45)) # IPv4: 15, IPv6: 45
    request_data_summary = db.Column(db.Text)
    response_status_code = db.Column(db.Integer)
    def __repr__(self):
        return f'<UsageLog {self.endpoint} Type: {self.usage_type} at {self.timestamp}>'

class IRIS(db.Model):
    __tablename__ = 'iris_results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'), index=True)
    sepal_length = db.Column(db.Float, nullable=False)
    sepal_width = db.Column(db.Float, nullable=False)
    petal_length = db.Column(db.Float, nullable=False)
    petal_width = db.Column(db.Float, nullable=False)
    predicted_class = db.Column(db.String(50)) # 붓꽃 분류 결과 (예: 'setosa', 'versicolor', 'virginica')
    # AI 모델 버전 정보 추가 (추후 모델 업데이트 시 유용)
    model_version = db.Column(db.String(20), default='1.0')
    confirmed_class = db.Column(db.String(50)) # 붓꽃 분류 결과 (예: 'setosa', 'versicolor', 'virginica')
    confirm = db.Column(db.Boolean, default=False) # 사용자가 추론 결과를 확인했는지 여부
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    def __repr__(self):
        return f'<IRIS {self.sepal_length}, {self.sepal_width}, {self.petal_length}, {self.petal_width} -> {self.predicted_class}>'