#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.schemas import RiskItem, RiskLevel
from agents.verification_agent import VerificationAgent

# Create a test risk item
risk = RiskItem(
    id="test-1",
    level=RiskLevel.HIGH,
    title="Test Risk",
    description="Test description",
    service_affected="aws-ec2",
    recommendation="Test recommendation"
)

print(f"Risk type: {type(risk)}")
print(f"Risk attributes: {dir(risk)}")

# Test the verification agent
agent = VerificationAgent()

try:
    result = agent.process(
        "@startdiagram\naws-ec2 web-server -> aws-rds database\n@enddiagram",
        [risk]
    )
    print("Success!")
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

