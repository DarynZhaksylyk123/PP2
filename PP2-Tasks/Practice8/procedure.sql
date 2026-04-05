CREATE OR REPLACE PROCEDURE upsert(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql as $$
BEGIN 
    IF EXISTS (SELECT 1 FROM contacts WHERE name = p_name) THEN
        UPDATE contacts SET phone = p_phone WHERE name = p_name;
    ELSE
        INSERT INTO contacts(name, phone) VALUES(p_phone, p_name);
    END IF;
END;
$$;


CREATE OR REPLACE PROCEDURE many_contacts(name TEXT[], phone TEXT[])
LANGUAGE plpgsql AS $$
DECLARE
     i INT;
    invalid_data TEXT := '';
BEGIN
    FOR i IN 1..array_length(names, 1) LOOP

        IF phones[i] ~ '^[0-9]+$' AND length(phones[i]) >= 10 THEN
            
            INSERT INTO contacts(name, phone)
            VALUES(names[i], phones[i]);
        
        ELSE
            invalid_data := invalid_data || 
                names[i] || ' ' || ' -> ' || phones[i] || E'\n';
        END IF;

    END LOOP;

    RAISE NOTICE 'Invalid data:\n%', invalid_data;

END;
$$;

CREATE OR REPLACE PROCEDURE d_contact(p_value TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM contacts WHERE name = p_value OR phone = p_value;

END;
$$;
