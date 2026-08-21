import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database.session import SessionLocal, engine
from app.database.base import Base

from test_classification import test_classification
from test_behavior_intelligence_engine import test_behavior_intelligence_engine
from test_monitoring_rule_engine import test_monitoring_rule_engine
from test_onboarding_workflow import test_onboarding_workflow
from test_production_dashboards import test_production_dashboards
from test_ai_prediction_engine import test_ai_prediction_engine

def run_master_production_test_suite():
    print("\n==========================================================================================")
    print("        STUDIQ MASTER PRODUCTION READINESS & SECURITY TEST SUITE                          ")
    print("==========================================================================================")

    print("\n---> [TEST PHASE 1/6] Running Telemetry Classification Engine Verification...")
    test_classification()

    print("\n---> [TEST PHASE 2/6] Running AI Behavior Intelligence Engine Verification...")
    test_behavior_intelligence_engine()

    print("\n---> [TEST PHASE 3/6] Running Intelligent Monitoring Rule Engine Verification...")
    test_monitoring_rule_engine()

    print("\n---> [TEST PHASE 4/6] Running Interlinked Role Workflow & Approval Verification...")
    test_onboarding_workflow()

    print("\n---> [TEST PHASE 5/6] Running Live Dashboards & Export APIs Verification...")
    test_production_dashboards()

    print("\n---> [TEST PHASE 6/6] Running AI Risk Prediction & Recommendation Engine Verification...")
    test_ai_prediction_engine()

    print("==========================================================================================")
    print("SUCCESS: ALL 6 MASTER PRODUCTION SUITE PHASES PASSED WITH 100% SUCCESS!")
    print("   StudIQ Platform is Fully Production-Ready, Secure, and Architecturally Verified.")
    print("==========================================================================================\n")


if __name__ == "__main__":
    run_master_production_test_suite()
