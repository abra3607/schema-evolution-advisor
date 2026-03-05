from schema_evolution_advisor.parser import Operation
from schema_evolution_advisor.analyzer import analyze, has_dangerous, has_cautious_or_dangerous


def _op(op_type, args=None, kwargs=None):
    return Operation(
        op_type=op_type,
        args=args or [],
        kwargs=kwargs or {},
        function="upgrade",
        source_file="test.py",
    )


def test_add_column_nullable_is_safe():
    findings = analyze([_op("add_column", ["users", "bio"], {"nullable": "True"})])
    assert len(findings) == 1
    assert findings[0].risk_level == "safe"


def test_add_column_non_nullable_no_default_is_cautious():
    findings = analyze([_op("add_column", ["users", "age"], {"nullable": "False"})])
    assert findings[0].risk_level == "cautious"


def test_add_column_non_nullable_with_default_is_safe():
    findings = analyze([_op("add_column", ["users", "status"], {"nullable": "False", "server_default": "'active'"})])
    assert findings[0].risk_level == "safe"


def test_drop_column_is_dangerous():
    findings = analyze([_op("drop_column", ["users", "bio"])])
    assert findings[0].risk_level == "dangerous"


def test_drop_table_is_dangerous():
    findings = analyze([_op("drop_table", ["old_table"])])
    assert findings[0].risk_level == "dangerous"


def test_alter_column_type_change_is_cautious():
    findings = analyze([_op("alter_column", ["users", "name"], {"type_": "sa.Text()"})])
    assert findings[0].risk_level == "cautious"


def test_alter_column_make_non_nullable_is_cautious():
    findings = analyze([_op("alter_column", ["users", "name"], {"nullable": "False"})])
    assert findings[0].risk_level == "cautious"


def test_alter_column_metadata_is_safe():
    findings = analyze([_op("alter_column", ["users", "name"], {"comment": "full name"})])
    assert findings[0].risk_level == "safe"


def test_create_table_is_safe():
    findings = analyze([_op("create_table", ["new_table"])])
    assert findings[0].risk_level == "safe"


def test_create_index_is_safe():
    findings = analyze([_op("create_index", ["ix_email"])])
    assert findings[0].risk_level == "safe"


def test_drop_index_is_cautious():
    findings = analyze([_op("drop_index", ["ix_email"])])
    assert findings[0].risk_level == "cautious"


def test_rename_table_is_cautious():
    findings = analyze([_op("rename_table", ["old_name", "new_name"])])
    assert findings[0].risk_level == "cautious"


def test_has_dangerous():
    findings = analyze([
        _op("create_table", ["t"]),
        _op("drop_table", ["t2"]),
    ])
    assert has_dangerous(findings)


def test_has_cautious_or_dangerous():
    findings = analyze([
        _op("create_table", ["t"]),
        _op("drop_index", ["ix"]),
    ])
    assert has_cautious_or_dangerous(findings)
    assert not has_dangerous(findings)


def test_all_safe():
    findings = analyze([
        _op("create_table", ["t"]),
        _op("create_index", ["ix"]),
        _op("add_column", ["t", "col"]),
    ])
    assert not has_dangerous(findings)
    assert not has_cautious_or_dangerous(findings)
