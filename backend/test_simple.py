import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("STEP 1: Starting script", flush=True)

from app.database.session import SessionLocal
print("STEP 2: SessionLocal imported", flush=True)

from app.routers.auth_router import login, register_student
print("STEP 3: auth_router imported", flush=True)

from test_auth_flow import run_tests
print("STEP 4: Running full test suite", flush=True)
run_tests()
print("STEP 5: Done", flush=True)
