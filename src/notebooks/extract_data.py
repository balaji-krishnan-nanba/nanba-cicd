# Databricks notebook source
# MAGIC %md
# MAGIC # Extract Data Notebook
# MAGIC This notebook handles data extraction from various sources

# COMMAND ----------

import pyspark.sql.functions as F
from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Extraction Logic

# COMMAND ----------

def extract_sample_data():
    """Extract sample data for processing pipeline"""
    try:
        # Create sample source data
        print("🔄 Starting data extraction...")
        
        source_data = spark.range(1000).withColumn("timestamp", F.current_timestamp()) \
                          .withColumn("value", F.rand() * 100) \
                          .withColumn("category", 
                                    F.when(F.col("id") % 3 == 0, "A")
                                     .when(F.col("id") % 3 == 1, "B")
                                     .otherwise("C"))
        
        # Write to staging area
        staging_path = "/tmp/staging/raw_data"
        source_data.write.mode("overwrite").parquet(staging_path)
        
        # Verify extraction
        extracted_count = spark.read.parquet(staging_path).count()
        print(f"✅ Extracted {extracted_count} records to {staging_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data extraction failed: {str(e)}")
        raise e

# COMMAND ----------

# Execute extraction
result = extract_sample_data()
print("🎉 Data extraction completed successfully!")