# Databricks notebook source
# MAGIC %md
# MAGIC # Validation Notebook
# MAGIC This notebook runs validation checks for the development environment

# COMMAND ----------

import pyspark.sql.functions as F
from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Environment Validation

# COMMAND ----------

# Test basic Spark functionality
test_df = spark.range(10).withColumn("test_col", F.lit("validation"))
assert test_df.count() == 10, "Basic Spark test failed"
print("✅ Basic Spark functionality validated")

# COMMAND ----------

# Test Delta Lake functionality
try:
    spark.sql("CREATE DATABASE IF NOT EXISTS dev_validation")
    spark.sql("USE dev_validation")
    
    test_df.write.format("delta").mode("overwrite").saveAsTable("test_table")
    
    result_df = spark.sql("SELECT COUNT(*) as row_count FROM test_table")
    row_count = result_df.collect()[0]["row_count"]
    
    assert row_count == 10, f"Delta table test failed, expected 10 rows but got {row_count}"
    print("✅ Delta Lake functionality validated")
    
    # Cleanup
    spark.sql("DROP TABLE IF EXISTS test_table")
    
except Exception as e:
    print(f"❌ Delta Lake validation failed: {str(e)}")
    raise

# COMMAND ----------

print("🎉 All validation checks passed successfully!")