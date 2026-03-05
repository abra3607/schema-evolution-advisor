from pathlib import Path
from schema_evolution_advisor.parser import parse_migration, parse_directory, is_alembic_migration

FIXTURES = Path(__file__).parent / "fixtures"


def test_is_alembic_migration():
    assert is_alembic_migration(FIXTURES / "001_safe_migration.py")
    assert is_alembic_migration(FIXTURES / "002_cautious_migration.py")
    assert is_alembic_migration(FIXTURES / "003_dangerous_migration.py")


def test_is_not_alembic_migration(tmp_path):
    f = tmp_path / "not_migration.py"
    f.write_text("x = 1\n")
    assert not is_alembic_migration(f)


def test_parse_safe_migration():
    ops = parse_migration(FIXTURES / "001_safe_migration.py")
    upgrade_ops = [o for o in ops if o.function == "upgrade"]
    assert len(upgrade_ops) == 3
    assert upgrade_ops[0].op_type == "create_table"
    assert upgrade_ops[0].args[0] == "users"
    assert upgrade_ops[1].op_type == "add_column"
    assert upgrade_ops[1].args[0] == "users"
    assert upgrade_ops[2].op_type == "create_index"
    assert upgrade_ops[2].args[0] == "ix_users_email"


def test_parse_cautious_migration():
    ops = parse_migration(FIXTURES / "002_cautious_migration.py")
    upgrade_ops = [o for o in ops if o.function == "upgrade"]
    assert len(upgrade_ops) == 3
    assert upgrade_ops[0].op_type == "alter_column"
    assert "type_" in upgrade_ops[0].kwargs
    assert upgrade_ops[1].op_type == "drop_index"
    assert upgrade_ops[2].op_type == "add_column"


def test_parse_dangerous_migration():
    ops = parse_migration(FIXTURES / "003_dangerous_migration.py")
    upgrade_ops = [o for o in ops if o.function == "upgrade"]
    assert len(upgrade_ops) == 2
    assert upgrade_ops[0].op_type == "drop_column"
    assert upgrade_ops[1].op_type == "drop_table"
    assert upgrade_ops[1].args[0] == "legacy_sessions"


def test_parse_directory():
    ops = parse_directory(FIXTURES)
    assert len(ops) > 0
    op_types = {o.op_type for o in ops}
    assert "create_table" in op_types
    assert "drop_table" in op_types
    assert "alter_column" in op_types


def test_downgrade_ops_parsed():
    ops = parse_migration(FIXTURES / "001_safe_migration.py")
    downgrade_ops = [o for o in ops if o.function == "downgrade"]
    assert len(downgrade_ops) == 3
    assert downgrade_ops[0].op_type == "drop_index"
    assert downgrade_ops[1].op_type == "drop_column"
    assert downgrade_ops[2].op_type == "drop_table"
