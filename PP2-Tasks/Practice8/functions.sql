CREATE OR REPLACE FUNCTION s_contacts(p TEXT)
RETURNS TABLE(name VARCHAR, phone VARCHAR) as $$
BEGIN
    RETURN QUERY SELECT c.name, c.phone FROM contacts c
    WHERE c.name ILIKE '%' || p || '%'
       OR c.phone ILIKE '%' || p || '%';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION paginated(limitc INT, offsetc INT)
RETURNS TABLE(name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY SELECT c.name, c.phone FROM contacts c
    ORDER BY c.name
    LIMIT limitc OFFSET offsetc;
END;
$$ LANGUAGE plpgsql; 
