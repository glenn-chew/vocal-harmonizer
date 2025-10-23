"""
Test script for the Architecture Security Analysis API
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_analyze():
    """Test architecture analysis endpoint"""
    print("\nTesting architecture analysis...")
    
    # Sample diagram - simple web app with database
    test_diagram = """@startdiagram
aws-ec2 web-server -> aws-rds database
aws-s3 storage-bucket -> aws-cloudfront cdn
aws-cloudfront cdn -> aws-ec2 web-server
@enddiagram"""
    
    payload = {
        "diagram": test_diagram
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Analysis successful!")
            print(f"Risks found: {len(result['analysis']['risks'])}")
            print(f"Compliance issues: {len(result['analysis']['compliance_issues'])}")
            print(f"Overall risk score: {result['analysis']['overall_risk_score']}")
            
            # Print first few risks
            for i, risk in enumerate(result['analysis']['risks'][:3]):
                print(f"  Risk {i+1}: [{risk['level']}] {risk['title']}")
            
            return True
        else:
            print(f"Analysis failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Analysis test failed: {e}")
        return False

def test_verify():
    """Test architecture verification endpoint"""
    print("\nTesting architecture verification...")
    
    # Sample diagram with potential security issues
    test_diagram = """@startdiagram
aws-ec2 web-server -> aws-rds database
aws-s3 storage-bucket
@enddiagram"""
    
    # Sample risks (using proper Pydantic model format)
    sample_risks = [
        {
            "id": "risk-1",
            "level": "high",
            "title": "S3 Bucket Public Access",
            "description": "S3 bucket may be publicly accessible",
            "service_affected": "aws-s3",
            "recommendation": "Configure bucket policies to restrict public access",
            "compliance_rule": "S3 Public Access Control"
        }
    ]
    
    payload = {
        "original_diagram": test_diagram,
        "risks": sample_risks
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/verify",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Verification successful!")
            print(f"Changes made: {len(result['changes'])}")
            print(f"Original diagram length: {len(result['original'])}")
            print(f"Corrected diagram length: {len(result['corrected'])}")
            
            # Print changes
            for i, change in enumerate(result['changes'][:3]):
                print(f"  Change {i+1}: {change['type']} - {change['description']}")
            
            return True
        else:
            print(f"Verification failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Verification test failed: {e}")
        return False

def test_combined():
    """Test combined analyze and verify endpoint"""
    print("\nTesting combined analyze and verify...")
    
    # Sample diagram - more complex architecture
    test_diagram = """@startdiagram
aws-ec2 web-server -> aws-rds database
aws-s3 storage-bucket -> aws-cloudfront cdn
aws-lambda function -> aws-sqs queue
aws-sqs queue -> aws-lambda function
@enddiagram"""
    
    payload = {
        "diagram": test_diagram
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/analyze-and-verify",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Combined analysis successful!")
            
            analysis = result['analysis']
            verification = result['verification']
            
            print(f"Risks found: {len(analysis['risks'])}")
            print(f"Compliance issues: {len(analysis['compliance_issues'])}")
            print(f"Overall risk score: {analysis['overall_risk_score']}")
            print(f"Changes made: {len(verification['changes'])}")
            
            return True
        else:
            print(f"Combined analysis failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Combined analysis test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Architecture Security Analysis API Test Suite")
    print("=" * 50)
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health),
        ("Architecture Analysis", test_analyze),
        ("Architecture Verification", test_verify),
        ("Combined Analysis", test_combined)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = 0
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("All tests passed! 🎉")
    else:
        print("Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
