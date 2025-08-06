def migrate_catalog_complete_no_mv(old_catalog, new_catalog, managed_location):
    """
    Catalog migration excluding materialized views
    Only migrates: tables, volumes, and normal views
    """
    
    # Track migration results
    migration_results = {
        'schemas': {'success': 0, 'failed': 0},
        'managed_tables': {'success': 0, 'failed': 0},
        'external_tables': {'success': 0, 'failed': 0},
        'views': {'success': 0, 'failed': 0},
        'managed_volumes': {'success': 0, 'failed': 0},
        'external_volumes': {'success': 0, 'failed': 0},
        'functions': {'success': 0, 'failed': 0}
    }
    
    # Create new catalog if not exists
    try:
        spark.sql(f"""
            CREATE CATALOG IF NOT EXISTS `{new_catalog}`
            MANAGED LOCATION '{managed_location}'
        """)
        print(f"✓ Created catalog: {new_catalog}")
    except Exception as e:
        print(f"✗ Error creating catalog: {str(e)}")
        return
    
    # Set the current catalog context
    current_catalog = spark.sql("SELECT current_catalog()").collect()[0][0]
    
    # List all schemas
    spark.sql(f"USE CATALOG `{old_catalog}`")
    schemas = spark.sql(f"SHOW SCHEMAS").collect()
    
    for schema in schemas:
        schema_name = schema.databaseName
        
        # Skip system schemas
        if schema_name in ('information_schema', '__databricks_internal'):
            continue
        
        print(f"\n{'='*60}")
        print(f"MIGRATING SCHEMA: {schema_name}")
        print(f"{'='*60}")
        
        # Create schema with properties
        if not migrate_schema_fixed(old_catalog, new_catalog, schema_name, migration_results):
            continue
        
        # Set schema context
        spark.sql(f"USE SCHEMA `{schema_name}`")
        
        # Migrate all object types in proper order
        
        # 1. Tables first
        migrate_all_tables_fixed(old_catalog, new_catalog, schema_name, migration_results)
        
        # 2. Volumes
        migrate_volumes_fixed(old_catalog, new_catalog, schema_name, migration_results)
        
        # 3. Functions
        migrate_functions_fixed(old_catalog, new_catalog, schema_name, migration_results)
        
        # 4. Views (only normal views, not materialized)
        migrate_normal_views_only(old_catalog, new_catalog, schema_name, migration_results)
    
    # Restore original catalog
    spark.sql(f"USE CATALOG `{current_catalog}`")
    
    # Print summary
    print_migration_summary(migration_results)
    
    return migration_results

def migrate_normal_views_only(old_catalog, new_catalog, schema_name, results):
    """Migrate only normal views, skip materialized views"""
    try:
        spark.sql(f"USE CATALOG `{old_catalog}`")
        spark.sql(f"USE SCHEMA `{schema_name}`")
        
        # Get all tables and views
        all_objects = spark.sql("SHOW TABLES").collect()
        
        # Identify normal views only
        normal_views = []
        mv_count = 0
        
        for obj in all_objects:
            if not obj.isTemporary:
                table_name = obj.tableName
                try:
                    # Get the CREATE statement to check if it's a view
                    create_stmt = spark.sql(f"SHOW CREATE TABLE `{table_name}`").collect()[0].createtab_stmt
                    
                    # Check if it's a view
                    if 'CREATE VIEW' in create_stmt or 'CREATE OR REPLACE VIEW' in create_stmt:
                        # Check if it's NOT a materialized view
                        if 'MATERIALIZED VIEW' not in create_stmt:
                            normal_views.append(table_name)
                        else:
                            mv_count += 1
                            print(f"    ~ Skipping materialized view: {table_name}")
                except:
                    # If we can't get the create statement, skip
                    pass
        
        if mv_count > 0:
            print(f"\n  Skipped {mv_count} materialized views (not supported in target workspace)")
        
        # Migrate normal views
        if normal_views:
            print(f"\n  Migrating {len(normal_views)} views...")
            for view_name in normal_views:
                migrate_single_normal_view(old_catalog, new_catalog, schema_name, view_name, results)
                
    except Exception as e:
        print(f"  ! Error listing views: {str(e)}")

def migrate_single_normal_view(old_catalog, new_catalog, schema_name, view_name, results):
    """Migrate a single normal view"""
    try:
        spark.sql(f"USE CATALOG `{old_catalog}`")
        spark.sql(f"USE SCHEMA `{schema_name}`")
        
        # Get view definition
        view_def = spark.sql(f"SHOW CREATE TABLE `{view_name}`").collect()[0].createtab_stmt
        
        # Double-check it's not a materialized view
        if 'MATERIALIZED VIEW' in view_def:
            print(f"    ~ Skipping materialized view: {view_name}")
            return
        
        # Update catalog references
        view_def = view_def.replace(f"`{old_catalog}`", f"`{new_catalog}`")
        
        # Switch to new catalog
        spark.sql(f"USE CATALOG `{new_catalog}`")
        spark.sql(f"USE SCHEMA `{schema_name}`")
        
        # Check if view exists
        existing = spark.sql(f"SHOW TABLES LIKE '{view_name}'").collect()
        if existing:
            print(f"    ~ View {view_name} already exists, skipping")
            return
        
        # Create the view
        spark.sql(view_def)
        
        results['views']['success'] += 1
        print(f"    ✓ View: {view_name}")
            
    except Exception as e:
        results['views']['failed'] += 1
        print(f"    ✗ View {view_name}: {str(e)}")

def is_materialized_view(old_catalog, schema_name, object_name):
    """Check if an object is a materialized view"""
    try:
        # Try to get object type from information_schema first
        result = spark.sql(f"""
            SELECT table_type 
            FROM `{old_catalog}`.information_schema.tables 
            WHERE table_schema = '{schema_name}' 
            AND table_name = '{object_name}'
        """).collect()
        
        if result and 'MATERIALIZED' in result[0].table_type:
            return True
        
        # Fallback: check CREATE statement
        create_stmt = spark.sql(f"SHOW CREATE TABLE `{old_catalog}`.`{schema_name}`.`{object_name}`").collect()[0].createtab_stmt
        return 'MATERIALIZED VIEW' in create_stmt
    except:
        return False

def migrate_all_tables_no_mv(old_catalog, new_catalog, schema_name, results):
    """Migrate tables, excluding materialized views"""
    try:
        spark.sql(f"USE CATALOG `{old_catalog}`")
        spark.sql(f"USE SCHEMA `{schema_name}`")
        
        # Get all tables
        tables = spark.sql("SHOW TABLES").collect()
        
        # Separate by type, excluding materialized views
        managed_tables = []
        external_tables = []
        skipped_mvs = []
        
        for table in tables:
            if not table.isTemporary:
                table_name = table.tableName
                
                # Skip if it's a materialized view
                if is_materialized_view(old_catalog, schema_name, table_name):
                    skipped_mvs.append(table_name)
                    continue
                
                # Check if it's a regular view
                try:
                    create_stmt = spark.sql(f"SHOW CREATE TABLE `{table_name}`").collect()[0].createtab_stmt
                    if 'CREATE VIEW' in create_stmt and 'MATERIALIZED' not in create_stmt:
                        # It's a regular view, skip here (will be handled by view migration)
                        continue
                except:
                    pass
                
                # Get table type
                try:
                    table_type = spark.sql(f"""
                        SELECT table_type 
                        FROM `{old_catalog}`.information_schema.tables 
                        WHERE table_schema = '{schema_name}' 
                        AND table_name = '{table_name}'
                    """).collect()[0].table_type
                    
                    if table_type == 'MANAGED':
                        managed_tables.append(table_name)
                    elif table_type == 'EXTERNAL':
                        external_tables.append(table_name)
                except:
                    # Default to managed if can't determine
                    managed_tables.append(table_name)
        
        # Report skipped materialized views
        if skipped_mvs:
            print(f"\n  Skipping {len(skipped_mvs)} materialized views: {', '.join(skipped_mvs)}")
        
        # Migrate managed tables
        if managed_tables:
            print(f"\n  Migrating {len(managed_tables)} managed tables...")
            for table_name in managed_tables:
                migrate_single_table_fixed(old_catalog, new_catalog, schema_name, 
                                         table_name, 'MANAGED', results)
        
        # Migrate external tables
        if external_tables:
            print(f"\n  Migrating {len(external_tables)} external tables...")
            for table_name in external_tables:
                migrate_single_table_fixed(old_catalog, new_catalog, schema_name, 
                                         table_name, 'EXTERNAL', results)
                
    except Exception as e:
        print(f"  ! Error listing tables: {str(e)}")

# Update the print_migration_summary to exclude materialized views
def print_migration_summary_no_mv(results):
    """Print migration summary excluding materialized views"""
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)
    
    total_success = 0
    total_failed = 0
    
    # Exclude materialized_views from the summary
    for obj_type, counts in results.items():
        if obj_type == 'materialized_views':
            continue
            
        success = counts['success']
        failed = counts['failed']
        total = success + failed
        
        if total > 0:
            total_success += success
            total_failed += failed
            
            print(f"\n{obj_type.replace('_', ' ').title()}:")
            print(f"  Success: {success:3d}")
            print(f"  Failed:  {failed:3d}")
            print(f"  Total:   {total:3d}")
            if total > 0:
                print(f"  Success Rate: {(success/total)*100:.1f}%")
    
    print(f"\n{'='*60}")
    print(f"OVERALL:")
    print(f"  Total Success: {total_success}")
    print(f"  Total Failed:  {total_failed}")
    if (total_success + total_failed) > 0:
        print(f"  Overall Success Rate: {(total_success/(total_success+total_failed))*100:.1f}%")
    print(f"{'='*60}")

# Run the migration without materialized views
results = migrate_catalog_complete_no_mv(
    'cddp-dev-bronze', 
    'cddp-dev-bronze-new',
    'abfss://bronze@agentstge.dfs.core.windows.net/'
)

# Alternative: If you want to continue from where the previous migration left off
# You can run this function to complete remaining items
def complete_remaining_migration(old_catalog, new_catalog):
    """Complete migration for remaining schemas/objects"""
    print("Completing remaining migration tasks...")
    
    # Get list of schemas in both catalogs
    spark.sql(f"USE CATALOG `{old_catalog}`")
    old_schemas = set([s.databaseName for s in spark.sql("SHOW SCHEMAS").collect()])
    
    spark.sql(f"USE CATALOG `{new_catalog}`")
    new_schemas = set([s.databaseName for s in spark.sql("SHOW SCHEMAS").collect()])
    
    # Find schemas that need migration
    remaining_schemas = old_schemas - new_schemas
    
    if remaining_schemas:
        print(f"Found {len(remaining_schemas)} schemas to migrate: {remaining_schemas}")
        # Run migration for remaining schemas
        for schema in remaining_schemas:
            if schema not in ('information_schema', '__databricks_internal'):
                print(f"\nMigrating remaining schema: {schema}")
                # Run targeted migration for this schema
    else:
        print("All schemas already migrated")
    
    # For each schema, check for missing objects
    for schema in new_schemas:
        if schema in ('information_schema', '__databricks_internal'):
            continue
            
        print(f"\nChecking schema: {schema}")
        
        # Compare object counts
        spark.sql(f"USE CATALOG `{old_catalog}`")
        spark.sql(f"USE SCHEMA `{schema}`")
        old_objects = spark.sql("SHOW TABLES").collect()
        
        spark.sql(f"USE CATALOG `{new_catalog}`")
        spark.sql(f"USE SCHEMA `{schema}`")
        new_objects = spark.sql("SHOW TABLES").collect()
        
        if len(old_objects) != len(new_objects):
            print(f"  Object count mismatch: old={len(old_objects)}, new={len(new_objects)}")
