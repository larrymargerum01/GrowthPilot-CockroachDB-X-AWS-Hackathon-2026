import psycopg2

conn = psycopg2.connect(
    "postgresql://YOUR_USRNAME:<YOUR_PASSWORD>@gtm-agent-29882.j77.aws-eu-west-2.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full"
)

cur = conn.cursor()

vector = [0.0] * 1024
vector[10] = 1.0

cur.execute(
    """
    INSERT INTO vector_test (content, embedding)
    VALUES (%s, %s)
    """,
    (
        "Customers need faster support responses",
        vector
    )
)

conn.commit()

print("Inserted successfully")

cur.close()
conn.close()