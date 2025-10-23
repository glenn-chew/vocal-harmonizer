#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.schemas import RiskItem, RiskLevel

# Test the conversion
risk_dict = {
    "id": "risk-1",
    "level": "high",
    "title": "Test Risk",
    "description": "Test description",
    "service_affected": "aws-ec2",
    "recommendation": "Test recommendation"
}

print(f"Risk dict: {risk_dict}")
print(f"Risk dict level type: {type(risk_dict['level'])}")

try:
    risk_item = RiskItem(
        id=risk_dict.get("id", ""),
        level=RiskLevel(risk_dict["level"]),
        title=risk_dict["title"],
        description=risk_dict["description"],
        service_affected=risk_dict.get("service_affected"),
        recommendation=risk_dict["recommendation"],
        compliance_rule=risk_dict.get("compliance_rule")
    )
    print(f"Risk item created successfully: {risk_item}")
    print(f"Risk item level: {risk_item.level}")
    print(f"Risk item level type: {type(risk_item.level)}")
except Exception as e:
    print(f"Error creating RiskItem: {e}")
    import traceback
    traceback.print_exc()

