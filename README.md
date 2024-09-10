## 개발 환경
- Python 3.11
- Django 4.2
- Djagno REST Framework
- Postgresql

## 필요한 패키지 목록
- requirements.txt

## 추가 필요 파일
- root/.env
```
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```
- root/secrets.json
```json
{
  "SECRET_KEY": "django-insecure-)@n))55gv=xay1tr2s4a^8$%v&yj%=&8yz$y=vt%%uv15s4s)y"
}
```

## 테스트 데이터
```
python create_test_data.py
```