from dotenv import load_dotenv
load_dotenv()  # Loads environment variables from .env

from app import app, db
from sqlalchemy import text
import routes  # noqa: F401

import schedule
import time
import threading
import os
from predict_disorder import run_disorder_prediction


#Weekly prediction scheduler function:
def start_scheduler():
    schedule.every(7).days.do(run_disorder_prediction)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    try:
        with app.app_context():
            # Use text() function to properly format the SQL query
            result = db.session.execute(text('SELECT 1'))
            print(f"Database connection successful! Result: {result.scalar()}")
    except Exception as e:
        print(f"Database connection failed: {str(e)}")


    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    
app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)