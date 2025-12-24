import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="module")
def setup_database():
    """Testlerden önce veri tabanını oluşturmak ve testlerden sonra temizlemek için kullanılan test düzeneği."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Test sırasında veri tabanı bağlantısı oluşturur ve testten sonra bağlantıyı kapatır."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Veri tabanı ve 'users' tablosunun oluşturulmasını test eder."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "The 'users' table should exist in the database."

def test_add_new_user(setup_database, connection):
    """Yeni bir kullanıcının eklenmesini test eder."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "The user should be added to the database."

def test_add_existing_user(setup_database):
    """Var olan bir kullanıcı adıyla kullanıcı eklemeye çalışmayı test eder"""
    add_user('existinguser', 'existinguser@example.com', 'password123')
    response = add_user('existinguser', 'existinguser2@example.com', 'password1234') 
    assert not response, "Aynı kullanıcı adına sahip kullanıcı kaydedilmemelidir."

def test_authenticate_user_success(setup_database):
    """Başarılı kullanıcı doğrulamasını test eder."""
    add_user('testauth', 'testauth@example.com', 'password123')
    assert authenticate_user('testauth', 'password123') == True

def test_authenticate_nonexistent_user(setup_database):
    """Var olmayan kullanıcıyla doğrulama yapmayı test eder."""
    assert authenticate_user('nonexistentuser', 'password') == False

def test_authenticate_user_wrong_password(setup_database):
    """Yanlış şifreyle doğrulama yapmayı test eder."""
    add_user('wrongpass', 'wrongpass@example.com', 'password123')
    assert authenticate_user('wrongpass', 'wrongpassword') == False

def test_display_users(setup_database, capsys):
    """Kullanıcı listesinin doğru şekilde görüntülenmesini test etme."""
    add_user('displaytest', 'displaytest@example.com', 'password123')
    display_users()
    captured = capsys.readouterr()
    assert 'displaytest' in captured.out, "Görüntüleme fonksiyonu kullanıcı adlarını çıktı vermelidir."
    assert 'password123' not in captured.out, "Şifreler çıktı verilmemelidir."