# **Alembic - The Migration Environment**

## **The Structure of the Environment** (from docs)

```
yourproject/
    alembic/
        env.py
        README
        script.py.mako
        versions/
            3512b954651e_add_account.py
            2b1ae634e5cd_add_order_id.py
            3adcc9a56557_rename_username_field.py
```

- `alembic`: The home of the migration environment. A project that uses multiple databases my have more than one.

- `env.py`: A Python script that is run whenever the `alembic` migration tool is invoked. It contains instructions to configure and generate a SQLAlchemy engine procure a connection from that engine along with a transaction, and then invoke the migration engine, using the connection as a source of database connectivity.

- `script.py.mako`: This is a Mako template file which is used to generate new migration scripts. Whatever is here is used to generate new files within versions/. This is scriptable so that the structure of each migration file can be controlled, including standard imports to be within each, as well as changes to the structure of the upgrade() and downgrade() functions. For example, the multidb environment allows for multiple functions to be generated using a naming scheme upgrade_engine1(), upgrade_engine2().

- `versions/`: This directory holds the individual version scripts. Users of other migration tools may notice that the files here don’t use ascending integers, and instead use a partial GUID approach. In Alembic, the ordering of version scripts is relative to directives within the scripts themselves, and it is theoretically possible to “splice” version files in between others, allowing migration sequences from different branches to be merged, albeit carefully by hand.

## **The `.ini` File**

`alembic.ini`:
- This is a file that the `alembic` script looks for when invoked.