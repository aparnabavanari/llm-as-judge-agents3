"""
Test script for Phase 1 Safety Net - Metric Validation

Demonstrates how the validation prevents invalid metric configurations
"""
from src.database.db_manager import DatabaseManager
from src.database.models import ComplaintType, EvaluationProfile

def test_valid_metrics():
    """Test case: Valid metric configuration (weights sum to 1.0)"""
    print("\n" + "="*80)
    print("TEST 1: Valid Metric Configuration (weights sum to 1.0)")
    print("="*80)
    
    db = DatabaseManager()
    
    # Valid metrics - weights sum to 1.0
    metrics = [
        {
            'metric_id': 'accuracy',
            'name': 'Accuracy',
            'description': 'Factual accuracy',
            'weight': 0.35,
            'scale': '1-5',
            'display_order': 1
        },
        {
            'metric_id': 'completeness',
            'name': 'Completeness',
            'description': 'Information completeness',
            'weight': 0.40,
            'scale': '1-5',
            'display_order': 2
        },
        {
            'metric_id': 'clarity',
            'name': 'Clarity',
            'description': 'Clarity and readability',
            'weight': 0.25,
            'scale': '1-5',
            'display_order': 3
        }
    ]
    
    # Get or create complaint type
    session = db.get_session()
    complaint_type = session.query(ComplaintType).filter_by(type_id='fraud').first()
    if not complaint_type:
        print("❌ Fraud complaint type not found. Please initialize database first.")
        db.close_session(session)
        return
    
    complaint_type_id = complaint_type.id
    db.close_session(session)
    
    try:
        # Create profile - should succeed
        profile = db.create_evaluation_profile(
            data={
                'complaint_type_id': complaint_type_id,
                'name': 'Test Valid Profile',
                'description': 'Test profile with valid weights'
            },
            metrics=metrics
        )
        print(f"✅ SUCCESS: Profile created with ID {profile.id}")
        print(f"   Total weight: {sum(m['weight'] for m in metrics):.3f}")
        
        # Validate the profile
        validation = db.validate_metric_profile(profile.id)
        print(f"   Validation: {'✅ PASSED' if validation['is_valid'] else '❌ FAILED'}")
        
    except ValueError as e:
        print(f"❌ FAILED: {e}")


def test_invalid_weights_sum():
    """Test case: Invalid metric configuration (weights sum > 1.0)"""
    print("\n" + "="*80)
    print("TEST 2: Invalid Metric Configuration (weights sum to 1.2)")
    print("="*80)
    
    db = DatabaseManager()
    
    # Invalid metrics - weights sum to 1.2
    metrics = [
        {
            'metric_id': 'accuracy',
            'name': 'Accuracy',
            'description': 'Factual accuracy',
            'weight': 0.35,
            'scale': '1-5',
            'display_order': 1
        },
        {
            'metric_id': 'completeness',
            'name': 'Completeness',
            'description': 'Information completeness',
            'weight': 0.40,
            'scale': '1-5',
            'display_order': 2
        },
        {
            'metric_id': 'clarity',
            'name': 'Clarity',
            'description': 'Clarity and readability',
            'weight': 0.25,
            'scale': '1-5',
            'display_order': 3
        },
        {
            'metric_id': 'urgency',
            'name': 'Urgency',
            'description': 'Urgency detection',
            'weight': 0.20,  # Adding this makes total = 1.2
            'scale': '1-5',
            'display_order': 4
        }
    ]
    
    # Get complaint type
    session = db.get_session()
    complaint_type = session.query(ComplaintType).filter_by(type_id='fraud').first()
    if not complaint_type:
        print("❌ Fraud complaint type not found. Please initialize database first.")
        db.close_session(session)
        return
    
    complaint_type_id = complaint_type.id
    db.close_session(session)
    
    try:
        # Attempt to create profile - should fail
        profile = db.create_evaluation_profile(
            data={
                'complaint_type_id': complaint_type_id,
                'name': 'Test Invalid Profile',
                'description': 'Test profile with invalid weights'
            },
            metrics=metrics
        )
        print(f"❌ UNEXPECTED: Profile created (should have failed!)")
        
    except ValueError as e:
        print(f"✅ SUCCESS: Validation prevented invalid configuration")
        print(f"   Error message: {e}")
        print(f"   Total weight attempted: {sum(m['weight'] for m in metrics):.3f}")


def test_weight_normalization_suggestions():
    """Test case: Get normalized weight suggestions"""
    print("\n" + "="*80)
    print("TEST 3: Weight Normalization Suggestions")
    print("="*80)
    
    db = DatabaseManager()
    
    # Metrics with incorrect sum
    metrics = [
        {'metric_id': 'accuracy', 'name': 'Accuracy', 'weight': 0.35},
        {'metric_id': 'completeness', 'name': 'Completeness', 'weight': 0.40},
        {'metric_id': 'clarity', 'name': 'Clarity', 'weight': 0.25},
        {'metric_id': 'urgency', 'name': 'Urgency', 'weight': 0.20}
    ]
    
    # Validate weights
    validation = db._validate_metric_weights(metrics)
    
    print(f"Current total weight: {validation['total_weight']:.3f}")
    print(f"Is valid: {validation['is_valid']}")
    
    if validation['errors']:
        print(f"\n❌ Errors:")
        for error in validation['errors']:
            print(f"   - {error}")
    
    if validation['suggested_weights']:
        print(f"\n💡 Suggested normalized weights:")
        for suggestion in validation['suggested_weights']:
            print(f"   - {suggestion['metric_id']:15s}: "
                  f"{suggestion['current_weight']:.3f} → {suggestion['suggested_weight']:.3f}")


def test_duplicate_metric_ids():
    """Test case: Duplicate metric IDs"""
    print("\n" + "="*80)
    print("TEST 4: Duplicate Metric IDs Detection")
    print("="*80)
    
    db = DatabaseManager()
    
    # Metrics with duplicate IDs
    metrics = [
        {'metric_id': 'accuracy', 'name': 'Accuracy', 'weight': 0.50},
        {'metric_id': 'accuracy', 'name': 'Accuracy 2', 'weight': 0.30},  # Duplicate!
        {'metric_id': 'clarity', 'name': 'Clarity', 'weight': 0.20}
    ]
    
    # Validate weights
    validation = db._validate_metric_weights(metrics)
    
    print(f"Is valid: {validation['is_valid']}")
    
    if validation['errors']:
        print(f"\n❌ Errors detected:")
        for error in validation['errors']:
            print(f"   - {error}")
        print("✅ SUCCESS: Duplicate metric IDs properly detected")
    else:
        print("❌ FAILED: Should have detected duplicate metric IDs")


def test_update_validation():
    """Test case: Validation on metric update"""
    print("\n" + "="*80)
    print("TEST 5: Validation on Metric Update")
    print("="*80)
    
    db = DatabaseManager()
    
    # Get an existing profile
    session = db.get_session()
    profiles = session.query(EvaluationProfile).filter(EvaluationProfile.is_active == True).all()
    db.close_session(session)
    
    if not profiles:
        print("❌ No evaluation profiles found. Run Test 1 first.")
        return
    
    profile = profiles[0]
    print(f"Testing with profile: {profile.name} (ID: {profile.id})")
    
    # Validate current state
    validation = db.validate_metric_profile(profile.id)
    print(f"\nCurrent state:")
    print(f"   Total weight: {validation['total_weight']:.3f}")
    print(f"   Metric count: {validation['metric_count']}")
    print(f"   Is valid: {validation['is_valid']}")
    
    if validation['metrics']:
        print(f"\n   Metrics:")
        for metric in validation['metrics']:
            print(f"      - {metric['metric_id']:15s}: {metric['weight']:.3f}")
    
    # Try to update a metric to break validation
    if validation['metrics']:
        first_metric = validation['metrics'][0]
        print(f"\n⚠️  Attempting to update '{first_metric['metric_id']}' weight from "
              f"{first_metric['weight']:.3f} to 0.80 (would break validation)...")
        
        try:
            db.update_evaluation_metric(
                first_metric['id'],
                {'weight': 0.80}
            )
            print("❌ UNEXPECTED: Update succeeded (should have failed!)")
        except ValueError as e:
            print(f"✅ SUCCESS: Update blocked by validation")
            print(f"   Error: {e}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("PHASE 1 SAFETY NET - METRIC VALIDATION TESTS")
    print("="*80)
    
    # Run tests
    test_valid_metrics()
    test_invalid_weights_sum()
    test_weight_normalization_suggestions()
    test_duplicate_metric_ids()
    test_update_validation()
    
    print("\n" + "="*80)
    print("TESTS COMPLETED")
    print("="*80)
    print()
