import os
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from datetime import datetime
import re

def get_db_connection():
    """Veritabanı bağlantısı oluştur - Render için"""
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Render PostgreSQL bağlantısı
        print(f"✅ Render PostgreSQL kullanılıyor")
        return psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    else:
        # Yerel geliştirme için
        print(f"✅ Yerel PostgreSQL kullanılıyor")
        return psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'yolo_userdb'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres'),
            cursor_factory=RealDictCursor
        )

def init_db():
    """Veritabanı tablolarını oluştur"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Users tablosu
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                phone VARCHAR(20),
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Login logları
        cur.execute('''
            CREATE TABLE IF NOT EXISTS login_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                ip_address VARCHAR(45),
                user_agent TEXT,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN
            )
        ''')
        
        # Admin kullanıcıyı oluştur
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@yolo.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'Admin123!')
        
        cur.execute("SELECT id FROM users WHERE email = %s", (admin_email,))
        admin_exists = cur.fetchone()
        
        if not admin_exists:
            hashed = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
            cur.execute('''
                INSERT INTO users (email, password_hash, is_admin)
                VALUES (%s, %s, %s)
            ''', (admin_email, hashed.decode('utf-8'), True))
            print(f"✅ Admin kullanıcı oluşturuldu: {admin_email}")
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Veritabanı başarıyla başlatıldı.")
    except Exception as e:
        print(f"❌ Veritabanı hatası: {e}")
        raise e

def get_user_by_email(email):
    """Email ile kullanıcı ara"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def create_user(email, password_hash, phone, is_admin=False):
    """Yeni kullanıcı oluştur"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO users (email, password_hash, phone, is_admin)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    ''', (email, password_hash, phone, is_admin))
    user_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return user_id

def delete_user(user_id):
    """Kullanıcı sil (soft delete)"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_active = FALSE WHERE id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

def update_password(user_id, new_password_hash):
    """Kullanıcı şifresini güncelle"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        UPDATE users 
        SET password_hash = %s, updated_at = CURRENT_TIMESTAMP 
        WHERE id = %s
    ''', (new_password_hash, user_id))
    conn.commit()
    cur.close()
    conn.close()

def get_all_users():
    """Tüm aktif kullanıcıları getir"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT id, email, phone, is_admin, created_at, updated_at, last_login 
        FROM users 
        WHERE is_active = TRUE
        ORDER BY created_at DESC
    ''')
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

def log_login(user_id, ip, user_agent, success):
    """Login girişimini logla"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO login_logs (user_id, ip_address, user_agent, success)
        VALUES (%s, %s, %s, %s)
    ''', (user_id, ip, user_agent, success))
    conn.commit()
    cur.close()
    conn.close()