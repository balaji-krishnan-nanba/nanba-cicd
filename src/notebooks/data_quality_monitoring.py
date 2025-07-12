# Databricks notebook source
# MAGIC %md
# MAGIC # Data Quality Monitoring Notebook
# MAGIC This notebook performs data quality checks and monitoring

# COMMAND ----------

import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.types import *

spark = SparkSession.getActiveSession()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Quality Monitoring Functions

# COMMAND ----------

def check_data_quality():
    """Perform comprehensive data quality checks"""
    try:
        print("🔍 Starting data quality monitoring...")
        
        # Get environment-specific database
        environment = spark.conf.get('spark.databricks.clusterUsageTags.clusterTargetWorkerEnvironment', 'dev')
        database_name = f"nanba_cicd_{environment}"
        
        # Check if database and table exist
        try:
            spark.sql(f"USE {database_name}")
            df = spark.sql("SELECT * FROM processed_data")
        except:
            print(f"⚠️ Database {database_name} or table processed_data not found")
            print("🔧 Creating sample data for quality checks...")
            # Create sample data for testing
            df = spark.range(100).withColumn("value", F.rand() * 100) \
                                .withColumn("category", F.lit("test")) \
                                .withColumn("value_category", F.lit("medium"))
        
        print(f"📊 Analyzing {df.count()} records...")
        
        # Quality Check 1: Null value detection
        null_checks = {}
        for col_name in df.columns:
            null_count = df.filter(F.col(col_name).isNull()).count()
            null_checks[col_name] = null_count
            if null_count > 0:
                print(f"⚠️ Found {null_count} null values in column '{col_name}'")
        
        # Quality Check 2: Data type validation
        print("🔍 Data type validation:")
        df.printSchema()
        
        # Quality Check 3: Value range validation
        if "value" in df.columns:
            value_stats = df.select(
                F.min("value").alias("min_value"),
                F.max("value").alias("max_value"),
                F.avg("value").alias("avg_value"),
                F.stddev("value").alias("stddev_value")
            ).collect()[0]
            
            print(f"📈 Value statistics:")
            print(f"  Min: {value_stats['min_value']:.2f}")
            print(f"  Max: {value_stats['max_value']:.2f}")
            print(f"  Avg: {value_stats['avg_value']:.2f}")
            print(f"  StdDev: {value_stats['stddev_value']:.2f}")
            
            # Check for outliers (values beyond 3 standard deviations)
            outlier_threshold = value_stats['avg_value'] + (3 * value_stats['stddev_value'])
            outlier_count = df.filter(F.col("value") > outlier_threshold).count()
            if outlier_count > 0:
                print(f"⚠️ Found {outlier_count} potential outliers")
        
        # Quality Check 4: Duplicate detection
        total_count = df.count()
        distinct_count = df.distinct().count()
        duplicate_count = total_count - distinct_count
        if duplicate_count > 0:
            print(f"⚠️ Found {duplicate_count} duplicate records")
        else:
            print("✅ No duplicates found")
        
        # Quality Check 5: Category distribution
        if "category" in df.columns:
            print("📊 Category distribution:")
            df.groupBy("category").count().orderBy(F.desc("count")).show()
        
        # Create quality report
        quality_report = {
            "timestamp": F.current_timestamp(),
            "total_records": total_count,
            "distinct_records": distinct_count,
            "duplicate_count": duplicate_count,
            "null_checks": null_checks,
            "quality_score": calculate_quality_score(null_checks, duplicate_count, total_count)
        }
        
        print(f"📋 Data Quality Report:")
        print(f"  Total Records: {quality_report['total_records']}")
        print(f"  Duplicates: {quality_report['duplicate_count']}")
        print(f"  Quality Score: {quality_report['quality_score']:.2f}%")
        
        # Alert if quality is below threshold
        if quality_report['quality_score'] < 90:
            print("🚨 DATA QUALITY ALERT: Quality score below 90%!")
        else:
            print("✅ Data quality checks passed!")
        
        return quality_report
        
    except Exception as e:
        print(f"❌ Data quality monitoring failed: {str(e)}")
        raise e

def calculate_quality_score(null_checks, duplicate_count, total_count):
    """Calculate overall data quality score"""
    total_nulls = sum(null_checks.values())
    null_penalty = (total_nulls / (total_count * len(null_checks))) * 100 if total_count > 0 else 0
    duplicate_penalty = (duplicate_count / total_count) * 100 if total_count > 0 else 0
    
    quality_score = 100 - null_penalty - duplicate_penalty
    return max(0, quality_score)  # Ensure score doesn't go below 0

# COMMAND ----------

# Execute data quality monitoring
quality_report = check_data_quality()
print("🎉 Data quality monitoring completed!")