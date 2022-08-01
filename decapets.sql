-- SQL FOR CREATING TABLES FOR THE DECAPETS APP


            CREATE TABLE subcategory (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                name TEXT,
                category_id INTEGER,
                FOREIGN KEY(category_id) REFERENCES category(id)
                
            );

            CREATE TABLE category (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                name TEXT
                
            );

            CREATE TABLE user (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_name TEXT,
                password TEXT,
                email TEXT UNIQUE,
                role TEXT,
                registration_date TEXT
            );

            --if we are creating separate table for the staff
            CREATE TABLE admin (
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES user(id)
            );

            CREATE TABLE booking (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_id INTEGER,
                cart_id INTEGER,
                booking_status TEXT,
                booking_status_report TEXT,
                payment_status TEXT,
                booking_status_date TEXT,
                booking_address TEXT,
                total_cost CURRENCY,
                FOREIGN KEY(cart_id) REFERENCES cart(id),
                FOREIGN KEY(user_id) REFERENCES user(id)
            );


            CREATE TABLE cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_id INTEGER,
                cart_date TEXT,
                total_cost CURRENCY,
                FOREIGN KEY(user_id) REFERENCES user(id)
            );

            --keeping record of every pet in a cart
            CREATE TABLE cart_pet (
                cart_id INTEGER,
                pet_id INTEGER,
                pet_quantity INTEGER,
                FOREIGN KEY(cart_id) REFERENCES cart(id),
                FOREIGN KEY(pet_id) REFERENCES pet(id)
            );


            CREATE TABLE pet(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                pet_name TEXT,
                category_id INTEGER,
                subcategory_id INTEGER,
                shelter_home_id INTEGER,
                user_id INTEGER,
                pet_description TEXT,
                age TEXT,
                price CURRENCY DEFAULT 0,
                pet_status TEXT,
                pet_image_url TEXT,
                upload_date TEXT,
                FOREIGN KEY(category_id) REFERENCES category(id),
                FOREIGN KEY(user_id) REFERENCES user(id),
                FOREIGN KEY(subcategory_id) REFERENCES subcategory(id),
                FOREIGN KEY(shelter_home_id) REFERENCES shelter_home(id)
            );

            CREATE TABLE shelter_home(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                shelter_home_name TEXT,
                email TEXT UNIQUE,
                description TEXT,
                address TEXT,
                registration_date TEXT
            );



            CREATE TABLE pet_report(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                pet_name TEXT,
                user_id INTEGER,
                category_id INTEGER,
                subcategory_id INTEGER,
                shelter_home_id INTEGER,
                description TEXT,
                age TEXT,
                pet_status TEXT,
                pet_status_comment TEXT,
                address TEXT,
                pet_image_url TEXT,
                upload_date TEXT,
                FOREIGN KEY(category_id) REFERENCES category(id),
                FOREIGN KEY(subcategory_id) REFERENCES subcategory(id),
                FOREIGN KEY(shelter_home_id) REFERENCES shelter_home(id),
                FOREIGN KEY(user_id) REFERENCES user(id)
            );
