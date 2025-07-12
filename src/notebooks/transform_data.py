# Databricks notebook source
# MAGIC %md
# MAGIC # Transform Data Notebook
# MAGIC This notebook handles data transformation and cleansing

# COMMAND ----------

import pyspark.sql.functions as F
from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Transformation Logic

# COMMAND ----------

def transform_data():
    """Transform and cleanse extracted data"""
    try:
        print("🔄 Starting data transformation...")
        
        # Read from staging
        staging_path = "/tmp/staging/raw_data"
        raw_data = spark.read.parquet(staging_path)
        
        # Apply transformations
        transformed_data = raw_data.withColumn("value_rounded", F.round(F.col("value"), 2)) \
                                  .withColumn("value_category", 
                                            F.when(F.col("value") < 25, "low")
                                             .when(F.col("value") < 75, "medium")
                                             .otherwise("high")) \
                                  .withColumn("processing_date", F.current_date()) \
                                  .withColumn("is_weekend", 
                                            F.when(F.dayofweek(F.col("timestamp")).isin([1, 7]), True)
                                             .otherwise(False))
        
        # Data quality checks
        null_count = transformed_data.filter(F.col("value").isNull()).count()
        if null_count > 0:
            raise Exception(f"Found {null_count} null values in data")
        
        # Write to processed area
        processed_path = "/tmp/processed/clean_data"
        transformed_data.write.mode("overwrite").parquet(processed_path)
        
        # Verify transformation
        processed_count = spark.read.parquet(processed_path).count()
        print(f"✅ Transformed {processed_count} records to {processed_path}")
        
        # Show sample of transformed data
        print("📊 Sample transformed data:")
        transformed_data.show(5)
        
        return True
        
    except Exception as e:
        print(f"❌ Data transformation failed: {str(e)}")
        raise e

# COMMAND ----------

# Execute transformation
result = transform_data()
print("🎉 Data transformation completed successfully!")