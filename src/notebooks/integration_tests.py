# Databricks notebook source
# MAGIC %md
# MAGIC # Integration Tests
# MAGIC This notebook runs integration tests for the test environment

# COMMAND ----------

import pyspark.sql.functions as F
from pyspark.sql import SparkSession
import time

spark = SparkSession.getActiveSession()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Pipeline Integration Tests

# COMMAND ----------

def test_data_ingestion():
    """Test data ingestion functionality"""
    try:
        # Create sample source data
        source_data = spark.range(1000).withColumn("timestamp", F.current_timestamp()) \
                          .withColumn("value", F.rand() * 100)
        
        # Write to staging area
        source_data.write.format("delta").mode("overwrite") \
                  .option("path", "/tmp/integration_test/staging") \
                  .saveAsTable("test_staging.raw_data")
        
        # Verify data was written
        staging_count = spark.sql("SELECT COUNT(*) as count FROM test_staging.raw_data").collect()[0]["count"]
        assert staging_count == 1000, f"Expected 1000 rows in staging, got {staging_count}"
        
        print("✅ Data ingestion test passed")
        return True
    except Exception as e:
        print(f"❌ Data ingestion test failed: {str(e)}")
        return False

# COMMAND ----------

def test_data_transformation():
    """Test data transformation functionality"""
    try:
        # Read from staging
        staging_df = spark.sql("SELECT * FROM test_staging.raw_data")
        
        # Apply transformations
        transformed_df = staging_df.withColumn("value_category", 
                                              F.when(F.col("value") < 25, "low")
                                               .when(F.col("value") < 75, "medium")
                                               .otherwise("high")) \
                                  .withColumn("processing_date", F.current_date())
        
        # Write to processed area
        transformed_df.write.format("delta").mode("overwrite") \
                      .option("path", "/tmp/integration_test/processed") \
                      .saveAsTable("test_processed.clean_data")
        
        # Verify transformation
        category_counts = spark.sql("""
            SELECT value_category, COUNT(*) as count 
            FROM test_processed.clean_data 
            GROUP BY value_category
        """).collect()
        
        total_processed = sum([row["count"] for row in category_counts])
        assert total_processed == 1000, f"Expected 1000 processed rows, got {total_processed}"
        
        print("✅ Data transformation test passed")
        return True
    except Exception as e:
        print(f"❌ Data transformation test failed: {str(e)}")
        return False

# COMMAND ----------

def test_data_quality():
    """Test data quality checks"""
    try:
        # Check for null values
        null_count = spark.sql("""
            SELECT COUNT(*) as null_count 
            FROM test_processed.clean_data 
            WHERE value IS NULL OR value_category IS NULL
        """).collect()[0]["null_count"]
        
        assert null_count == 0, f"Found {null_count} null values in processed data"
        
        # Check data ranges
        value_stats = spark.sql("""
            SELECT MIN(value) as min_val, MAX(value) as max_val 
            FROM test_processed.clean_data
        """).collect()[0]
        
        assert 0 <= value_stats["min_val"] <= 100, f"Value out of range: {value_stats['min_val']}"
        assert 0 <= value_stats["max_val"] <= 100, f"Value out of range: {value_stats['max_val']}"
        
        print("✅ Data quality test passed")
        return True
    except Exception as e:
        print(f"❌ Data quality test failed: {str(e)}")
        return False

# COMMAND ----------

# Run all integration tests
print("🚀 Starting integration tests...")

tests = [
    ("Data Ingestion", test_data_ingestion),
    ("Data Transformation", test_data_transformation),
    ("Data Quality", test_data_quality)
]

results = []
for test_name, test_func in tests:
    print(f"\n📋 Running {test_name} test...")
    result = test_func()
    results.append((test_name, result))

# COMMAND ----------

# Cleanup test data
try:
    spark.sql("DROP TABLE IF EXISTS test_staging.raw_data")
    spark.sql("DROP TABLE IF EXISTS test_processed.clean_data")
    spark.sql("DROP DATABASE IF EXISTS test_staging")
    spark.sql("DROP DATABASE IF EXISTS test_processed")
    print("🧹 Test cleanup completed")
except:
    pass

# COMMAND ----------

# Summary
print("\n📊 Integration Test Results:")
print("=" * 40)
passed = 0
for test_name, result in results:
    status = "✅ PASSED" if result else "❌ FAILED"
    print(f"{test_name}: {status}")
    if result:
        passed += 1

print(f"\nOverall: {passed}/{len(tests)} tests passed")

if passed == len(tests):
    print("🎉 All integration tests passed!")
else:
    raise Exception(f"Integration tests failed: {len(tests) - passed} out of {len(tests)} tests failed")