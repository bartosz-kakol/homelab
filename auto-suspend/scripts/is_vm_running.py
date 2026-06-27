import requests as req

response = req.get("http://localhost:5156/domain/win11")
response.raise_for_status()
text = response.text.strip().lower()

print("yes" if text == "shut off" else "no")
