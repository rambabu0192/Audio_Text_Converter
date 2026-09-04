import mysql.connector
import bcrypt


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="ram123",
        database="audio_text_db"
    )

    return connection


# ==========================================
# FORMAT LANGUAGE
# ==========================================

def format_language(language):

    language_map = {
        "en": "English",
        "hi": "Hindi",
        "te": "Telugu",

        "English": "English",
        "Hindi": "Hindi",
        "Telugu": "Telugu",

        "English 🇬🇧": "English",
        "Hindi 🇮🇳": "Hindi",
        "Telugu 🇮🇳": "Telugu"
    }

    if language is None:
        return "Unknown"

    return language_map.get(
        language.strip(),
        language.strip()
    )


# ==========================================
# CREATE USER / SIGNUP
# ==========================================

def create_user(name, email, password):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        # Hash password
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        query = """
        INSERT INTO users
        (
            name,
            email,
            password
        )
        VALUES (%s, %s, %s)
        """

        cursor.execute(
            query,
            (
                name.strip(),
                email.strip().lower(),
                hashed_password
            )
        )

        connection.commit()

        return True, "Account created successfully!"

    except mysql.connector.IntegrityError:

        return False, "Email already registered!"

    except Exception as e:

        return False, f"Error: {str(e)}"

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# USER LOGIN
# ==========================================

def login_user(email, password):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
        SELECT *
        FROM users
        WHERE email = %s
        """

        cursor.execute(
            query,
            (email.strip().lower(),)
        )

        user = cursor.fetchone()

        if user:

            stored_password = user["password"]

            if bcrypt.checkpw(
                password.encode("utf-8"),
                stored_password.encode("utf-8")
            ):

                return user

        return None

    except Exception as e:

        print("Login Error:", e)

        return None

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# SAVE CONVERSION
# ==========================================

def save_conversion(
    user_id,
    conversion_type,
    input_text=None,
    output_text=None,
    language=None,
    audio_file=None
):

    connection = None
    cursor = None

    try:

        # Convert language code to clean name
        language = format_language(language)

        connection = get_connection()

        cursor = connection.cursor()

        query = """
        INSERT INTO conversions
        (
            user_id,
            conversion_type,
            input_text,
            output_text,
            language,
            audio_file
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            user_id,
            conversion_type,
            input_text,
            output_text,
            language,
            audio_file
        )

        cursor.execute(
            query,
            values
        )

        connection.commit()

        # Get inserted ID
        conversion_id = cursor.lastrowid

        return conversion_id

    except Exception as e:

        print("Save Conversion Error:", e)

        return None

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# UPDATE CONVERSION TEXT
# ==========================================

def update_conversion(
    conversion_id,
    output_text
):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        query = """
        UPDATE conversions
        SET output_text = %s
        WHERE id = %s
        """

        cursor.execute(
            query,
            (
                output_text,
                conversion_id
            )
        )

        connection.commit()

        return True

    except Exception as e:

        print("Update Error:", e)

        return False

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# GET USER CONVERSIONS
# ==========================================

def get_conversions(user_id):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
        SELECT *
        FROM conversions
        WHERE user_id = %s
        ORDER BY created_at DESC
        """

        cursor.execute(
            query,
            (user_id,)
        )

        conversions = cursor.fetchall()

        return conversions

    except Exception as e:

        print("History Error:", e)

        return []

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# DASHBOARD STATISTICS
# ==========================================

def get_dashboard_stats(user_id):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # Total conversions
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM conversions
            WHERE user_id = %s
            """,
            (user_id,)
        )

        total = cursor.fetchone()["total"]


        # Audio to Text
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM conversions
            WHERE user_id = %s
            AND conversion_type = 'Audio to Text'
            """,
            (user_id,)
        )

        audio_to_text = cursor.fetchone()["total"]


        # Text to Audio
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM conversions
            WHERE user_id = %s
            AND conversion_type = 'Text to Audio'
            """,
            (user_id,)
        )

        text_to_audio = cursor.fetchone()["total"]


        # Most used language
        cursor.execute(
            """
            SELECT
                language,
                COUNT(*) AS total
            FROM conversions
            WHERE user_id = %s
            AND language IS NOT NULL
            GROUP BY language
            ORDER BY total DESC
            LIMIT 1
            """,
            (user_id,)
        )

        language_result = cursor.fetchone()

        if language_result:

            most_used_language = (
                language_result["language"]
            )

        else:

            most_used_language = "No Data"


        return {
            "total": total,
            "audio_to_text": audio_to_text,
            "text_to_audio": text_to_audio,
            "most_used_language": most_used_language
        }

    except Exception as e:

        print("Dashboard Error:", e)

        return {
            "total": 0,
            "audio_to_text": 0,
            "text_to_audio": 0,
            "most_used_language": "No Data"
        }

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# CONVERSION TYPE CHART DATA
# ==========================================

def get_conversion_chart_data(user_id):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
        SELECT
            conversion_type,
            COUNT(*) AS total
        FROM conversions
        WHERE user_id = %s
        GROUP BY conversion_type
        ORDER BY total DESC
        """

        cursor.execute(
            query,
            (user_id,)
        )

        data = cursor.fetchall()

        return data

    except Exception as e:

        print("Conversion Chart Error:", e)

        return []

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# LANGUAGE CHART DATA
# ==========================================

def get_language_chart_data(user_id):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
        SELECT
            language,
            COUNT(*) AS total
        FROM conversions
        WHERE user_id = %s
        AND language IS NOT NULL
        GROUP BY language
        ORDER BY total DESC
        """

        cursor.execute(
            query,
            (user_id,)
        )

        data = cursor.fetchall()

        return data

    except Exception as e:

        print("Language Chart Error:", e)

        return []

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
            
# ==========================================
# DELETE SINGLE CONVERSION
# ==========================================

def delete_conversion(conversion_id, user_id):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # Get audio file path first
        cursor.execute(
            """
            SELECT audio_file
            FROM conversions
            WHERE id = %s AND user_id = %s
            """,
            (conversion_id, user_id)
        )

        conversion = cursor.fetchone()

        # Conversion not found
        if not conversion:

            return False, None


        audio_file = conversion["audio_file"]


        # Delete database record
        cursor.execute(
            """
            DELETE FROM conversions
            WHERE id = %s AND user_id = %s
            """,
            (conversion_id, user_id)
        )

        connection.commit()

        return True, audio_file


    except Exception as e:

        print("Delete Conversion Error:", e)

        return False, None


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
            
# ==========================================
# DELETE ALL USER CONVERSIONS
# ==========================================

def delete_all_conversions(user_id):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # Get all audio file paths first
        cursor.execute(
            """
            SELECT audio_file
            FROM conversions
            WHERE user_id = %s
            """,
            (user_id,)
        )

        conversions = cursor.fetchall()

        audio_files = [
            item["audio_file"]
            for item in conversions
            if item["audio_file"]
        ]


        # Delete all database records
        cursor.execute(
            """
            DELETE FROM conversions
            WHERE user_id = %s
            """,
            (user_id,)
        )

        connection.commit()

        return True, audio_files


    except Exception as e:

        print("Delete All History Error:", e)

        return False, []


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()