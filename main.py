# from app import app

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5001, debug=True)

from app import app
import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5001)),
        debug=False,
        use_reloader=False
    )


