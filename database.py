import os
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from datetime import datetime

def get_db_connection():
    """Veritabanı bağlantısı - ÖNCE DATABASE_URL"""
    # 1. Önce DATABASE_URL dene (Render'da)
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print(f"✅ DATABASE_URL bulundu: {database_url[:50]}...")
        try:
            return psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        except Exception as e:
            print(f"❌ DATABASE_URL ile bağlanılamadı: {e}")
            raise e
    
    # 2. Yoksa yerel bağlantı dene
    print("⚠️ DATABASE_URL yok, yerel bağlantı deneniyor...")
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'yolo_userdb'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
        cursor_factory=RealDictCursor
    )

def init_db():
    """Tabloları oluştur"""
    try:
        print("🔄 Veritabanı başlatılıyor...")
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
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Admin kullanıcı
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@yolo.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'Admin123!')
        
        cur.execute("SELECT id FROM users WHERE email = %s", (admin_email,))
        if not cur.fetchone():
            hashed = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
            cur.execute('''
                INSERT INTO users (email, password_hash, is_admin)
                VALUES (%s, %s, %s)
            ''', (admin_email, hashed.decode('utf-8'), True))
            print(f"✅ Admin oluşturuldu: {admin_email}")
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Veritabanı başarıyla başlatıldı.")
    except Exception as e:
        print(f"❌ Veritabanı hatası: {e}")
        import traceback
        traceback.print_exc()
        raise e

def get_user_by_email(email):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user
    except Exception as e:
        print(f"❌ get_user_by_email hatası: {e}")
        return None

def get_all_users():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, email, phone, is_admin, created_at FROM users WHERE is_active = TRUE")
        users = cur.fetchall()
        cur.close()
        conn.close()
        return users
    except Exception as e:
        print(f"❌ get_all_users hatası: {e}")
        return []

def create_user(email, password_hash, phone, is_admin=False):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO users (email, password_hash, phone, is_admin)
        VALUES (%s, %s, %s, %s) RETURNING id
    ''', (email, password_hash, phone, is_admin))
    user_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return user_id

def delete_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_active = FALSE WHERE id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

def update_password(user_id, new_hash):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user_id))
    conn.commit()
    cur.close()
    conn.close()