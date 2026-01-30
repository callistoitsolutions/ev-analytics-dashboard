import yaml
from sqlalchemy import create_engine, text

def upload_to_mysql(df):
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    db = config["database"]

    engine = create_engine(
        f"mysql+pymysql://{db['user']}:{db['password']}@{db['host']}/{db['name']}"
    )

    # ✅ STEP 1: DELETE OLD DATA (avoid duplicates)
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM ev_data"))
        conn.commit()

    # ✅ STEP 2: INSERT NEW DATA
    df.to_sql("ev_data", engine, if_exists="append", index=False)
