import psutil

sessions = psutil.users()

print("yes" if not sessions else "no")
