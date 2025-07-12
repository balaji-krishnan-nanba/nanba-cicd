# Databricks notebook source
# MAGIC %md
# MAGIC # Load Data Notebook
# MAGIC This notebook handles loading processed data to final destinations

# COMMAND ----------

import pyspark.sql.functions as F
from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Loading Logic

# COMMAND ----------

def load_data():
    """Load processed data to final destinations"""
    try:
        print("🔄 Starting data loading...")
        
        # Read processed data
        processed_path = "/tmp/processed/clean_data"
        processed_data = spark.read.parquet(processed_path)
        
        # Create database if not exists
        database_name = f"nanba_cicd_{spark.conf.get('spark.databricks.clusterUsageTags.clusterTargetWorkerEnvironment', 'dev')}"
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        spark.sql(f"USE {database_name}")
        
        # Load to Delta table
        table_name = "processed_data"
        processed_data.write.format("delta") \
                     .mode("overwrite") \
                     .option("overwriteSchema", "true") \
                     .saveAsTable(table_name)
        
        # Verify loading
        loaded_count = spark.sql(f"SELECT COUNT(*) as count FROM {table_name}").collect()[0]["count"]
        print(f"✅ Loaded {loaded_count} records to {database_name}.{table_name}")
        
        # Create summary statistics table
        summary_stats = processed_data.groupBy("category", "value_category") \
                                     .agg(F.count("*").alias("record_count"),
                                          F.avg("value").alias("avg_value"),
                                          F.min("value").alias("min_value"),
                                          F.max("value").alias("max_value"))
        
        summary_stats.write.format("delta") \
                    .mode("overwrite") \
                    .option("overwriteSchema", "true") \
                    .saveAsTable("data_summary")
        
        print("📊 Summary statistics:")
        summary_stats.show()
        
        # Data lineage information
        print(f"📈 Data pipeline completed:")
        print(f"  - Database: {database_name}")
        print(f"  - Main table: {table_name}")
        print(f"  - Summary table: data_summary")
        print(f"  - Processing date: {F.current_date()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data loading failed: {str(e)}")
        raise e

# COMMAND ----------

# Execute loading
result = load_data()
print("🎉 Data loading completed successfully!")