import os

MODE = os.environ.get("MODE", "local")  # local or production
ORS_API_KEY = os.environ.get("ORS_API_KEY", "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImQxNDRjZTQ5ZTg4YjQ3MTRhNzRjYzY0ODdlZjJlN2UyIiwiaCI6Im11cm11cjY0In0=")

# 本番用APIキー（必要なら）
#GOOGLE_VISION_KEY = os.environ.get("GOOGLE_VISION_KEY", "")
#ORS_API_KEY = os.environ.get("ORS_API_KEY", "")